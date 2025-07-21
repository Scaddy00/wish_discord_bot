
# ----------------------------- Imported Libraries -----------------------------
from discord.ext import commands
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from cogs.verification import VerificationManager
from cogs.twitch import TwitchApp
from config_manager import ConfigManager
# ----------------------------- Commands -----------------------------
from .cmd_admin import CmdAdmin
from .cmd_roles import CmdRoles
from .cmd_rules import CmdRules
from .cmd_info import CmdInfo
from .cmd_config import CmdConfig
from .cmd_utility import CmdUtility
from .cmd_verification import CmdVerification
from .cmd_twitch import CmdTwitch

# ============================= Add Commands =============================
async def add_commands(bot: commands.Bot, log: Logger, config: ConfigManager, verification: VerificationManager, twitch_app: TwitchApp) -> None:
    await bot.add_cog(CmdAdmin(bot, log, config))
    await bot.add_cog(CmdRoles(bot, log, config))
    await bot.add_cog(CmdRules(bot, log, config, verification))
    await bot.add_cog(CmdInfo(bot, log, config))
    await bot.add_cog(CmdConfig(bot, log, config, twitch_app, verification))
    await bot.add_cog(CmdUtility(bot, log, config))
    await bot.add_cog(CmdVerification(bot, log, config, verification))
    await bot.add_cog(CmdTwitch(bot, log, config, twitch_app))