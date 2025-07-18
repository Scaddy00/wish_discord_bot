
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from os import getenv
# ----------------------------- Custom Libraries -----------------------------
from cogs.commands import add_commands
from cogs.events import add_events
from cogs.tasks import setup_all_tasks

# ============================= BOT SETUP HOOK =============================
class WishBot(commands.Bot):
    """
    Main Discord bot class for the Wish Discord Bot.
    
    Handles all bot functionality including commands, events, tasks,
    verification system, and Twitch integration.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the WishBot with all necessary components.
        
        Sets up logger, config manager, verification system, and Twitch app.
        """
        super().__init__(*args, **kwargs)
        from logger import Logger
        from config_manager import ConfigManager
        from cogs.verification import VerificationManager
        from cogs.twitch import TwitchApp
        
        self.color = '0xA6BBF0'
        
        self.log = Logger()
        self.config = ConfigManager()
        self.verification = VerificationManager(self, self.log, self.config)
        self.twitch_app = TwitchApp(self, self.log, self.config)

    async def setup_hook(self):
        """
        Setup hook called when the bot is starting up.
        
        Loads all commands, events, and tasks. Handles command synchronization
        for both debug and production modes.
        """
        # COMMANDS
        await add_commands(self, self.log, self.config, self.verification, self.twitch_app)
        # EVENTS
        await add_events(self, self.log, self.config, self.verification, self.twitch_app)
        # TASKS
        await setup_all_tasks(self, self.log, self.config, self.twitch_app)
        
        if getenv("DEBUG_MODE") == "1":
            dev_guild = discord.Object(id=int(getenv('GUILD_ID')))
            self.tree.clear_commands(guild=dev_guild)
            self.tree.copy_global_to(guild=dev_guild)
            synced = await self.tree.sync(guild=dev_guild)
            print(f"[DEBUG] Comandi sincronizzati con la dev guild: {len(synced)}")
            
            tree = self.tree._get_all_commands()
            commands_names: list = [command.name for command in tree]
            print(f"[DEBUG] Nomi dei comandi: {commands_names}")
        else:
            synced = await self.tree.sync()
            print(f"[PROD] Comandi globali sincronizzati: {len(synced)}")