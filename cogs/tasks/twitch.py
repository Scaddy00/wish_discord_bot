
# ----------------------------- Imported Libraries -----------------------------
from discord.ext import tasks
# ----------------------------- Custom Libraries -----------------------------
from cogs.twitch import TwitchApp

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Blank Variables ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
_twitch_app: TwitchApp

@tasks.loop(minutes=1.0)
async def check_twitch() -> None:
    if _twitch_app == None:
        return
    
    await _twitch_app.check_live_status()

async def setup_task(twitch_app) -> None:
    global _twitch_app
    _twitch_app = twitch_app
    check_twitch.start()