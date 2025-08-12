
# ----------------------------- Imported Libraries -----------------------------
# Third-party library imports
import discord
from discord.ext import commands

# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from cogs.tasks import setup_all_tasks
from cogs.verification import VerificationManager
from cogs.twitch import TwitchApp
from config_manager import ConfigManager

class OnReady(commands.Cog):
    """
    Cog that handles the Discord client's ready event.
    
    Authenticates Twitch app and restores verification pending tasks
    once the bot is ready.
    """

    def __init__(
        self,
        bot: commands.Bot,
        log: Logger,
        config: ConfigManager,
        verification: VerificationManager,
        twitch_app: TwitchApp,
    ) -> None:
        self.bot: commands.Bot = bot
        self.log: Logger = log
        self.config: ConfigManager = config
        self.verification: VerificationManager = verification
        self.twitch_app: TwitchApp = twitch_app
    
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """
        Listener invoked when the bot is ready.
        
        Ensures Twitch authentication and restores verification tasks.
        """
        # Authenticate Twitch App
        await self.twitch_app._authenticate()
        # Restore verification pending tasks
        await self.verification.restore_pending_tasks()