
# ----------------------------- Imported Libraries -----------------------------
from discord.ext import commands
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from cogs.verification import VerificationManager
from cogs.twitch import TwitchApp
from config_manager import ConfigManager
# ----------------------------- Events -----------------------------
from .on_ready import OnReady
from .member_events import MemberEvents
from .reaction_events import ReactionEvents
from .message_events import MessageEvents
from .guild_events import GuildEvents

# ============================= Add Events =============================
async def add_events(bot: commands.Bot, log: Logger, config: ConfigManager, verification: VerificationManager, twitch_app: TwitchApp) -> None:
    await bot.add_cog(OnReady(bot, log, config, verification, twitch_app))
    await bot.add_cog(GuildEvents(bot, log, config))
    await bot.add_cog(MemberEvents(bot, log, config))
    await bot.add_cog(ReactionEvents(bot, log, config, verification))
    await bot.add_cog(MessageEvents(bot, log, config))