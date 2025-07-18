
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

