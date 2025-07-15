
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from os import getenv
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from config_manager import ConfigManager

class GuildEvents(commands.Cog):
    def __init__(self, bot: commands.Bot, log: Logger, config: ConfigManager):
        self.bot = bot
        self.log = log
        self.config = config
    
    # ============================= ON_GUILD_JOIN =============================
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        channel: discord.TextChannel = None
        # Find a general channel where to send the message
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                channel = channel
                break
        
        await channel.send(
            f'Ciao! Sono {self.bot.user.name} e sono qui per aiutarti!\n'
            f'Per iniziare, puoi inviare il comando `/config standard` per eseguire la configurazione del bot.')
        
        # INFO LOG
        await self.log.event(f'Bot aggiunto in {guild.name} ({guild.id})', 'guild_join')
        
        