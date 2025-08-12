
# ----------------------------- Imported Libraries -----------------------------
# Standard library imports
from os import getenv

# Third-party library imports
import discord
from discord.ext import commands
from dotenv import load_dotenv

# ----------------------------- Custom Libraries -----------------------------
from bot import WishBot

# Load .env file
load_dotenv()

# ============================= BOT SETUP =============================
intents = discord.Intents(
    guilds=True,
    members=True,           # Necessario per eventi membro/ruoli/benvenuto
    messages=True,          # Necessario per message logging
    message_content=True,   # Necessario per on_message e logging contenuti
    reactions=True,         # Necessario per reaction roles/verification
    presences=False,
    bans=False,
    emojis_and_stickers=False,
    integrations=False,
    webhooks=False,
    invites=False,
    voice_states=False,
    typing=False,
    guild_scheduled_events=False,
    auto_moderation_configuration=False,
    auto_moderation_execution=False
)
bot = WishBot(command_prefix=str(getenv('COMMAND_PREFIX')), intents=intents)

# ============================= MAIN AND START =============================
# >>==============<< MAIN >>==============<< 
def main() -> None:
    """
    Main function that starts the Discord bot.
    
    Loads environment variables and runs the bot with the Discord token.
    """
    # Start the bot
    bot.run(str(getenv('DISCORD_TOKEN')))

if __name__ == '__main__':
    main()