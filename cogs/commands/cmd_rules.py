
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from discord import app_commands
from os import getenv
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from config_manager import ConfigManager
from cogs.verification import VerificationManager
from utils.printing import create_embed_from_dict, load_embed_text, load_single_embed_text, safe_send_message

class CmdRules(commands.GroupCog, name="rule"):
    def __init__(self, bot: commands.bot, log: Logger, config: ConfigManager, verification: VerificationManager):
        super().__init__()
        self.bot = bot
        self.log = log
        self.config = config
        self.verification = verification
    
    # ============================= Rule Message Management =============================
    @app_commands.command(name="new", description="Crea un nuovo messaggio delle regole")
    async def new(self, interaction: discord.Interaction, address_channel: discord.TextChannel) -> None:
        """Crea un nuovo messaggio delle regole con embed e sistema di verifica"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel)
        channel = interaction.channel
        
        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel
        
        await self.log.command('Creazione di un nuovo messaggio', 'rule', 'NEW')
        await interaction.response.send_message('Inizio la creazione di un nuovo messaggio delle regole.', ephemeral=True)
        
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
            message_content: list = await load_embed_text(guild, 'rule', self.config)
            # Create the embed message
            rule_embed: list[discord.Embed] = [create_embed_from_dict(content) for content in message_content]
            
            # Send the message in rule channel
            rule_message: discord.Message = await address_channel.send(embeds=rule_embed)
            
            try:
                # Load the embed content
                verification_content: dict = await load_single_embed_text(guild, 'verification', self.config)
                
                # Create the embed
                verification_embed: discord.Embed = create_embed_from_dict(verification_content)
                
                # Send the embed with the reaction emoji
                verification_message: discord.Message = await address_channel.send(embed=verification_embed)
                
                # INFO Log that the message for the reaction was sent
                await self.log.command('Messaggio reazione inviato', 'rule', 'NEW')
                
                # Add the reaction
                try:
                    emoji = discord.PartialEmoji.from_str(rules_config['emoji'])
                    await verification_message.add_reaction(emoji)
                except Exception as e:
                    # EXCEPTION
                    error_message: str = f"Errore nell'aggiungere la reazione {rules_config['emoji']}: {e}"
                    await self.log.error(error_message, 'COMMAND - RULE - NEW')
                    await communication_channel.send(self.log.error_message(command='COMMAND - RULE - NEW', message=error_message))
                
                # INFO Log that reaction was added
                await self.log.command('Reazione aggiunta al messaggio', 'rule', 'NEW')
                
                # Save the data in config file
                rules_config['message_id'] = verification_message.id
                rules_config['embed_id'] = rule_message.id
                rules_config['channel_id'] = address_channel.id
                self.config.add_rules(rules_config)
                
                # Send a message to the user
                await safe_send_message(interaction, 'Messaggio creato con successo!')
                
                # INFO Log that data was saved
                await self.log.command('Dati salvati con successo', 'rule', 'NEW')
                
            except Exception as e:
                # EXCEPTION
                error_message: str = f'Errore durante la fase di invio del messaggio con reazione e aggiunta della reazione: {e}'
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
            error_message: str = f'Errore durante la creazione di un nuovo messaggio: {e}'
            await self.log.error(error_message, 'COMMAND - RULE - NEW')
            await communication_channel.send(self.log.error_message(command='COMMAND - RULE - NEW', message=error_message))

    @app_commands.command(name="reload", description="Ricarica l'embed delle regole esistente")
    async def reload(self, interaction: discord.Interaction) -> None:
        """Ricarica l'embed delle regole esistente con contenuto aggiornato"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel)
        
        await self.log.command('Ricarica dell\'embed delle regole', 'rule', 'RELOAD')
        await interaction.response.send_message('Inizio il reload dell\'embed delle regole.', ephemeral=True)
        
        try:
            # Load rules configuration
            rules_config: dict = self.config.load_rules()
            embed_id: int = rules_config.get('embed_id', 0)
            channel_id: int = rules_config.get('channel_id', 0)
            
            if not embed_id:
                error_message: str = 'Nessun embed_id trovato nella configurazione. Esegui prima /rule new.'
                await self.log.error(error_message, 'COMMAND - RULE - RELOAD')
                await safe_send_message(interaction, error_message)
                return
            
            # Find the message with the embed_id
            rule_channel = guild.get_channel(channel_id)
            if not rule_channel:
                error_message: str = 'Canale delle regole non trovato nella configurazione.'
                await self.log.error(error_message, 'COMMAND - RULE - RELOAD')
                await safe_send_message(interaction, error_message)
                return
            
            try:
                # Fetch the message using the embed_id
                rule_message: discord.Message = await rule_channel.fetch_message(embed_id)
            except discord.NotFound:
                error_message: str = f'Messaggio con ID {embed_id} non trovato nel canale delle regole.'
                await self.log.error(error_message, 'COMMAND - RULE - RELOAD')
                await safe_send_message(interaction, error_message)
                return
            except Exception as e:
                error_message: str = f'Errore nel recuperare il messaggio con ID {embed_id}: {e}'
                await self.log.error(error_message, 'COMMAND - RULE - RELOAD')
                await safe_send_message(interaction, error_message)
                return
            
            # Load new embed content
            message_content: list = await load_embed_text(guild, 'rule', self.config)
            # Create the new embed message
            new_rule_embed: list[discord.Embed] = [create_embed_from_dict(content) for content in message_content]
            
            # Edit the existing message with new embeds
            await rule_message.edit(embeds=new_rule_embed)
            
            # INFO Log successful reload
            await self.log.command('Embed delle regole ricaricato con successo', 'rule', 'RELOAD')
            await safe_send_message(interaction, 'Embed delle regole ricaricato con successo!')
            
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - RULE - RELOAD')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - RULE - RELOAD')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante il reload dell\'embed delle regole: {e}'
            await self.log.error(error_message, 'COMMAND - RULE - RELOAD')
            await safe_send_message(interaction, f"❌ {error_message}")
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - RULE - RELOAD', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - RULE - RELOAD')