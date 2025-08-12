
# ----------------------------- Imported Libraries -----------------------------
# Third-party library imports
import discord
from discord.ext import commands

# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from config_manager import ConfigManager

class MessageEvents(commands.Cog):
    """
    Cog that listens to message events and logs messages.
    
    Applies filtering based on the message logging configuration.
    """

    def __init__(self, bot: commands.Bot, log: Logger, config: ConfigManager) -> None:
        super().__init__()
        self.bot: commands.Bot = bot
        self.log: Logger = log
        self.config: ConfigManager = config
    
    # ============================= ON_MESSAGE =============================
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """
        Handle every message and log it if configured.
        
        Skips bot messages and respects configured logging channels.
        """
        guild: discord.Guild = message.guild
        communication_channel = None
        if guild is not None:
            communication_channel = guild.get_channel(self.config.communication_channel)
        
        try:
            if message.author.bot:
                return
            
            # Check if message logging is enabled
            if self.config.load_message_logging()['enabled']:
                # Get message logging channels
                message_logging_channels: list[int] = self.config.load_message_logging_channels()
                # Check if the channel id is in message logging channels
                if message.channel.id not in message_logging_channels:
                    return

            # Log the message
            await self.log.message(
                log_message=message.content,
                channel_id=str(message.channel.id),
                channel_name=message.channel.name,
                user_id=str(message.author.id),
                user_name=message.author.name
            )
            
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore nel salvataggio del seguente messaggio: \n\'{message.content}\' \nCanale: {message.channel.name} ({message.channel.id}) \n{e}'
            await self.log.error(error_message, 'EVENT - MESSAGE')
            if communication_channel is not None:
                await communication_channel.send(self.log.error_message(command = 'EVENT - MESSAGE', message = error_message))