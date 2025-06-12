
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from dotenv import load_dotenv
from os import getenv
# ----------------------------- Custom Libraries -----------------------------
from logger.logger import Logger

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Blank Variables ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
bot: discord.Client
log: Logger
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Variables ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
BOT_COMMUNICATION_CHANNEL_ID: int = int(str(getenv('BOT_COMMUNICATION_CHANNEL_ID')))
ADMIN_CHANNEL_ID: int = int(str(getenv('ADMIN_CHANNEL_ID')))

# ============================= BOT SETUP =============================
intents = discord.Intents.all()
intents.messages = True
bot = commands.Bot(command_prefix=str(getenv('COMMAND_PREFIX')), intents=intents)


# ============================= ON_MEMBER_JOIN (Welcome) =============================
@bot.event
async def on_member_join(member: discord.Member) -> None:
    # Load bot communication channel
    communication_channel = bot.get_channel(BOT_COMMUNICATION_CHANNEL_ID)
    # Get guild
    guild: discord.Guild = member.guild
    
    try:
        welcome_channel: discord.TextChannel = guild.system_channel
        # TODO Update the message with the Embed
        message: str = f'Benvenuto {member.mention}!'
        await welcome_channel.send(message)
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

# ============================= MAIN =============================
def main():
    # Load .env file
    load_dotenv()
    
    global log
    log = Logger(name = 'Discord_bot')
    
    # Start the bot
    bot.run(str(getenv('DISCORD_TOKEN')))

if __name__ == '__main__':
    main()