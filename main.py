
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from dotenv import load_dotenv
from os import getenv
# ----------------------------- Custom Libraries -----------------------------
from bot import WishBot

# Load .env file
load_dotenv()

# ============================= BOT SETUP =============================
intents = discord.Intents.all()
intents.messages = True
bot = WishBot(command_prefix=str(getenv('COMMAND_PREFIX')), intents=intents)

# ============================= MAIN AND START =============================
# >>==============<< MAIN >>==============<< 
def main():
    # Start the bot
    bot.run(str(getenv('DISCORD_TOKEN')))

if __name__ == '__main__':
    main()