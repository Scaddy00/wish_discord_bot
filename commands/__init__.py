
# ----------------------------- Imported Libraries -----------------------------
from discord.ext import commands
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from verification import VerificationManager
# ----------------------------- Commands -----------------------------
from commands.cmd_admin import CmdAdmin
from commands.cmd_roles import CmdRoles
from commands.cmd_rules import CmdRules
from commands.cmd_info import CmdInfo
from commands.cmd_config import CmdConfig
from commands.cmd_utility import CmdUtility
from commands.cmd_verification import CmdVerification

# ============================= Add Commands =============================
async def add_commands(bot: commands.Bot, log: Logger, verification: VerificationManager) -> None:
    await bot.add_cog(CmdAdmin(bot, log))
    await bot.add_cog(CmdRoles(bot, log))
    await bot.add_cog(CmdRules(bot, log, verification))
    await bot.add_cog(CmdInfo(bot, log))
    await bot.add_cog(CmdConfig(bot, log))
    await bot.add_cog(CmdUtility(bot, log))
    await bot.add_cog(CmdVerification(bot, log, verification))