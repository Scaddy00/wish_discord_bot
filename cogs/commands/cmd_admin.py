
# ----------------------------- Imported Libraries -----------------------------
# Standard library imports
import asyncio
from datetime import datetime, timedelta, timezone
from os import getenv

# Third-party library imports
import discord
from discord import app_commands
from discord.ext import commands

# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from config_manager import ConfigManager
from utils.printing import safe_send_message, create_embed, load_single_embed_text, create_embed_from_dict

class CmdAdmin(commands.GroupCog, name="admin"):
    """Admin commands for maintenance, logging, and utilities."""
    description: str = "Comandi amministrativi per gestione server e pulizia log."

    def __init__(self, bot: commands.Bot, log: Logger, config: ConfigManager) -> None:
        super().__init__()
        self.bot: commands.Bot = bot
        self.log: Logger = log
        self.config: ConfigManager = config
        
        # Dictionary containing all commands and their descriptions
        self.commands_info = {
            "clear": "Cancella tutti i messaggi in questo canale",
            "clear-user": "Cancella tutti i messaggi di un utente specifico in questo canale",
            "clear-channel": "Cancella tutti i messaggi nel canale indicato",
            "clear-channel-user": "Cancella tutti i messaggi di un utente specifico nel canale indicato",
            "clear-server-user": "Cancella tutti i messaggi di un utente in tutto il server",
            "update-welcome-db": "Aggiorna la tabella welcome del database",
            "database-cleanup": "Esegue manualmente la pulizia del database rimuovendo i record vecchi",
            "force-welcome": "Forza l'esecuzione manuale della task di benvenuto",
            "send-weekly-report": "Invia manualmente il report settimanale degli eventi Discord",
            "dm-welcome": "Invia un DM di benvenuto (scegli tra singolo utente o tutti i 'not_verified')"
        }
    
    # ============================= Help Command =============================
    @app_commands.command(name="help", description="Mostra l'elenco dei comandi admin disponibili")
    async def help(self, interaction: discord.Interaction) -> None:
        """
        Show an embed with all admin commands and their descriptions.
        """
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel) if self.config.communication_channel else None
        
        try:
            # Create embed with commands info
            embed = create_embed(
                title="🛠️ Comandi Admin",
                description="Elenco di tutti i comandi admin disponibili",
                color=self.bot.color,
                fields=[]
            )
            
            # Add each command to the embed
            for command_name, description in self.commands_info.items():
                embed.add_field(
                    name=f"`/admin {command_name}`",
                    value=description,
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await self.log.command('Visualizzato help comandi admin', 'admin', 'HELP')
            
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - HELP')
            await interaction.response.send_message(f"❌ {error_message}", ephemeral=True)
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - HELP')
            await interaction.response.send_message(f"❌ {error_message}", ephemeral=True)
            
        except Exception as e:
            error_message: str = f'Errore durante la visualizzazione dell\'help: {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - HELP')
            await interaction.response.send_message(f"❌ {error_message}", ephemeral=True)
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - ADMIN - HELP', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - ADMIN - HELP')

    # ============================= Helper Methods =============================
    async def delete_messages(self, channel: discord.abc.GuildChannel) -> int:
        """
        Delete all messages in a channel using an iterative approach.
        
        Returns the total number of deleted messages.
        """
        total_deleted = 0
        
        while True:
            # Get a batch of messages (up to 100)
            messages = []
            async for msg in channel.history(limit=100, oldest_first=False):
                messages.append(msg)
            
            # If no messages found, we're done
            if not messages:
                break
            
            # Divide messages by age
            recent = []
            old = []
            for msg in messages:
                age = datetime.now(timezone.utc) - msg.created_at
                if age < timedelta(days=14):
                    recent.append(msg)
                else:
                    old.append(msg)
            
            # Delete recent messages in batch
            if recent:
                try:
                    deleted = await channel.purge(check=lambda m: m.id in [x.id for x in recent])
                    total_deleted += len(deleted)
                except discord.HTTPException:
                    pass
            
            # Delete old messages one by one
            for msg in old:
                try:
                    await msg.delete()
                    total_deleted += 1
                    await asyncio.sleep(1)  # Rate limiting
                except discord.HTTPException:
                    pass
            
            # If we got less than 100 messages, we've reached the end
            if len(messages) < 100:
                break
        
        return total_deleted

    async def delete_user_messages(self, channel: discord.abc.GuildChannel, user: discord.Member) -> int:
        """
        Delete all messages from a specific user in a channel using an iterative approach.
        
        Returns the total number of deleted messages.
        """
        total_deleted = 0
        
        while True:
            # Get a batch of messages (up to 100)
            messages = []
            async for msg in channel.history(limit=100, oldest_first=False):
                messages.append(msg)
            
            # If no messages found, we're done
            if not messages:
                break
            
            # Filter messages by user
            user_messages = [msg for msg in messages if msg.author.id == user.id]
            
            # Divide messages by age
            recent = []
            old = []
            for msg in user_messages:
                age = datetime.now(timezone.utc) - msg.created_at
                if age < timedelta(days=14):
                    recent.append(msg)
                else:
                    old.append(msg)
            
            # Delete recent messages in batch
            if recent:
                try:
                    deleted = await channel.purge(check=lambda m: m.id in [x.id for x in recent])
                    total_deleted += len(deleted)
                except discord.HTTPException:
                    pass
            
            # Delete old messages one by one
            for msg in old:
                try:
                    await msg.delete()
                    total_deleted += 1
                    await asyncio.sleep(1)  # Rate limiting
                except discord.HTTPException:
                    pass
            
            # If we got less than 100 messages, we've reached the end
            if len(messages) < 100:
                break
        
        return total_deleted
        
    # ============================= Channel Management =============================
    @app_commands.command(name="clear", description="Cancella tutti i messaggi in questo canale")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.cooldown(1, 10)
    async def clear(self, interaction: discord.Interaction) -> None:
        """
        Delete all messages in the current channel.
        """
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel)
        channel = interaction.channel
        
        await self.log.command(f'Pulizia del seguente canale: {channel} ({channel.id})', 'admin', 'CLEAR')
        await interaction.response.send_message('Avvio la pulizia di questo canale', ephemeral=True)
        
        try:
            deleted: int = await self.delete_messages(channel)
            await interaction.channel.send(f'Sono stati cancellati **{deleted} messaggi**', delete_after=30)
            await self.log.command(f'Cancellati {deleted} messaggi dal seguente canale: {channel} ({channel.id})', 'admin', 'CLEAR')
            
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - CLEAR')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - CLEAR')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except Exception as e:
            error_message: str = f'Errore durante l\'eliminazione dei messaggi nel seguente canale: {channel} ({channel.id}): {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - CLEAR')
            await safe_send_message(interaction, f"❌ {error_message}")
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - ADMIN - CLEAR', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - ADMIN - CLEAR')

    @app_commands.command(name="clear-user", description="Cancella tutti i messaggi di un utente specifico in questo canale")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.cooldown(1, 10)
    async def clear_user(self, interaction: discord.Interaction, user: discord.Member) -> None:
        """
        Delete all messages from a specific user in the current channel.
        """
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel)
        channel = interaction.channel
        
        await self.log.command(f'Pulizia messaggi dell\'utente {user} ({user.id}) nel canale: {channel} ({channel.id})', 'admin', 'CLEAR-USER')
        await interaction.response.send_message(f'Avvio la pulizia dei messaggi di {user.mention} in questo canale', ephemeral=True)
        
        try:
            deleted: int = await self.delete_user_messages(channel, user)
            await interaction.channel.send(f'Sono stati cancellati **{deleted} messaggi** di {user.mention}', delete_after=30)
            await self.log.command(f'Cancellati {deleted} messaggi dell\'utente {user} ({user.id}) dal canale: {channel} ({channel.id})', 'admin', 'CLEAR-USER')
            
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - CLEAR-USER')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - CLEAR-USER')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except Exception as e:
            error_message: str = f'Errore durante l\'eliminazione dei messaggi dell\'utente {user} ({user.id}) nel canale: {channel} ({channel.id}): {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - CLEAR-USER')
            await safe_send_message(interaction, f"❌ {error_message}")
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - ADMIN - CLEAR-USER', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - ADMIN - CLEAR-USER')

    @app_commands.command(name="clear-channel", description="Cancella tutti i messaggi nel canale indicato")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.cooldown(1, 10)
    async def clear_channel(self, interaction: discord.Interaction, channel: discord.abc.GuildChannel) -> None:
        """
        Delete all messages in the specified channel.
        """
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel)
        
        await self.log.command(f'Pulizia del seguente canale: {channel} ({channel.id})', 'admin', 'CLEAR-CHANNEL')
        await interaction.response.send_message('Avvio la pulizia di questo canale', ephemeral=True)
        
        # Check if the channel supports message operations
        if not isinstance(channel, (discord.TextChannel, discord.ForumChannel, discord.StageChannel, discord.VoiceChannel)):
            await safe_send_message(interaction, "❌ Questo tipo di canale non supporta la cancellazione di messaggi.")
            return
        
        try:
            deleted: int = await self.delete_messages(channel)
            await interaction.delete_original_response()
            await interaction.channel.send(f'Sono stati cancellati **{deleted} messaggi**', delete_after=30)
            await self.log.command(f'Cancellati {deleted} messaggi dal seguente canale: {channel} ({channel.id})', 'admin', 'CLEAR-CHANNEL')
            
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - CLEAR-CHANNEL')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - CLEAR-CHANNEL')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except Exception as e:
            error_message: str = f'Errore durante l\'eliminazione dei messaggi nel seguente canale: {channel} ({channel.id}): {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - CLEAR-CHANNEL')
            await safe_send_message(interaction, f"❌ {error_message}")
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - ADMIN - CLEAR-CHANNEL', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - ADMIN - CLEAR-CHANNEL')

    @app_commands.command(name="clear-channel-user", description="Cancella tutti i messaggi di un utente specifico nel canale indicato")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.cooldown(1, 10)
    async def clear_channel_user(self, interaction: discord.Interaction, channel: discord.abc.GuildChannel, user: discord.Member) -> None:
        """
        Delete all messages from a specific user in the specified channel.
        """
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel)
        
        await self.log.command(f'Pulizia messaggi dell\'utente {user} ({user.id}) nel canale: {channel} ({channel.id})', 'admin', 'CLEAR-CHANNEL-USER')
        await interaction.response.send_message(f'Avvio la pulizia dei messaggi di {user.mention} nel canale {channel.mention}', ephemeral=True)
        
        # Check if the channel supports message operations
        if not isinstance(channel, (discord.TextChannel, discord.ForumChannel, discord.StageChannel, discord.VoiceChannel)):
            await safe_send_message(interaction, "❌ Questo tipo di canale non supporta la cancellazione di messaggi.")
            return
        
        try:
            deleted: int = await self.delete_user_messages(channel, user)
            await interaction.delete_original_response()
            await interaction.channel.send(f'Sono stati cancellati **{deleted} messaggi** di {user.mention} nel canale {channel.mention}', delete_after=30)
            await self.log.command(f'Cancellati {deleted} messaggi dell\'utente {user} ({user.id}) dal canale: {channel} ({channel.id})', 'admin', 'CLEAR-CHANNEL-USER')
            
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - CLEAR-CHANNEL-USER')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - CLEAR-CHANNEL-USER')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except Exception as e:
            error_message: str = f'Errore durante l\'eliminazione dei messaggi dell\'utente {user} ({user.id}) nel canale: {channel} ({channel.id}): {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - CLEAR-CHANNEL-USER')
            await safe_send_message(interaction, f"❌ {error_message}")
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - ADMIN - CLEAR-CHANNEL-USER', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - ADMIN - CLEAR-CHANNEL-USER')

    @app_commands.command(name="clear-server-user", description="Cancella tutti i messaggi di un utente in tutto il server")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.cooldown(1, 30)
    async def clear_server_user(self, interaction: discord.Interaction, user: discord.Member) -> None:
        """
        Delete all messages from a specific user across the entire server.
        """
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel)
        
        await self.log.command(f'Pulizia messaggi dell\'utente {user} ({user.id}) in tutto il server', 'admin', 'CLEAR-SERVER-USER')
        await interaction.response.send_message(f'Avvio la pulizia di tutti i messaggi di {user.mention} in tutto il server. Questa operazione potrebbe richiedere del tempo.', ephemeral=True)
        
        try:
            total_deleted = 0
            channels_processed = 0
            
            # Get all text channels, forum channels, stage channels, and voice channels
            all_channels = [ch for ch in guild.channels if isinstance(ch, (discord.TextChannel, discord.ForumChannel, discord.StageChannel, discord.VoiceChannel))]
            
            for channel in all_channels:
                try:
                    # Check if bot has permissions to manage messages in this channel
                    if not channel.permissions_for(guild.me).manage_messages:
                        continue
                    
                    # Check if bot has permissions to read message history
                    if not channel.permissions_for(guild.me).read_message_history:
                        continue
                    
                    deleted = await self.delete_user_messages(channel, user)
                    if deleted > 0:
                        total_deleted += deleted
                        channels_processed += 1
                        
                except discord.Forbidden:
                    # Skip channels where bot doesn't have permissions
                    continue
                except Exception as e:
                    # Log error but continue with other channels
                    await self.log.error(f'Errore durante la pulizia del canale {channel.name} ({channel.id}): {e}', 'COMMAND - ADMIN - CLEAR-SERVER-USER')
                    continue
            
            # Send final report
            await interaction.delete_original_response()
            await interaction.channel.send(
                f'✅ **Pulizia completata!**\n'
                f'**Utente:** {user.mention}\n'
                f'**Messaggi cancellati:** {total_deleted}\n'
                f'**Canali processati:** {channels_processed}\n'
                f'**Canali totali:** {len(all_channels)}',
                delete_after=60
            )
            
            await self.log.command(f'Cancellati {total_deleted} messaggi dell\'utente {user} ({user.id}) da {channels_processed} canali su {len(all_channels)} totali', 'admin', 'CLEAR-SERVER-USER')
            
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - CLEAR-SERVER-USER')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - CLEAR-SERVER-USER')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except Exception as e:
            error_message: str = f'Errore durante l\'eliminazione dei messaggi dell\'utente {user} ({user.id}) in tutto il server: {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - CLEAR-SERVER-USER')
            await safe_send_message(interaction, f"❌ {error_message}")
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - ADMIN - CLEAR-SERVER-USER', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - ADMIN - CLEAR-SERVER-USER')

    # ============================= Database Management =============================
    @app_commands.command(name="update-welcome-db", description="Aggiorna la tabella welcome del database")
    async def update_welcome_db(self, interaction: discord.Interaction) -> None:
        """Aggiorna la tabella welcome del database con tutti i membri del server"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel)
        await self.log.command('Aggiornamento del database delle benvenute', 'admin', 'UPDATE-WELCOME-DB')
        await interaction.response.send_message('Avvio l\'aggiornamento del database delle benvenute', ephemeral=True)

        try:
            members: list[discord.Member] = guild.members
            # Get all existing welcome records
            existing_welcomes = self.log.db.get_welcome()
            existing_user_ids = {entry['user_id'] for entry in existing_welcomes}

            added = 0
            for member in members:
                if member.bot:
                    continue  # Skip bots
                if member.id not in existing_user_ids:
                    # Insert into db (use current timestamp and full username)
                    timestamp = datetime.now(timezone.utc).isoformat()
                    self.log.db.insert_welcome(timestamp, str(member.id), str(member))
                    added += 1

            await safe_send_message(interaction, f'Sono stati aggiunti **{added} utenti** alla tabella delle benvenute.')
            await self.log.command(f'Aggiunti {added} utenti alla tabella welcome.', 'admin', 'UPDATE-WELCOME-DB')
            
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - UPDATE-WELCOME-DB')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - UPDATE-WELCOME-DB')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except Exception as e:
            error_message: str = f'Errore durante l\'aggiornamento del database delle benvenute: {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - UPDATE-WELCOME-DB')
            await safe_send_message(interaction, f"❌ {error_message}")
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - ADMIN - UPDATE-WELCOME-DB', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - ADMIN - UPDATE-WELCOME-DB')

    @app_commands.command(name="database-cleanup", description="Esegue manualmente la pulizia del database rimuovendo i record vecchi")
    async def database_cleanup(self, interaction: discord.Interaction) -> None:
        """Esegue manualmente la pulizia del database rimuovendo i record obsoleti"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel)
        await self.log.command('Esecuzione manuale della pulizia del database', 'admin', 'DATABASE-CLEANUP')
        await interaction.response.send_message('Avvio la pulizia manuale del database', ephemeral=True)

        try:
            # Get the DatabaseCleanup cog from the bot
            database_cleanup_cog = self.bot.get_cog('DatabaseCleanup')

            # Execute the database cleanup task manually
            await database_cleanup_cog.database_cleanup()
            
            await safe_send_message(interaction, 'Pulizia del database eseguita con successo.')
            await self.log.command('Pulizia del database eseguita manualmente con successo', 'admin', 'DATABASE-CLEANUP')
            
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - DATABASE-CLEANUP')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - DATABASE-CLEANUP')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except Exception as e:
            error_message: str = f'Errore durante l\'esecuzione manuale della pulizia del database: {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - DATABASE-CLEANUP')
            await safe_send_message(interaction, f"❌ {error_message}")
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - ADMIN - DATABASE-CLEANUP', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - ADMIN - DATABASE-CLEANUP')

    # ============================= Task Management =============================
    @app_commands.command(name="force-welcome", description="Forza l'esecuzione manuale della task di benvenuto")
    async def force_welcome(self, interaction: discord.Interaction) -> None:
        """Forza l'esecuzione manuale della task di benvenuto per tutti i nuovi membri"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel)
        await self.log.command('Esecuzione forzata della task di benvenuto', 'admin', 'FORCE-WELCOME')
        await interaction.response.send_message('Avvio l\'esecuzione forzata della task di benvenuto', ephemeral=True)

        try:
            # Get the Welcome cog from the bot
            welcome_cog = self.bot.get_cog('Welcome')

            # Execute the welcome task manually
            await welcome_cog.execute_welcome_task()
            
            await safe_send_message(interaction, 'Task di benvenuto eseguita con successo.')
            await self.log.command('Task di benvenuto eseguita manualmente con successo', 'admin', 'FORCE-WELCOME')
            
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - FORCE-WELCOME')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - FORCE-WELCOME')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except Exception as e:
            error_message: str = f'Errore durante l\'esecuzione forzata della task di benvenuto: {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - FORCE-WELCOME')
            await safe_send_message(interaction, f"❌ {error_message}")
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - ADMIN - FORCE-WELCOME', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - ADMIN - FORCE-WELCOME')

    @app_commands.command(name="send-weekly-report", description="Invia manualmente il report settimanale degli eventi Discord")
    async def send_weekly_report(self, interaction: discord.Interaction) -> None:
        """Invia manualmente il report settimanale degli eventi Discord"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel)
        await self.log.command('Invio manuale del report settimanale', 'admin', 'SEND-WEEKLY-REPORT')
        await interaction.response.send_message('Avvio l\'invio manuale del report settimanale', ephemeral=True)

        try:
            # Get the WeeklyReport cog from the bot
            weekly_report_cog = self.bot.get_cog('WeeklyReport')

            # Execute the weekly report task manually
            await weekly_report_cog.weekly_report()
            
            await safe_send_message(interaction, 'Report settimanale inviato con successo.')
            await self.log.command('Report settimanale inviato manualmente con successo', 'admin', 'SEND-WEEKLY-REPORT')
            
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - SEND-WEEKLY-REPORT')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - SEND-WEEKLY-REPORT')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except Exception as e:
            error_message: str = f'Errore durante l\'invio manuale del report settimanale: {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - SEND-WEEKLY-REPORT')
            await safe_send_message(interaction, f"❌ {error_message}")
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - ADMIN - SEND-WEEKLY-REPORT', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - ADMIN - SEND-WEEKLY-REPORT')
    
    # ============================= Send Messages =============================
    @app_commands.command(name="dm-welcome", description="Invia un DM di benvenuto: scegli tra singolo utente o tutti i 'not_verified'")
    async def dm_welcome(self, interaction: discord.Interaction) -> None:
        """Mostra una view per scegliere la modalità (utente singolo o bulk) e invia i DM"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel)
        await self.log.command('Avvio selezione modalità per invio DM di benvenuto', 'admin', 'DM-WELCOME')
        await interaction.response.defer(ephemeral=True)

        # Import here to avoid circular imports at module load
        from cogs.modals.dm_welcome_mode_view import DmWelcomeModeView
        from cogs.modals.user_view import UserView

        # Ask for mode
        mode_view = DmWelcomeModeView(author=interaction.user)
        await interaction.followup.send("Scegli la modalità di invio DM di benvenuto:", view=mode_view, ephemeral=True)
        await mode_view.wait()

        if not mode_view.confirmed or not mode_view.selected_mode:
            await safe_send_message(interaction, "Selezione modalità non confermata.")
            return

        # Handle single user mode
        if mode_view.selected_mode == "user":
            user_view = UserView(author=interaction.user, min_values=1, max_values=1)
            await interaction.followup.send("Seleziona l'utente a cui inviare il DM di benvenuto:", view=user_view, ephemeral=True)
            await user_view.wait()

            if not user_view.confirmed or user_view.selected_user_id is None:
                await safe_send_message(interaction, "Selezione utente non confermata o nessun utente selezionato.")
                return

            user = guild.get_member(user_view.selected_user_id) or await self.bot.fetch_user(user_view.selected_user_id)
            if user is None:
                await safe_send_message(interaction, "❌ Utente non trovato.")
                return

            try:
                message_content: dict = await load_single_embed_text(guild, 'welcome-user', self.config)
                message: discord.Embed = create_embed_from_dict(message_content)
                await user.send(embed=message)
                mention = user.mention if isinstance(user, discord.Member) else f"<@{user.id}>"
                name = getattr(user, 'name', str(user))
                await safe_send_message(interaction, f'DM di benvenuto inviato correttamente a {mention}.')
                await self.log.command(f'DM di benvenuto inviato a {name} ({user.id})', 'admin', 'DM-WELCOME')

            except discord.Forbidden:
                uname = getattr(user, 'name', str(user))
                error_message: str = ("Errore durante l'invio del DM di benvenuto. "
                                       f"\nUtente: {uname} ({user.id}) \nL'utente ha disabilitato i messaggi privati.")
                await self.log.error(error_message, 'COMMAND - ADMIN - DM-WELCOME')
                await safe_send_message(interaction, f"❌ {error_message}")

            except discord.NotFound as e:
                error_message = f'Risorsa non trovata: {e}'
                await self.log.error(error_message, 'COMMAND - ADMIN - DM-WELCOME')
                await safe_send_message(interaction, f"❌ {error_message}")

            except Exception as e:
                uname = getattr(user, 'name', str(user)) if 'user' in locals() and user else 'Sconosciuto'
                uid = getattr(user, 'id', 'N/D') if 'user' in locals() and user else 'N/D'
                error_message: str = ("Errore durante l'invio manuale del DM di benvenuto al membro selezionato: "
                                       f"{uname} ({uid}): {e}")
                await self.log.error(error_message, 'COMMAND - ADMIN - DM-WELCOME')
                await safe_send_message(interaction, f"❌ {error_message}")

                if communication_channel:
                    try:
                        await communication_channel.send(self.log.error_message(command='COMMAND - ADMIN - DM-WELCOME', message=error_message))
                    except Exception as comm_error:
                        await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - ADMIN - DM-WELCOME')

            return

        # Handle bulk mode
        if mode_view.selected_mode == "bulk":
            await self.log.command('Invio manuale del DM di benvenuto a tutti i membri che hanno il ruolo "not_verified"', 'admin', 'DM-WELCOME-BULK')
            try:
                not_verified_role_id = self.config.load_admin('roles', 'not_verified')
                if not_verified_role_id and not_verified_role_id != '':
                    not_verified_role = guild.get_role(int(not_verified_role_id))
                    if not_verified_role:
                        members = [member for member in guild.members if not_verified_role in member.roles]
                        for member in members:
                            try:
                                message_content: dict = await load_single_embed_text(guild, 'welcome-user', self.config)
                                message: discord.Embed = create_embed_from_dict(message_content)
                                await member.send(embed=message)
                                await self.log.command(f'DM di benvenuto inviato a {member.name} ({member.id})', 'admin', 'DM-WELCOME-BULK')
                            except discord.Forbidden:
                                error_message: str = ("Errore durante l'invio del DM di benvenuto. "
                                                      f"\nUtente: {member.name} ({member.id}) \nL'utente ha disabilitato i messaggi privati.")
                                await self.log.error(error_message, 'COMMAND - ADMIN - DM-WELCOME-BULK')
                            except Exception as e:
                                error_message: str = ("Errore durante l'invio del DM di benvenuto. "
                                                      f"\nUtente: {member.name} ({member.id}) \n{e}")
                                await self.log.error(error_message, 'COMMAND - ADMIN - DM-WELCOME-BULK')

                await safe_send_message(interaction, 'DM di benvenuto inviati con successo.')
                await self.log.command('DM di benvenuto inviati manualmente con successo', 'admin', 'DM-WELCOME-BULK')

            except discord.NotFound as e:
                error_message = f'Risorsa non trovata: {e}'
                await self.log.error(error_message, 'COMMAND - ADMIN - DM-WELCOME-BULK')
                await safe_send_message(interaction, f"❌ {error_message}")

            except discord.Forbidden as e:
                error_message = f'Permessi insufficienti: {e}'
                await self.log.error(error_message, 'COMMAND - ADMIN - DM-WELCOME-BULK')
                await safe_send_message(interaction, f"❌ {error_message}")

            except Exception as e:
                error_message: str = ("Errore durante l'invio manuale del DM di benvenuto a tutti i membri che hanno il ruolo \"not_verified\": "
                                       f"{e}")
                await self.log.error(error_message, 'COMMAND - ADMIN - DM-WELCOME-BULK')
                await safe_send_message(interaction, f"❌ {error_message}")

                if communication_channel:
                    try:
                        await communication_channel.send(self.log.error_message(command='COMMAND - ADMIN - DM-WELCOME-BULK', message=error_message))
                    except Exception as comm_error:
                        await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - ADMIN - DM-WELCOME-BULK')
            return

        try:
            # Get welcome message content
            message_content: dict = await load_single_embed_text(guild, 'welcome-user', self.config)
            # Create embed
            message: discord.Embed = create_embed_from_dict(message_content)
            # Send DM to the specified user
            await user.send(embed=message)
            # Success response and log
            mention = user.mention if isinstance(user, discord.Member) else f"<@{user.id}>"
            name = getattr(user, 'name', str(user))
            await safe_send_message(interaction, f'DM di benvenuto inviato correttamente a {mention}.')
            await self.log.command(f'DM di benvenuto inviato a {name} ({user.id})', 'admin', 'DM-WELCOME')

        except discord.Forbidden:
            uname = getattr(user, 'name', str(user))
            error_message: str = ("Errore durante l'invio del DM di benvenuto. "
                                   f"\nUtente: {uname} ({user.id}) \nL'utente ha disabilitato i messaggi privati.")
            await self.log.error(error_message, 'COMMAND - ADMIN - DM-WELCOME')
            await safe_send_message(interaction, f"❌ {error_message}")

        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - DM-WELCOME')
            await safe_send_message(interaction, f"❌ {error_message}")

        except Exception as e:
            uname = getattr(user, 'name', str(user)) if 'user' in locals() and user else 'Sconosciuto'
            uid = getattr(user, 'id', 'N/D') if 'user' in locals() and user else 'N/D'
            error_message: str = ("Errore durante l'invio manuale del DM di benvenuto al membro selezionato: "
                                   f"{uname} ({uid}): {e}")
            await self.log.error(error_message, 'COMMAND - ADMIN - DM-WELCOME')
            await safe_send_message(interaction, f"❌ {error_message}")

            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - ADMIN - DM-WELCOME', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - ADMIN - DM-WELCOME')