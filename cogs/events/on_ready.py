
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from os import getenv
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from cogs.tasks import setup_all_tasks
from cogs.verification import VerificationManager

class OnReady(commands.Cog):
    def __init__(self, bot: commands.Bot, log: Logger, verification: VerificationManager):
        self.bot = bot
        self.log = log
        self.verification = verification
    
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        await setup_all_tasks(self.bot, self.log)
        # Restore verification pending tasks
        await self.verification.restore_pending_tasks()