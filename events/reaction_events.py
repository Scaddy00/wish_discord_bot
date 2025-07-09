
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from os import getenv
# ----------------------------- Custom Libraries -----------------------------
from functions.roles import add_role_event, remove_role_event, add_role
from logger import Logger
from verification import VerificationManager
from utility.config import load_rules

class ReactionEvents(commands.Cog):
    def __init__(self, bot: commands.Bot, log: Logger, verification: VerificationManager):
        self.bot = bot
        self.log = log
        self.verification = verification
    
    # ============================= ON_RAW_REACTION_ADD (Add Role) =============================
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        guild: discord.Guild = self.bot.get_guild(payload.guild_id)
        message_id: str = payload.message_id
        emoji: discord.PartialEmoji = payload.emoji
        member: discord.Member = payload.member
        
        # Check for verification
        rules_data: dict = load_rules()
        if message_id == int(rules_data.get('message_id', '0')) and str(emoji) == rules_data.get('emoji', ''):
            if not member.bot:
                await add_role(self.log, guild, self.verification.temp_role_id, member.id)
                await self.verification.start_timer(guild.id, member.id)
        
        # Check for roles
        await add_role_event(self.bot.log, guild, message_id, emoji, member.id)
        
    # ============================= ON_RAW_REACTION_REMOVE (Remove Role) =============================
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent) -> None:
        guild: discord.Guild = self.bot.get_guild(payload.guild_id)
        message_id: str = payload.message_id
        emoji: discord.PartialEmoji = payload.emoji
        member_id: int = payload.user_id
        
        await remove_role_event(self.bot.log, guild, message_id, emoji, member_id)