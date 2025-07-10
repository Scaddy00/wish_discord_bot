
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from discord import app_commands
from os import getenv
import re
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from utils.config import add_exception

class CmdConfig(commands.GroupCog, name="config"):
    def __init__(self, bot: commands.bot, log: Logger):
        super().__init__()
        self.bot = bot
        self.log = log
    
    @app_commands.command(name="add-exception", description="Aggiunge una lista di ruoli alle eccezioni")
    async def add_exception(self, interaction: discord.Interaction, tag: str) -> None:
        # Get the guild from interaction
        guild: discord.Guild = interaction.guild
        # Load communication channel
        communication_channel = guild.get_channel(int(getenv('BOT_COMMUNICATION_CHANNEL_ID')))
        # Get the channel
        channel = interaction.channel

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        # INFO Log the start of the creation of the exception
        await self.log.command('Creazione di una nuova eccezione', 'config', 'EXCEPTION')
        
        output_tag: str = tag
        output_list: list = []
        
        try:
            await interaction.response.send_message('Menziona di seguito i ruoli che vuoi aggiungere alle eccezioni. \nPuoi scrivere tutti i ruoli insieme divisi da | oppure un ruolo per messaggio. \nQuando hai terminato scrivi "stop". \nHai **3 minuti** per completare l\'operazione.')
            
            while True:
                # Get the response from the user, with a timeout of 3 minutes (180 s)
                response = await self.bot.wait_for('message', check=check, timeout=180.0)
                
                if response.content.lower() == 'stop':
                    break
                
                # Split the message content with the selected divider
                splitted: list = response.content.replace(' ', '').split('|')
                
                for item in splitted:
                    # The role id is taken using a regex
                    output_list.append(''.join(re.findall(r'\d+', item)))
            
            # INFO Log the status of the operation
            await self.log.command('Ruoli ottenuti', 'config', 'EXCEPTION')
            
            try:
                # Add the new exception to config file
                await add_exception(output_tag, output_list)
                
                # INFO Config saved with success
                await self.log.command('Dati salvati con successo nel file config', 'config', 'EXCEPTION')
                
                # Send a message that tell the user that the operation is complete
                await channel.send('Lavorazione completata!')
                
                # INFO Log that the process is complete
                await self.log.command('Lavorazione completata', 'config', 'EXCEPTION')
            except Exception as e:
                # EXCEPTION
                error_message: str = f'Errore durante l\'invio del nuovo messaggio.\n{e}'
                await self.log.error(error_message, 'COMMAND - CONFIG - EXCEPTION')
                await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - EXCEPTION', message=error_message))
        except TimeoutError:
            await channel.send('Tempo scaduto. Lavorazione interrotta!')
            # EXCEPTION
            error_message: str = 'Tempo scaduto durante la creazione di un nuovo messaggio.'
            await self.log.error(error_message, 'COMMAND - CONFIG - EXCEPTION')
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante l\'aggiunta di nuove eccezioni al file config.\n{e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - EXCEPTION')
            await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - EXCEPTION', message=error_message))