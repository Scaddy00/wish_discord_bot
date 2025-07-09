
# ----------------------------- Imported Libraries -----------------------------
from discord.ext import commands
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
# ----------------------------- Tasks -----------------------------
from .booster import setup_task as setup_booster_task

async def setup_all_tasks(bot: commands.bot, log: Logger) -> None:
    await setup_booster_task(bot, log)