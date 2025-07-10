
# ----------------------------- Imported Libraries -----------------------------
from discord.ext import commands
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from cogs.twitch import TwitchApp
# ----------------------------- Tasks -----------------------------
from .booster import setup_task as setup_booster_task
from .twitch import setup_task as setup_twitch_task

async def setup_all_tasks(bot: commands.bot, log: Logger, twitch_app: TwitchApp) -> None:
    await setup_booster_task(bot, log)
    await setup_twitch_task(twitch_app)