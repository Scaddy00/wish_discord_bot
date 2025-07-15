
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from discord import app_commands
from os import getenv
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from utils.printing import create_embed_from_dict, load_single_embed_text
from config_manager import ConfigManager

class CmdInfo(commands.GroupCog, name="info"):
    def __init__(self, bot: commands.bot, log: Logger, config: ConfigManager):
        super().__init__()
        self.bot = bot
        self.log = log
        self.config = config
    
    @app_commands.command(name="dreamer", description="Invia un embed con le info per avere un Dreamer personalizzato")
    async def dreamer(self, interaction: discord.Interaction, channel: discord.TextChannel) -> None:
        # Get the guild from interaction
        guild: discord.Guild = interaction.guild
        # Load communication channel
        communication_channel = guild.get_channel(self.config.communication_channel)
        
        # INFO Log the start of the creation of the message
        await self.log.command('Creazione di un nuovo messaggio', 'info', 'DREAMER')
        
        try:
            # Load embed message content
            message_content: dict = await load_single_embed_text(guild, 'info-dreamer')
            # Create the embed message
            message: dict = create_embed_from_dict(message_content)
            
            # Send the message in the selected channel
            await channel.send(embed=message)
            
            # INFO Log that the embed was sent
            await self.log.command('Messaggio inviato', 'info', 'DREAMER')
            
            # Send the response to the initial message
            await interaction.response.send_message('Il messaggio è stato inviato correttamente')
        
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante la creazione e l\'invio di un nuovo messaggio.\n{e}'
            await self.log.error(error_message, 'COMMAND - INFO - DREAMER')
            await communication_channel.send(self.log.error_message(command='COMMAND - INFO - DREAMER', message=error_message))