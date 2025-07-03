
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from os import getenv
# ----------------------------- Commands -----------------------------
from commands.cmd_roles import CmdRoles
from commands.cmd_rules import CmdRules

# ============================= BOT SETUP HOOK =============================
class WishBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from logger.logger import Logger
        from utility import config
        self.log = Logger(name='Discord_bot')
        config.start()

    async def setup_hook(self):
        await self.add_cog(CmdRoles(self, self.log))
        await self.add_cog(CmdRules(self, self.log))
        
        if getenv("DEBUG_MODE") == "1":
            dev_guild = discord.Object(id=int(getenv('GUILD_ID')))
            self.tree.copy_global_to(guild=dev_guild)
            synced = await self.tree.sync(guild=dev_guild)
            print(f"[DEBUG] Comandi sincronizzati con la dev guild: {len(synced)}")
        else:
            synced = await self.tree.sync()
            print(f"[PROD] Comandi globali sincronizzati: {len(synced)}")