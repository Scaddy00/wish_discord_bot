
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from os import getenv
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from cogs.tasks import setup_all_tasks
from cogs.verification import VerificationManager
from cogs.twitch import TwitchApp
from config_manager import ConfigManager

class OnReady(commands.Cog):
    def __init__(self, bot: commands.Bot, log: Logger, config: ConfigManager, verification: VerificationManager, twitch_app: TwitchApp):
        self.bot = bot
        self.log = log
        self.config = config
        self.verification = verification
        self.twitch_app = twitch_app
    
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        # Authenticate Twitch App
        await self.twitch_app._authenticate()
        # Restore verification pending tasks
        await self.verification.restore_pending_tasks()