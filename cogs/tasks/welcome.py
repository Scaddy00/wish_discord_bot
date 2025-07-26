
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import tasks, commands
from datetime import datetime
from logger import Logger
import pytz
from os import getenv
import asyncio

# ----------------------------- Custom Libraries -----------------------------
from config_manager import ConfigManager
from utils import printing

ROME_TZ = pytz.timezone('Europe/Rome')

def extract_user_ids_from_welcome(welcome_messages: list[dict]) -> set:
    """
    Extract user IDs from the list of welcome message records.
    Args:
        welcome_messages (list[dict]): List of welcome message records from the database.
    Returns:
        set: Set of user IDs who have already received the welcome message.
    """
    return set(int(record['user_id']) for record in welcome_messages)

async def create_welcome_message(member: discord.Member, config: ConfigManager, guild: discord.Guild) -> list[discord.Embed]:
    """
    Create the welcome message embeds for a new member.
    Args:
        member (discord.Member): The member to welcome.
        config (ConfigManager): The configuration manager instance.
        guild (discord.Guild): The guild where the member joined.
    Returns:
        list[discord.Embed]: List of embeds to send as welcome message.
    """
    # Get rule channel
    rule_channel_id = config.load_admin('channels', 'rule')
    rule_channel: discord.TextChannel = None
    
    if rule_channel_id and rule_channel_id != '':
        rule_channel = guild.get_channel(int(rule_channel_id))
    
    # Load embed message content
    message_content: list[dict] = await printing.load_embed_text(guild, 'welcome', config)
    
    description: str = message_content[0]['description'].format(user=member.mention, rule=rule_channel.mention if rule_channel else "#regole")
    message: list[discord.Embed] = [
        printing.create_embed(
            title=message_content[0]['title'], # Load title
            description=description, # Load description adding the mentions required
            color=message_content[0]['color'], # Load the color from str
            image=message_content[0]['image'], # Load image url
            thumbnail=member.avatar.url if member.avatar != None else message_content[0]['thumbnail'], # Load thumbnail url
        ),
        printing.create_embed_from_dict(
            data=message_content[1]
        )
    ]
    return message

class Welcome(commands.Cog):
    """
    Cog for handling the periodic welcome message task.
    Sends a welcome message to new users who haven't received one yet.
    """
    def __init__(self, bot: commands.Bot, log: Logger, config: ConfigManager):
        """
        Initialize the Welcome cog.
        Args:
            bot (commands.Bot): The Discord bot instance.
            log (Logger): Logger instance for logging events and errors.
            config (ConfigManager): Configuration manager instance.
        """
        self.bot = bot
        self.log = log
        self.config = config

    async def execute_welcome_task(self):
        """
        Execute the welcome task logic manually.
        This method can be called directly without the task decorator.
        """
        try:
            # Get welcome message records from database
            welcome_messages = self.log.db.get_welcome()
            sent_user_ids = extract_user_ids_from_welcome(welcome_messages)
            # Get guild
            guild = self.bot.get_guild(int(getenv('GUILD_ID')))
            if not guild:
                await self.log.error("Guild not found.", 'EVENT - TASK WELCOME')
                return
            
            # Get welcome channel
            welcome_channel: discord.TextChannel = guild.system_channel
            
            if not welcome_channel:
                await self.log.error("Welcome channel not found.", 'EVENT - TASK WELCOME')
                return
            users = [member for member in guild.members]
            
            await asyncio.sleep(1)
            
            # Check if welcome message exists for each user
            for user in users:
                if user.id not in sent_user_ids and user.bot == False:
                    # Create welcome message
                    message = await create_welcome_message(user, self.config, guild)
                    # Send welcome message to user
                    await welcome_channel.send(embeds=message)
                    # Insert welcome message into database
                    self.log.db.insert_welcome(datetime.now().isoformat(), str(user.id), user.name)
                    # INFO LOG
                    await self.log.event(f"Messaggio di benvenuto inviato a {user.name} ({user.id})", 'welcome')
            # INFO LOG
            await self.log.event(f"Messaggio di benvenuto inviato a {len(sent_user_ids)} utenti", 'welcome')
        except Exception as e:
            # EXCEPTION
            communication_channel = self.bot.get_channel(self.config.communication_channel)
            error_message: str = f"Errore durante la task controllo del messaggio di benvenuto. \n{e}"
            await self.log.error(error_message, 'EVENT - TASK WELCOME')
            if communication_channel:
                await communication_channel.send(self.log.error_message(command = 'EVENT - TASK WELCOME', message = error_message))

    @tasks.loop(hours=1)
    async def welcome(self):
        """
        Periodic task that checks for new users and sends them a welcome message if they haven't received one yet.
        """
        await self.execute_welcome_task()

async def setup(bot):
    """
    Setup function for the Welcome cog.
    Args:
        bot (commands.Bot): Discord bot instance to add the cog to.
    """
    await bot.add_cog(Welcome(bot, Logger(), ConfigManager()))