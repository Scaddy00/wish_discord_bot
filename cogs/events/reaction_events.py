
# ----------------------------- Imported Libraries -----------------------------
# Third-party library imports
import discord
from discord.ext import commands

# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from config_manager import ConfigManager
from cogs.verification import VerificationManager
from utils.roles import add_role_event, remove_role_event, add_role, remove_role

class ReactionEvents(commands.Cog):
    """
    Cog that handles reaction add/remove events for verification and roles.
    """

    def __init__(self, bot: commands.Bot, log: Logger, config: ConfigManager, verification: VerificationManager) -> None:
        self.bot: commands.Bot = bot
        self.log: Logger = log
        self.config: ConfigManager = config
        self.verification: VerificationManager = verification
    
    # ============================= ON_RAW_REACTION_ADD (Add Role) =============================
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        guild: discord.Guild = self.bot.get_guild(payload.guild_id)
        message_id: str = payload.message_id
        emoji: discord.PartialEmoji = payload.emoji
        member: discord.Member = payload.member
        
        # Check for verification
        rules_data: dict = self.config.load_rules()
        rules_message_id = rules_data.get('message_id')
        try:
            rules_message_id_int = int(rules_message_id)
        except (TypeError, ValueError):
            rules_message_id_int = None

        if rules_message_id_int and message_id == rules_message_id_int and str(emoji) == rules_data.get('emoji', ''):
            if not member.bot:
                # Only add temp role if it's configured
                if self.verification.temp_role_id != 0:
                    await add_role(self.log, guild, self.verification.temp_role_id, member.id, self.config)
                    # Remove not_verified role if configured
                    not_verified_role_id = self.config.load_admin('roles', 'not_verified')
                    if not_verified_role_id and not_verified_role_id != '':
                        await remove_role(self.log, guild, int(not_verified_role_id), member.id, self.config)
                    # INFO Log that the user has been added to the temp role
                    await self.log.verification(f'User {member.name} ({member.id}) è in stato di verifica', 'pending', str(member.id))
                    # Start timer for verification
                    await self.verification.start_timer(guild.id, member.id)
                else:
                    # Log that verification is not properly configured
                    await self.log.verification(f'User {member.name} ({member.id}) tried to verify but temp_role_id is not configured', 'verification', str(member.id))
        
        # Check for roles
        await add_role_event(self.bot.log, self.config, guild, message_id, emoji, member.id)
        
    # ============================= ON_RAW_REACTION_REMOVE (Remove Role) =============================
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent) -> None:
        guild: discord.Guild = self.bot.get_guild(payload.guild_id)
        message_id: str = payload.message_id
        emoji: discord.PartialEmoji = payload.emoji
        member_id: int = payload.user_id
        
        await remove_role_event(self.bot.log, guild, self.config, message_id, emoji, member_id)