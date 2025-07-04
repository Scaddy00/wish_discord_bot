
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from os import getenv
# ----------------------------- Custom Libraries -----------------------------
from functions.roles import add_role_event, remove_role_event
from logger.logger import Logger

class ReactionEvents(commands.Cog):
    def __init__(self, bot: commands.Bot, log: Logger):
        self.bot = bot
        self.log = log
    
    # ============================= ON_RAW_REACTION_ADD (Add Role) =============================
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        guild: discord.Guild = self.bot.get_guild(payload.guild_id)
        message_id: str = payload.message_id
        emoji: discord.PartialEmoji = payload.emoji
        member_id: str = payload.member.id
        
        await add_role_event(self.bot.log, guild, message_id, emoji, member_id)
        
    # ============================= ON_RAW_REACTION_REMOVE (Remove Role) =============================
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent) -> None:
        guild: discord.Guild = self.bot.get_guild(payload.guild_id)
        message_id: str = payload.message_id
        emoji: discord.PartialEmoji = payload.emoji
        member_id: int = payload.user_id
        
        await remove_role_event(self.bot.log, guild, message_id, emoji, member_id)