
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from os import getenv
# ----------------------------- Custom Libraries -----------------------------
from cogs.commands import add_commands
from cogs.events import add_events

# ============================= BOT SETUP HOOK =============================
class WishBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from logger import Logger
        from utils import config
        from cogs.verification import VerificationManager
        from cogs.twitch import TwitchApp
        
        self.log = Logger()
        self.verification = VerificationManager(self, self.log)
        self.twitch_app = TwitchApp(self, self.log)
        config.start()

    async def setup_hook(self):
        # COMMANDS
        await add_commands(self, self.log, self.verification, self.twitch_app)
        # EVENTS
        await add_events(self, self.log, self.verification, self.twitch_app)
        
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
            self.tree.clear_commands()
            synced = await self.tree.sync()
            print(f"[PROD] Comandi globali sincronizzati: {len(synced)}")