
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from discord import app_commands
from os import getenv
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from config_manager import ConfigManager
from cogs.verification import VerificationManager
from utils.printing import create_embed_from_dict, load_embed_text, load_single_embed_text

class CmdRules(commands.GroupCog, name="rule"):
    def __init__(self, bot: commands.bot, log: Logger, config: ConfigManager, verification: VerificationManager):
        super().__init__()
        self.bot = bot
        self.log = log
        self.config = config
        self.verification = verification
    
    @app_commands.command(name="new", description="Crea un nuovo messaggio")
    async def new(self, interaction: discord.Interaction, address_channel: discord.TextChannel) -> None:
        # Get the guild from interaction
        guild: discord.Guild = interaction.guild
        # Load communication channel
        communication_channel = guild.get_channel(int(getenv('BOT_COMMUNICATION_CHANNEL_ID')))
        # Get the channel where the interaction started
        channel = interaction.channel
        
        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel
        
        # INFO Log the start of the creation of the message
        await self.log.command('Creazione di un nuovo messaggio', 'rule', 'NEW')
        
        # Send a response message
        await interaction.response.send_message('Inizio la creazione di un nuovo messaggio delle regole.')
        
        # Check if the reaction emoji is saved in config file
        # If not, request the emoji
        rules_config: dict = self.config.load_rules()
        if rules_config.get('emoji', '') == '' or rules_config.get('emoji', '') == None:
            while True:
                await channel.send('Nel file di configurazione manca l\'emoji necessaria perla reazione. \nInviala di seguito, così potrò procedere con la creazione del messaggio. \nHai **3 minuti** per inviare l\'emoji.')
                emoji_response: discord.Message = await self.bot.wait_for('message', check=check, timeout=180.0)
                
                # Format the message
                emoji: str = emoji_response.content.replace(' ', '')
                
                # Check if the emoji is correct
                try:
                    discord.PartialEmoji.from_str(emoji)
                    rules_config['emoji'] = emoji
                    break
                except Exception:
                    await channel.send(f"L'emoji `{emoji}` non è valida. Riprova.")
                    continue
        
        try:
            # Load embed message content
            message_content: list = await load_embed_text(guild, 'rule')
            # Create the embed message
            message: list[discord.Embed] = [create_embed_from_dict(content) for content in message_content]
            
            # Send the message in rule channel
            await address_channel.send(embeds=message)
            
            try:
                # Load the embed content
                verification_content: dict = await load_single_embed_text(guild, 'verification')
                
                # Create the embed
                verification_message: discord.Embed = create_embed_from_dict(verification_content)
                
                # Send the embed with the reaction emoji
                message: discord.Message = await address_channel.send(embed=verification_message)
                
                # INFO Log that the message for the reaction was sent
                await self.log.command('Messaggio reazione inviato', 'rule', 'NEW')
                
                # Add the reaction
                try:
                    emoji = discord.PartialEmoji.from_str(rules_config['emoji'])
                    await message.add_reaction(emoji)
                except Exception as e:
                    # EXCEPTION
                    error_message: str = f'Errore nell\'aggiungere la reazione {rules_config['emoji']}\n{e}'
                    await self.log.error(error_message, 'COMMAND - RULE - NEW')
                    await communication_channel.send(self.log.error_message(command='COMMAND - RULE - NEW', message=error_message))
                
                # INFO Log that reaction was added
                await self.log.command('Reazione aggiunta al messaggio', 'rule', 'NEW')
                
                # Save the data in config file
                rules_config['message_id'] = str(message.id)
                self.config.add_rules(rules_config)
                
                # INFO Log that data was saved
                await self.log.command('Dati salvati con successo', 'rule', 'NEW')
                
            except Exception as e:
                # EXCEPTION
                error_message: str = f'Errore durante la fase di invio del messaggio con reazione e aggiunta della reazione.\n{e}'
                await self.log.error(error_message, 'COMMAND - RULE - NEW')
                await communication_channel.send(self.log.error_message(command='COMMAND - RULE - NEW', message=error_message))
            
            
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