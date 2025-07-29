
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from discord import app_commands
from os import getenv
from datetime import datetime, timedelta, timezone
import asyncio
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from config_manager import ConfigManager
from utils.printing import safe_send_message

class CmdAdmin(commands.GroupCog, name="admin"):
    def __init__(self, bot: commands.bot, log: Logger, config: ConfigManager):
        super().__init__()
        self.bot = bot
        self.log = log
        self.config = config
    
    # ============================= Helper Methods =============================
    async def delete_messages(self, channel) -> int:
        # Get the list of messages in channel
        messages: list[discord.Message] = []
        async for msg in channel.history(limit=None, oldest_first=False):
            messages.append(msg)
        
        # Divide old messages from recent
        recent: list[discord.Message] = []
        old: list[discord.Message] = []
        for msg in messages:
            # Check if message was sent more than 14th days ago
            age: timedelta = datetime.now(timezone.utc) - msg.created_at
            if age < timedelta(days=14):
                recent.append(msg)
            else:
                old.append(msg)
        
        # Delete recent messages
        recent_deleted = await channel.purge(check=lambda m: m.id in [x.id for x in recent])
        
        # Delete old messages
        old_deleted: int = 0
        for msg in old:
            try:
                await msg.delete()
                old_deleted += 1
                await asyncio.sleep(1)
            except discord.HTTPException:
                pass
        
        # Return the number of messages deleted
        return len(recent_deleted) + old_deleted

    async def delete_user_messages(self, channel, user: discord.Member) -> int:
        # Get the list of messages in channel
        messages: list[discord.Message] = []
        async for msg in channel.history(limit=None, oldest_first=False):
            messages.append(msg)
        
        # Filter messages by user
        user_messages = [msg for msg in messages if msg.author.id == user.id]
        
        # Divide old messages from recent
        recent: list[discord.Message] = []
        old: list[discord.Message] = []
        for msg in user_messages:
            # Check if message was sent more than 14th days ago
            age: timedelta = datetime.now(timezone.utc) - msg.created_at
            if age < timedelta(days=14):
                recent.append(msg)
            else:
                old.append(msg)
        
        # Delete recent messages
        recent_deleted = await channel.purge(check=lambda m: m.id in [x.id for x in recent])
        
        # Delete old messages
        old_deleted: int = 0
        for msg in old:
            try:
                await msg.delete()
                old_deleted += 1
                await asyncio.sleep(1)
            except discord.HTTPException:
                pass
        
        # Return the number of messages deleted
        return len(recent_deleted) + old_deleted
        
    # ============================= Channel Management =============================
    @app_commands.command(name="clear", description="Cancella tutti i messaggi in questo canale")
    async def clear(self, interaction: discord.Interaction) -> None:
        """Cancella tutti i messaggi nel canale corrente"""
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
    async def clear_user(self, interaction: discord.Interaction, user: discord.Member) -> None:
        """Cancella tutti i messaggi di un utente specifico nel canale corrente"""
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
    async def clear_channel(self, interaction: discord.Interaction, channel: discord.abc.GuildChannel) -> None:
        """Cancella tutti i messaggi nel canale specificato"""
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
    async def clear_channel_user(self, interaction: discord.Interaction, channel: discord.abc.GuildChannel, user: discord.Member) -> None:
        """Cancella tutti i messaggi di un utente specifico nel canale specificato"""
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
    async def clear_server_user(self, interaction: discord.Interaction, user: discord.Member) -> None:
        """Cancella tutti i messaggi di un utente specifico in tutti i canali del server"""
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