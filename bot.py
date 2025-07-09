
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from os import getenv
# ----------------------------- Custom Libraries -----------------------------
from commands import add_commands
from events import add_events

# ============================= BOT SETUP HOOK =============================
class WishBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from logger import Logger
        from utility import config
        from verification import VerificationManager
        
        self.log = Logger(name='Discord_bot')
        self.verification = VerificationManager(self, self.log)
        config.start()

    async def setup_hook(self):
        # COMMANDS
        await add_commands(self, self.log, self.verification)
        # EVENTS
        await add_events(self, self.log, self.verification)
        
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