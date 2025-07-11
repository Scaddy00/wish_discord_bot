
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from os import getenv
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from utils.config import load_exception

class MessageEvents(commands.Cog):
    def __init__(self, bot: commands.Bot, log: Logger):
        super().__init__()
        self.bot = bot
        self.log = log
    
    # ============================= ON_MESSAGE =============================
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        # Load bot communication channel
        communication_channel = self.bot.get_channel(int(getenv('BOT_COMMUNICATION_CHANNEL_ID')))
        
        try:
            if message.author.bot:
                return
            
            # Get exception list
            channel_exceptions: list[int] = load_exception('message_logger')
            
            # Check if the channel id is in exception list
            if message.channel.id in channel_exceptions:
                return

            # Log the message
            await self.log.message(
                log_message=message.content,
                channel_id=message.channel.id,
                channel_name=message.channel.name
            )
            
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore nel salvataggio del seguente messaggio: \n\'{message.content}\' \nCanale: {message.channel.name} ({message.channel.id}) \n{e}'
            await self.log.error(error_message, 'EVENT - MESSAGE')
            await communication_channel.send(self.log.error_message(command = 'EVENT - MESSAGE', message = error_message))