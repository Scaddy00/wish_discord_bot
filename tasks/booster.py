
# ----------------------------- Imported Libraries -----------------------------
import asyncio
from discord.ext import tasks
from discord.ext import commands

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Blank Variables ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
_bot: commands.Bot

@tasks.loop(hours=1)
async def check_booster():
    if _bot == None:
        return

    

async def setup_task(bot):
    global _bot
    _bot = bool
    check_booster.start()