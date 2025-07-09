
# ----------------------------- Imported Libraries -----------------------------
from discord.ext import commands
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from verification import VerificationManager
# ----------------------------- Events -----------------------------
from events.on_ready import OnReady
from events.member_events import MemberEvents
from events.reaction_events import ReactionEvents

# ============================= Add Events =============================
async def add_events(bot: commands.Bot, log: Logger, verification: VerificationManager) -> None:
    await bot.add_cog(OnReady(bot, log, verification))
    await bot.add_cog(MemberEvents(bot, log))
    await bot.add_cog(ReactionEvents(bot, log, verification))