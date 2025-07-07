
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from os import getenv
# ----------------------------- Custom Libraries -----------------------------
from logger.logger import Logger
from tasks import setup_all_tasks

class OnReady(commands.Cog):
    def __init__(self, bot: commands.Bot, log: Logger):
        self.bot = bot
        self.log = log
    
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        await setup_all_tasks(self.bot, self.log)