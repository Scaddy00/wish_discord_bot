
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from os import getenv
# ----------------------------- Commands -----------------------------
from commands.cmd_admin import CmdAdmin
from commands.cmd_roles import CmdRoles
from commands.cmd_rules import CmdRules
from commands.cmd_info import CmdInfo
from commands.cmd_config import CmdConfig
from commands.cmd_utility import CmdUtility
from commands.cmd_verification import CmdVerification
# ----------------------------- Events -----------------------------
from events.on_ready import OnReady
from events.member_events import MemberEvents
from events.reaction_events import ReactionEvents

# ============================= BOT SETUP HOOK =============================
class WishBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from logger.logger import Logger
        from utility import config
        from verification import VerificationManager
        
        self.log = Logger(name='Discord_bot')
        self.verification = VerificationManager(self, self.log)
        config.start()

    async def setup_hook(self):
        # COMMANDS
        await self.add_cog(CmdAdmin(self, self.log))
        await self.add_cog(CmdRoles(self, self.log))
        await self.add_cog(CmdRules(self, self.log, self.verification))
        await self.add_cog(CmdInfo(self, self.log))
        await self.add_cog(CmdConfig(self, self.log))
        await self.add_cog(CmdUtility(self, self.log))
        await self.add_cog(CmdVerification(self, self.log, self.verification))
        # EVENTS
        await self.add_cog(OnReady(self, self.log, self.verification))
        await self.add_cog(MemberEvents(self, self.log))
        await self.add_cog(ReactionEvents(self, self.log, self.verification))
        
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