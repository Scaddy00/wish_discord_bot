
# ----------------------------- Imported Libraries -----------------------------
from discord.ext import commands
# ----------------------------- Custom Libraries -----------------------------
from .booster import setup_task as setup_booster_task

async def setup_all_tasks(bot: commands.bot) -> None:
    await setup_booster_task(bot)