
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

class CmdAdmin(commands.GroupCog, name="admin"):
    def __init__(self, bot: commands.bot, log: Logger, config: ConfigManager):
        super().__init__()
        self.bot = bot
        self.log = log
        self.config = config
    
    async def delete_messages(self, channel: discord.TextChannel) -> int:
        # Get the list of messages in channel
        messages: list[discord.Message] = []
        async for msg in channel.history(limit=100, oldest_first=False):
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
        
    
    @app_commands.command(name="clear", description="Cancella tutti i messaggi in questo canale")
    async def clear(self, interaction: discord.Interaction) -> None:
        # Get the guild from interaction
        guild: discord.Guild = interaction.guild
        # Load communication channel
        communication_channel = guild.get_channel(self.config.communication_channel)
        # Get the channel
        channel = interaction.channel
        
        # INFO Log the start of the clear
        await self.log.command(f'Pulizia del seguente canale: {channel} ({channel.id})', 'admin', 'CLEAR')
        
        await interaction.response.send_message('Avvio la pulizia di questo canale', ephemeral=True)
        
        try:
            # Delete the messages and get the number of messages deleted
            deleted: int = await self.delete_messages(channel)
            # Respond with success and the number of messages deleted
            await interaction.channel.send(f'Sono stati cancellati **{deleted} messaggi**', delete_after=30)
            # INFO Log the success and the number of messages deleted
            await self.log.command(f'Cancellati {deleted} messaggi dal seguente canale: {channel} ({channel.id})', 'admin', 'CLEAR')
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante l\'eliminazione dei messaggi nel seguente canale: {channel} ({channel.id}).\n{e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - CLEAR')
            await communication_channel.send(self.log.error_message(command='COMMAND - ADMIN - CLEAR', message=error_message))
    
    @app_commands.command(name="clear-channel", description="Cancella tutti i messaggi nel canale indicato")
    async def clear_channel(self, interaction: discord.Interaction, channel: discord.TextChannel) -> None:
        # Get the guild from interaction
        guild: discord.Guild = interaction.guild
        # Load communication channel
        communication_channel = guild.get_channel(self.config.communication_channel)
        
        # INFO Log the start of the clear
        await self.log.command(f'Pulizia del seguente canale: {channel} ({channel.id})', 'admin', 'CLEAR-CHANNEL')
        
        await interaction.response.send_message('Avvio la pulizia di questo canale', ephemeral=True)
        
        try:
            # Delete the messages and get the number of messages deleted
            deleted: int = await self.delete_messages(channel)
            # Delete the original response to the command
            await interaction.delete_original_response()
            # Respond with success and the number of messages deleted
            await interaction.channel.send(f'Sono stati cancellati **{deleted} messaggi**', delete_after=30)
            # INFO Log the success and the number of messages deleted
            await self.log.command(f'Cancellati {deleted} messaggi dal seguente canale: {channel} ({channel.id})', 'admin', 'CLEAR-CHANNEL')
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante l\'eliminazione dei messaggi nel seguente canale: {channel} ({channel.id}).\n{e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - CLEAR-CHANNEL')
            await communication_channel.send(self.log.error_message(command='COMMAND - ADMIN - CLEAR-CHANNEL', message=error_message))

    @app_commands.command(name="update-welcome-db", description="Aggiorna la tabella welcome del database")
    async def update_welcome_db(self, interaction: discord.Interaction) -> None:
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

            await interaction.followup.send(f'Sono stati aggiunti **{added} utenti** alla tabella delle benvenute.', ephemeral=True)
            await self.log.command(f'Aggiunti {added} utenti alla tabella welcome.', 'admin', 'UPDATE-WELCOME-DB')
        except Exception as e:
            error_message: str = f'Errore durante l\'aggiornamento del database delle benvenute.\n{e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - UPDATE-WELCOME-DB')
            await communication_channel.send(self.log.error_message(command='COMMAND - ADMIN - UPDATE-WELCOME-DB', message=error_message))

    @app_commands.command(name="force-welcome", description="Forza l'esecuzione manuale della task di benvenuto")
    async def force_welcome(self, interaction: discord.Interaction) -> None:
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel)
        await self.log.command('Esecuzione forzata della task di benvenuto', 'admin', 'FORCE-WELCOME')
        await interaction.response.send_message('Avvio l\'esecuzione forzata della task di benvenuto', ephemeral=True)

        try:
            # Debug: List all available cogs
            available_cogs = [cog_name for cog_name in self.bot.cogs.keys()]
            await interaction.followup.send(f'Cog disponibili: {available_cogs}', ephemeral=True)
            
            # Get the Welcome cog from the bot
            welcome_cog = self.bot.get_cog('Welcome')
            if not welcome_cog:
                await interaction.followup.send(f'Errore: Cog Welcome non trovato. Cog disponibili: {available_cogs}', ephemeral=True)
                await self.log.error(f'Welcome cog non trovato. Cog disponibili: {available_cogs}', 'COMMAND - ADMIN - FORCE-WELCOME')
                return

            # Debug: Check if execute_welcome_task method exists
            if not hasattr(welcome_cog, 'execute_welcome_task'):
                await interaction.followup.send('Errore: Metodo execute_welcome_task non trovato nel cog.', ephemeral=True)
                await self.log.error('Metodo execute_welcome_task non trovato nel cog Welcome', 'COMMAND - ADMIN - FORCE-WELCOME')
                return
            
            # Execute the welcome task manually
            await welcome_cog.execute_welcome_task()
            
            await interaction.followup.send('Task di benvenuto eseguita con successo.', ephemeral=True)
            await self.log.command('Task di benvenuto eseguita manualmente con successo', 'admin', 'FORCE-WELCOME')
        except Exception as e:
            error_message: str = f'Errore durante l\'esecuzione forzata della task di benvenuto.\n{e}'
            await self.log.error(error_message, 'COMMAND - ADMIN - FORCE-WELCOME')
            await communication_channel.send(self.log.error_message(command='COMMAND - ADMIN - FORCE-WELCOME', message=error_message))
            await interaction.followup.send('Errore durante l\'esecuzione della task di benvenuto.', ephemeral=True)