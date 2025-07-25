
# ----------------------------- Imported Libraries -----------------------------
from discord.ext import commands
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from config_manager import ConfigManager
from cogs.twitch import TwitchApp
# ----------------------------- Tasks -----------------------------
from .booster import setup_task as setup_booster_task
from .twitch import setup_task as setup_twitch_task

async def setup_all_tasks(bot: commands.bot, log: Logger, config: ConfigManager, twitch_app: TwitchApp) -> None:
    await setup_booster_task(bot, log, config)
    await setup_twitch_task(twitch_app)
    await bot.loop.create_task(bot.load_extension('cogs.tasks.weekly_report'))
    await bot.loop.create_task(bot.load_extension('cogs.tasks.database_cleanup'))
    await bot.loop.create_task(bot.load_extension('cogs.tasks.welcome'))