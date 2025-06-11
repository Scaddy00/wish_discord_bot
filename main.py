
# ----------------------------- Imported Libraries -----------------------------
import discord
from dotenv import load_dotenv
from os import getenv
# ----------------------------- Custom Libraries -----------------------------
from logger.logger import Logger

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Blank Variables ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
bot: discord.Client
log: Logger
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Variables ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
ERROR_CHANNEL_ID: int = int(str(getenv('ERROR_CHANNEL_ID')))


# ============================= ON_MEMBER_JOIN (Welcome) =============================
@bot.event # type: ignore
async def on_member_join(member: discord.Member) -> None:
    # Load error channel
    error_channel = bot.get_channel(ERROR_CHANNEL_ID)
    # Get guild
    guild: discord.Guild = member.guild
    
    try:
        welcome_channel: discord.TextChannel = guild.system_channel # type: ignore
        message: str = f'Benvenuto {member.mention}!'
        await welcome_channel.send(message)
        # INFO LOG
        await log.event(f'Nuovo utente aggiunto, {member.name}({member.id})', 'welcome')
    except Exception as e:
        # EXCEPTION
        error_message: str = log.error_message(command = 'EVENT - WELCOME', message = f'Errore durante l\'invio del messaggio di benvenuto \n{e}')
        await log.error(error_message, 'EVENT - WELCOME')
        await error_channel.send(error_message) # type: ignore

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