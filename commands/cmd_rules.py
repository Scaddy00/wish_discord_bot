
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from discord import app_commands
from os import getenv
# ----------------------------- Custom Libraries -----------------------------
from logger.logger import Logger
from utility.printing import create_embed, load_embed_text

class CmdRules(commands.GroupCog, name="rule"):
    def __init__(self, bot: discord.Client, log: Logger):
        super().__init__()
        self.bot = bot
        self.log = log
    
    @app_commands.command(name="new", description="Crea un nuovo messaggio")
    async def new(self, interaction: discord.Interaction) -> None:
        # Get the guild from interaction
        guild: discord.Guild = interaction.guild
        # Load communication channel
        communication_channel = guild.get_channel(int(getenv('BOT_COMMUNICATION_CHANNEL_ID')))
        # Load rule channel
        rule_channel = guild.get_channel(int(getenv('RULE_CHANNEL_ID')))
        # Get the channel where the interaction started
        channel = interaction.channel
        
        # INFO Log the start of the creation of the message
        await self.log.command('Creazione di un nuovo messaggio', 'rule', 'NEW')
        
        # Send a response message
        await interaction.response.send_message('Inizio la creazione di un nuovo messaggio delle regole.')
        
        try:
            # Load embed message content
            message_content: dict = load_embed_text(guild, 'rule')
            # Create the embed message
            message: discord.Embed = create_embed(title=message_content['title'],
                                                  description=message_content['description'],
                                                  color=discord.Colour.from_str(message_content['color']))
            
            # Send the message in rule channel
            await rule_channel.send(embed=message)
            
            # INFO Log that the reaction were added
            await self.log.command('Messaggio inviato con successo', 'rule', 'NEW')
                        
        except TimeoutError:
            await channel.send('Tempo scaduto. Lavorazione interrotta!')
            # EXCEPTION
            error_message: str = 'Tempo scaduto durante la creazione di un nuovo messaggio.'
            await self.log.error(error_message, 'COMMAND - RULE - NEW')
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante la creazione di un nuovo messaggio.\n{e}'
            await self.log.error(error_message, 'COMMAND - RULE - NEW')
            await communication_channel.send(self.log.error_message(command='COMMAND - RULE - NEW', message=error_message))