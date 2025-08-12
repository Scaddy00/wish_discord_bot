
# ----------------------------- Imported Libraries -----------------------------
# Standard library imports
import re
from asyncio import TimeoutError

# Third-party library imports
import discord
from discord.ext import commands
from discord import app_commands

# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from config_manager import ConfigManager
from utils.roles import add_role, remove_role
from utils.printing import safe_send_message, create_embed

class CmdRoles(commands.GroupCog, name="role"):
    """
    Role management commands to create role messages and assign/remove roles.
    """
    description: str = "Gestione messaggi ruoli e assegnazione/rimozione ruoli."

    def __init__(self, bot: commands.Bot, log: Logger, config: ConfigManager) -> None:
        super().__init__()
        self.bot: commands.Bot = bot
        self.log: Logger = log
        self.config: ConfigManager = config
        
        # Dictionary containing all commands and their descriptions
        self.commands_info = {
            "new": "Crea un nuovo messaggio per l'assegnazione automatica dei ruoli",
            "assign": "Assegna un ruolo ad un utente",
            "assign-all": "Assegna un ruolo a tutti gli utenti",
            "remove": "Rimuove un ruolo ad un utente",
            "remove-all": "Rimuove un ruolo da tutti gli utenti"
        }
    
    # ============================= Help Command =============================
    @app_commands.command(name="help", description="Mostra l'elenco dei comandi role disponibili")
    async def help(self, interaction: discord.Interaction) -> None:
        """
        Show an embed with all role commands and their descriptions.
        """
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel) if self.config.communication_channel else None
        
        try:
            # Create embed with commands info
            embed = create_embed(
                title="🎭 Comandi Role",
                description="Elenco di tutti i comandi per la gestione dei ruoli",
                color=self.bot.color,
                fields=[]
            )
            
            # Add each command to the embed
            for command_name, description in self.commands_info.items():
                embed.add_field(
                    name=f"`/role {command_name}`",
                    value=description,
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await self.log.command('Visualizzato help comandi role', 'role', 'HELP')
            
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - ROLE - HELP')
            await interaction.response.send_message(f"❌ {error_message}", ephemeral=True)
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - ROLE - HELP')
            await interaction.response.send_message(f"❌ {error_message}", ephemeral=True)
            
        except Exception as e:
            error_message: str = f'Errore durante la visualizzazione dell\'help: {e}'
            await self.log.error(error_message, 'COMMAND - ROLE - HELP')
            await interaction.response.send_message(f"❌ {error_message}", ephemeral=True)
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - ROLE - HELP', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - ROLE - HELP')
    
    # ============================= Helper Methods =============================
    
    # ============================= Role Message Management =============================
    @app_commands.command(name="new", description="Crea un nuovo messaggio per l'assegnazione automatica dei ruoli")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.cooldown(1, 10)
    async def new(self, interaction: discord.Interaction) -> None:
        """Crea un nuovo messaggio con reazioni per l'assegnazione automatica dei ruoli"""
        guild: discord.Guild = interaction.guild
        new_roles: dict = {}
        
        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel
        
        communication_channel = guild.get_channel(self.config.communication_channel)
        role_channel = guild.get_channel(self.config.role_channel)
        
        await self.log.command('Creazione di un nuovo messaggio', 'role', 'NEW')
        await interaction.response.send_message('Inizio la creazione di un nuovo messaggio per l\'assegnazione automatica dei ruoli.', ephemeral=True)

        try:
            # Request the roles
            await communication_channel.send('Inserisci l\'emoji e il ruolo seguendo il seguente esempio -> \nHai 3 minuti per completare l\'operazione.\nPer terminare l\'operazione scrivi "stop".')
            while True:
                # Get the response from the user, with a timeout of 3 minutes (180 s)
                response = await self.bot.wait_for('message', check=check, timeout=180.0)
                if response.content.lower() == 'stop':
                    break
                
                # Split the message content with the selected divider
                splitted: list = response.content.replace(' ', '').split('|')
                
                # Check if the emoji is correct
                try:
                    discord.PartialEmoji.from_str(splitted[0])
                except Exception:
                    await communication_channel.send(f"L'emoji `{splitted[0]}` non è valida. Riprova.")
                    continue
                
                # Append the emoji and the role id to the list
                # The role id is taken using a regex
                new_roles[splitted[0]] = ''.join(re.findall(r'\d+', splitted[1]))
            
            # INFO Log the status of the operation
            await self.log.command('Emoji e Ruoli inseriti', 'role', 'NEW')
            
            try:
                # Get the message
                message_str: str = 'Assegna un ruolo' # TODO Change the message with an embed
                # Send the message
                message: discord.Message = await role_channel.send(message_str)
                
                # INFO Log that the message was sent
                await self.log.command('Messaggio inviato con successo', 'role', 'NEW')
                
                for key in new_roles.keys():
                    try:
                        emoji = discord.PartialEmoji.from_str(key)
                        await message.add_reaction(emoji)
                    except Exception as e:
                        # EXCEPTION
                        error_message: str = f'Errore nell\'aggiungere la reazione {key}: {e}'
                        await self.log.error(error_message, 'COMMAND - ROLE - NEW')
                        await communication_channel.send(self.log.error_message(command='COMMAND - ROLE - NEW', message=error_message))
                
                # INFO Log that the reaction were added
                await self.log.command('Reazione aggiunte al messaggio con successo', 'role', 'NEW')
                
                try:
                    # Add the new config to the JSON file
                    await self.config.update_data(self.log, interaction.guild, new_roles, ['roles', str(message.id)])
                    
                    # INFO New config saved with success
                    await self.log.command('Dati salvati con successo nel file config.json', 'role', 'new')
                    
                    # Send a message that tell the user that's complete
                    await communication_channel.send('Lavorazione completata! Il messaggio è stato creato')
                    
                    # INFO Log that the process is complete
                    await self.log.command('Lavorazione completata', 'role', 'new')
                    
                except Exception as e:
                    # EXCEPTION
                    error_message: str = f'Errore durante la creazione di un nuovo messaggio: {e}'
                    await self.log.error(error_message, 'COMMAND - ROLE - NEW')
                    await communication_channel.send(self.log.error_message(command='COMMAND - ROLE - NEW', message=error_message))
                
            except Exception as e:
                # EXCEPTION
                error_message: str = f'Errore durante l\'invio del nuovo messaggio: {e}'
                await self.log.error(error_message, 'COMMAND - ROLE - NEW')
                await communication_channel.send(self.log.error_message(command='COMMAND - ROLE - NEW', message=error_message))
            
        except TimeoutError:
            await communication_channel.send('Tempo scaduto. Lavorazione interrotta!')
            # EXCEPTION
            error_message: str = 'Tempo scaduto durante la creazione di un nuovo messaggio.'
            await self.log.error(error_message, 'COMMAND - ROLE - NEW')
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante la creazione di un nuovo messaggio: {e}'
            await self.log.error(error_message, 'COMMAND - ROLE - NEW')
            await communication_channel.send(self.log.error_message(command='COMMAND - ROLE - NEW', message=error_message))
        
    # ============================= Role Assignment =============================
    @app_commands.command(name="assign", description="Assegna un ruolo ad un utente")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.cooldown(1, 5)
    async def assign(self, interaction: discord.Interaction, role: discord.Role, user: discord.Member) -> None:
        """Assegna un ruolo specifico ad un utente"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel)
        
        try:
            if role not in user.roles:
                await add_role(self.log, interaction.guild, role.id, user.id, self.config)
                # Respond that the role was assigned correctly
                await safe_send_message(interaction, f'Ruolo {role.mention} assegnato correttamente a {user.mention}!')
                # INFO Log that the role was assigned correctly
                await self.log.command(f'Ruolo {role.name} ({role.id}) assegnato correttamente a {user.name} ({user.id})', 'role', 'assign')
            else:
                await safe_send_message(interaction, f'L\'utente {user.mention} ha già il ruolo {role.mention}!')
                
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - ROLE - ASSIGN')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - ROLE - ASSIGN')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante l\'assegnazione del ruolo: {e}'
            await self.log.error(error_message, 'COMMAND - ROLE - ASSIGN')
            await safe_send_message(interaction, f"❌ {error_message}")
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - ROLE - ASSIGN', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - ROLE - ASSIGN')

    @app_commands.command(name="assign-all", description="Assegna un ruolo a tutti gli utenti")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.cooldown(1, 30)
    async def assign_all(self, interaction: discord.Interaction, role: discord.Role) -> None:
        """Assegna un ruolo a tutti gli utenti del server (escludendo quelli con ruoli di eccezione)"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel)
        
        # Get the member list
        members: list[discord.Member] = interaction.guild.members
        # Get the exception role list
        except_roles: list = await self.config.load_exception('cmd-role')
        
        counter: int = 0
        try:
            for member in members:
                # Check if member has an exception role
                for except_role in except_roles:
                    if except_role in member.roles:
                        return
                
                if role not in member.roles:
                    await add_role(self.log, interaction.guild, role.id, member.id, self.config)
                    # INFO Log that the role was assigned correctly
                    await self.log.command(f'Ruolo {role.name} ({role.id}) assegnato correttamente a {member.name} ({member.id})', 'role', 'assign-all')
                    counter += 1
            
            # Respond that how many roles were assigned
            await safe_send_message(interaction, f'Ruolo {role.mention} assegnato a {counter} utenti!')
            # INFO Log that the role was assigned correctly to all the members
            await self.log.command(f'Ruolo {role.name} ({role.id}) assegnato correttamente a {counter} utenti.', 'role', 'assign-all')
            
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - ROLE - ASSIGN-ALL')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - ROLE - ASSIGN-ALL')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante l\'assegnazione del ruolo: {e}'
            await self.log.error(error_message, 'COMMAND - ROLE - ASSIGN-ALL')
            await safe_send_message(interaction, f"❌ {error_message}")
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - ROLE - ASSIGN-ALL', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - ROLE - ASSIGN-ALL')

    # ============================= Role Removal =============================
    @app_commands.command(name="remove", description="Rimuove un ruolo ad un utente")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.cooldown(1, 5)
    async def remove(self, interaction: discord.Interaction, role: discord.Role, user: discord.Member) -> None:
        """Rimuove un ruolo specifico da un utente"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel)
        
        try:
            if role in user.roles:
                await remove_role(self.log, interaction.guild, role.id, user.id, self.config)
                # Respond that the role was removed correctly
                await safe_send_message(interaction, f'Ruolo {role.mention} rimosso correttamente da {user.mention}!')
                # INFO Log that the role was removed correctly
                await self.log.command(f'Ruolo {role.name} ({role.id}) rimosso correttamente da {user.name} ({user.id})', 'role', 'remove')
            else:
                await safe_send_message(interaction, f'L\'utente {user.mention} non ha il ruolo {role.mention}!')
                
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - ROLE - REMOVE')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - ROLE - REMOVE')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante la rimozione del ruolo: {e}'
            await self.log.error(error_message, 'COMMAND - ROLE - REMOVE')
            await safe_send_message(interaction, f"❌ {error_message}")
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - ROLE - REMOVE', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - ROLE - REMOVE')

    @app_commands.command(name="remove-all", description="Rimuove un ruolo da tutti gli utenti")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.cooldown(1, 30)
    async def remove_all(self, interaction: discord.Interaction, role: discord.Role) -> None:
        """Rimuove un ruolo da tutti gli utenti del server (escludendo quelli con ruoli di eccezione)"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel)
        
        # Get the member list
        members: list[discord.Member] = interaction.guild.members
        # Get the exception role list
        except_roles: list = await self.config.load_exception('cmd-role')
        
        counter: int = 0
        try:
            for member in members:
                # Check if member has an exception role
                for except_role in except_roles:
                    if except_role in member.roles:
                        return
                
                if role in member.roles:
                    await remove_role(self.log, interaction.guild, role.id, member.id, self.config)
                    # INFO Log that the role was removed correctly
                    await self.log.command(f'Ruolo {role.name} ({role.id}) rimosso correttamente da {member.name} ({member.id})', 'role', 'remove-all')
                    counter += 1
            
            # Respond that how many roles were removed
            await safe_send_message(interaction, f'Ruolo {role.mention} rimosso da {counter} utenti!')
            # INFO Log that the role was removed correctly from all the members
            await self.log.command(f'Ruolo {role.name} ({role.id}) rimosso correttamente da {counter} utenti.', 'role', 'remove-all')
            
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - ROLE - REMOVE-ALL')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - ROLE - REMOVE-ALL')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante la rimozione del ruolo: {e}'
            await self.log.error(error_message, 'COMMAND - ROLE - REMOVE-ALL')
            await safe_send_message(interaction, f"❌ {error_message}")
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - ROLE - REMOVE-ALL', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - ROLE - REMOVE-ALL')