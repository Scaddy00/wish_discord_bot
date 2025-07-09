
# ----------------------------- Imported Libraries -----------------------------
import asyncio
import discord
from discord.ext import tasks
from discord.ext import commands
from os import getenv
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from functions.roles import add_role, remove_role

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Blank Variables ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
_bot: commands.Bot
_log: Logger

@tasks.loop(hours=1)
async def check_booster():
    if _bot == None:
        return

    # Load bot communication channel
    communication_channel = _bot.get_channel(int(getenv('BOT_COMMUNICATION_CHANNEL_ID')))
    
    try:
        # Get bot guild
        guild: discord.Guild = _bot.get_guild(int(getenv('GUILD_ID')))
        # Get all the members in the guild
        members: list[discord.Member] = guild.members
        # Get the booster role
        role: discord.Role = guild.get_role(getenv('ROLE_ID_SERVER_BOOSTER'))
        
        for member in members:
            if member.premium_since is not None: # Check if member boosted
                if role not in member.roles: # Check if role isn't already in member roles
                    await add_role(_log, guild, role.id, member.id) # Add role
            else: # Member not boosted
                if role in member.roles: # Check if role is in member roles
                    await remove_role(_log, guild, role.id, member.id) # Remove the role
    except Exception as e:
        # EXCEPTION
        error_message: str = f'Errore durante il controllo. \n{e}'
        await _log.error(error_message, 'TASK - CHECK BOOSTER')
        await communication_channel.send(_log.error_message(command = 'TASK - CHECK BOOSTER', message = error_message))

async def setup_task(bot, log):
    global _bot, _log
    _bot = bot
    _log = log
    check_booster.start()