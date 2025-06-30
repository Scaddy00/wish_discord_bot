
# ----------------------------- Imported Libraries -----------------------------
import discord, asyncio
from discord.ext import commands
from dotenv import load_dotenv
from os import getenv
# ----------------------------- Custom Libraries -----------------------------
from logger.logger import Logger
from utility import config, printing
from events.roles import add_role_event, remove_role_event
# ----------------------------- Commands -----------------------------
from commands.cmd_roles import CmdRoles

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Blank Variables ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
bot: commands.Bot
log: Logger
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Variables ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
BOT_COMMUNICATION_CHANNEL_ID: int = int(str(getenv('BOT_COMMUNICATION_CHANNEL_ID')))
ADMIN_CHANNEL_ID: int = int(str(getenv('ADMIN_CHANNEL_ID')))

# ============================= BOT SETUP HOOK =============================
class WishBot(commands.Bot):
    async def setup_hook(self):
        await self.add_cog(CmdRoles(self, log))
        await self.tree.sync(guild=discord.Object(id=int(getenv('GUILD_ID'))))

# ============================= BOT SETUP =============================
intents = discord.Intents.all()
intents.messages = True
bot = WishBot(command_prefix=str(getenv('COMMAND_PREFIX')), intents=intents)

# ============================= ON_MEMBER_JOIN (Welcome) =============================
@bot.event
async def on_member_join(member: discord.Member) -> None:
    # Load bot communication channel
    communication_channel = bot.get_channel(BOT_COMMUNICATION_CHANNEL_ID)
    # Get guild
    guild: discord.Guild = member.guild
    
    try:
        welcome_channel: discord.TextChannel = guild.system_channel
        rule_channel: discord.TextChannel = guild.get_channel(int(getenv('RULE_CHANNEL_ID')))
        # Load embed message content
        message_content: dict = printing.load_embed_text(guild, 'welcome')
        
        message: discord.Embed = printing.create_embed(title=message_content['title'], # Load title
                                                       description=message_content['description'].format(user=member.mention, rule=rule_channel.mention), # Load description adding the mentions required
                                                       color=discord.Colour.from_str(message_content['color']), # Load the color from str
                                                       image=message_content['image_url'], # Load image url
                                                       thumbnail=message_content['thumbnail_url']) # Load thumbnail url
        
        await welcome_channel.send(embed=message)
        # INFO LOG
        await log.event(f'Nuovo utente aggiunto, {member.name} ({member.id})', 'welcome')
    except Exception as e:
        # EXCEPTION
        error_message: str = f'Errore durante l\'invio del messaggio di benvenuto. \nUtente: {member.name} ({member.id}) \n{e}'
        await log.error(error_message, 'EVENT - MEMBER WELCOME')
        await communication_channel.send(log.error_message(command = 'EVENT - WELCOME', message = error_message))

# ============================= ON_MEMBER_REMOVE (ByeBye) =============================
@bot.event
async def on_raw_member_remove(payload: discord.RawMemberRemoveEvent) -> None:
    # Load bot communication channel
    communication_channel = bot.get_channel(BOT_COMMUNICATION_CHANNEL_ID)
    # Get the user
    user: discord.User = payload.user
    
    try:
        await communication_channel.send(f'COMUNICAZIONE -> L\'utente {user.mention} ha lasciato il server')
        # INFO LOG
        await log.event(f'Utente uscito dal server, {user.name} ({user.id})', 'remove')
    except Exception as e:
        # EXCEPTION
        error_message: str = f'Errore durante l\'invio del messaggio di ByeBye. \nUtente: {user.name} ({user.id})\n{e}'
        await log.error(error_message, 'EVENT - MEMBER REMOVE')
        await communication_channel.send(log.error_message(command = 'EVENT - MEMBER REMOVE', message = error_message))

# ============================= ON_RAW_REACTION_ADD (Add Role) =============================
@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent) -> None:
    guild: discord.Guild = bot.get_guild(payload.guild_id)
    message_id: str = payload.message_id
    emoji: discord.PartialEmoji = payload.emoji
    member_id: str = payload.member.id
    
    await add_role_event(log, guild, message_id, emoji, member_id)
    
# ============================= ON_RAW_REACTION_REMOVE (Remove Role) =============================
@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent) -> None:
    guild: discord.Guild = bot.get_guild(payload.guild_id)
    message_id: str = payload.message_id
    emoji: discord.PartialEmoji = payload.emoji
    member_id: int = payload.user_id
    
    await remove_role_event(log, guild, message_id, emoji, member_id)

# ============================= MAIN AND START =============================
# >>==============<< MAIN >>==============<< 
def main():
    # Load .env file
    load_dotenv()
    
    global log
    log = Logger(name = 'Discord_bot')

    # Start the config file check
    config.start()
    
    # Start the bot
    bot.run(str(getenv('DISCORD_TOKEN')))
    
    # Clears the internal state of the bot
    bot.clear()

if __name__ == '__main__':
    main()