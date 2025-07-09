
# ----------------------------- Imported Libraries -----------------------------
import discord, re
from discord.ext import commands
from discord import app_commands
from os import getenv
from asyncio import TimeoutError
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from utils.config import update_data, load_exception, add_exception
from utils.roles import add_role, remove_role

class CmdRoles(commands.GroupCog, name="role"):
    def __init__(self, bot: discord.Client, log: Logger):
        super().__init__()
        self.bot = bot
        self.log = log
    
    # ============================= NEW =============================
    @app_commands.command(name="new", description="Crea un nuovo messaggio")
    async def new(self, interaction: discord.Interaction) -> None:
        # Set the default var
        new_roles: dict = {}
        
        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel
        
        # Load communication channel
        communication_channel = self.bot.get_channel(int(getenv('BOT_COMMUNICATION_CHANNEL_ID')))
        # Load role channel
        role_channel = self.bot.get_channel(int(getenv('ROLE_CHANNEL_ID')))
        # Get the channel where the interaction started
        channel = interaction.channel
        
        # INFO Log the start of the creation of the message
        await self.log.command('Creazione di un nuovo messaggio', 'role', 'NEW')
        
        # Send a response message
        await interaction.response.send_message('Inizio la creazione di un nuovo messaggio per l\'assegnazione automatica dei ruoli.')

        try:
            # Request the roles
            await channel.send('Inserisci l\'emoji e il ruolo seguendo il seguente esempio -> \nHai 3 minuti per completare l\'operazione.\nPer terminare l\'operazione scrivi "stop".')
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
                    await channel.send(f"L'emoji `{splitted[0]}` non è valida. Riprova.")
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
                        error_message: str = f'Errore nell\'aggiungere la reazione {key}\n{e}'
                        await self.log.error(error_message, 'COMMAND - ROLE - NEW')
                        await communication_channel.send(self.log.error_message(command='COMMAND - ROLE - NEW', message=error_message))
                
                # INFO Log that the reaction were added
                await self.log.command('Reazione aggiunte al messaggio con successo', 'role', 'NEW')
                
                try:
                    # Add the new config to the JSON file
                    await update_data(self.log, interaction.guild, new_roles, ['roles', str(message.id)])
                    
                    # INFO New config saved with success
                    await self.log.command('Dati salvati con successo nel file config.json', 'role', 'new')
                    
                    # Send a message that tell the user that's complete
                    await channel.send('Lavorazione completata! Il messaggio è stato creato')
                    
                    # INFO Log that the process is complete
                    await self.log.command('Lavorazione completata', 'role', 'new')
                    
                except Exception as e:
                    # EXCEPTION
                    error_message: str = f'Errore durante la creazione di un nuovo messaggio.\n{e}'
                    await self.log.error(error_message, 'COMMAND - ROLE - NEW')
                    await communication_channel.send(self.log.error_message(command='COMMAND - ROLE - NEW', message=error_message))
                
            except Exception as e:
                # EXCEPTION
                error_message: str = f'Errore durante l\'invio del nuovo messaggio.\n{e}'
                await self.log.error(error_message, 'COMMAND - ROLE - NEW')
                await communication_channel.send(self.log.error_message(command='COMMAND - ROLE - NEW', message=error_message))
            
        except TimeoutError:
            await channel.send('Tempo scaduto. Lavorazione interrotta!')
            # EXCEPTION
            error_message: str = 'Tempo scaduto durante la creazione di un nuovo messaggio.'
            await self.log.error(error_message, 'COMMAND - ROLE - NEW')
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante la creazione di un nuovo messaggio.\n{e}'
            await self.log.error(error_message, 'COMMAND - ROLE - NEW')
            await communication_channel.send(self.log.error_message(command='COMMAND - ROLE - NEW', message=error_message))
        
    # ============================= ASSIGN =============================
    @app_commands.command(name="assign", description="Assegna un ruolo ad un utente")
    async def assign(self, interaction: discord.Interaction, role: discord.Role, user: discord.Member) -> None:
        # Load communication channel
        communication_channel = self.bot.get_channel(int(getenv('BOT_COMMUNICATION_CHANNEL_ID')))
        
        try:
            if role not in user.roles:
                await add_role(self.log, interaction.guild, role.id, user.id)
                # Respond that the role was assigned correctly
                await interaction.response.send_message(f'Ruolo {role.mention} assegnato correttamente a {user.mention}!')
                # INFO Log that the role was assigned correctly
                await self.log.command(f'Ruolo {role.name} ({role.id}) assegnato correttamente a {user.name} ({user.id})', 'role', 'assign')
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante la l\'assegnazione del ruolo.\n{e}'
            await self.log.error(error_message, 'COMMAND - ROLE - ASSIGN')
            await communication_channel.send(self.log.error_message(command='COMMAND - ROLE - ASSIGN', message=error_message))

    # ============================= ASSIGN ALL =============================
    @app_commands.command(name="assign-all", description="Assegna un ruolo a tutti gli utenti")
    async def assign_all(self, interaction: discord.Interaction, role: discord.Role) -> None:
        # Load communication channel
        communication_channel = self.bot.get_channel(int(getenv('BOT_COMMUNICATION_CHANNEL_ID')))
        
        # Get the member list
        members: list[discord.Member] = interaction.guild.members
        # Get the exception role list
        except_roles: list = await load_exception('cmd-role')
        
        counter: int = 0
        try:
            for member in members:
                # Check if member has an exception role
                for except_role in except_roles:
                    if except_role in member.roles:
                        return
                
                if role not in member.roles:
                    await add_role(self.log, interaction.guild, role.id, member.id)
                    # INFO Log that the role was assigned correctly
                    await self.log.command(f'Ruolo {role.name} ({role.id}) assegnato correttamente a {member.name} ({member.id})', 'role', 'assign-all')
                    counter += 1
            
            # Respond that how many roles were assigned
            await interaction.response.send_message(f'Ruolo {role.mention} assegnato a {counter} utenti!')
            # INFO Log that the role was assigned correctly to all the members
            await self.log.command(f'Ruolo {role.name} ({role.id}) assegnato correttamente a {counter} utenti.', 'role', 'assign-all')
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante la l\'assegnazione del ruolo.\n{e}'
            await self.log.error(error_message, 'COMMAND - ROLE - ASSIGN-ALL')
            await communication_channel.send(self.log.error_message(command='COMMAND - ROLE - ASSIGN-ALL', message=error_message))

    # ============================= REMOVE =============================
    @app_commands.command(name="remove", description="Rimuove un ruolo ad un utente")
    async def remove(self, interaction: discord.Interaction, role: discord.Role, user: discord.Member) -> None:
        # Load communication channel
        communication_channel = self.bot.get_channel(int(getenv('BOT_COMMUNICATION_CHANNEL_ID')))
        
        try:
            if role in user.roles:
                await remove_role(self.log, interaction.guild, role.id, user.id)
                # Respond that the role was removed correctly
                await interaction.response.send_message(f'Ruolo {role.mention} rimosso correttamente da {user.mention}!')
                # INFO Log that the role was removed correctly
                await self.log.command(f'Ruolo {role.name} ({role.id}) rimosso correttamente da {user.name} ({user.id})', 'role', 'remove')
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante la la rimozione del ruolo.\n{e}'
            await self.log.error(error_message, 'COMMAND - ROLE - REMOVE')
            await communication_channel.send(self.log.error_message(command='COMMAND - ROLE - REMOVE', message=error_message))

    # ============================= REMOVE ALL =============================
    @app_commands.command(name="remove-all", description="Rimuove un ruolo da tutti gli utenti")
    async def remove_all(self, interaction: discord.Interaction, role: discord.Role) -> None:
        # Load communication channel
        communication_channel = self.bot.get_channel(int(getenv('BOT_COMMUNICATION_CHANNEL_ID')))
        
        # Get the member list
        members: list[discord.Member] = interaction.guild.members
        # Get the exception role list
        except_roles: list = await load_exception('cmd-role')
        
        counter: int = 0
        try:
            for member in members:
                # Check if member has an exception role
                for except_role in except_roles:
                    if except_role in member.roles:
                        return
                
                if role in member.roles:
                    await remove_role(self.log, interaction.guild, role.id, member.id)
                    # INFO Log that the role was removed correctly
                    await self.log.command(f'Ruolo {role.name} ({role.id}) rimosso correttamente da {member.name} ({member.id})', 'role', 'remove-all')
                    counter += 1
            
            # Respond that how many roles were removed
            await interaction.response.send_message(f'Ruolo {role.mention} rimosso da {counter} utenti!')
            # INFO Log that the role was removed correctly from all the members
            await self.log.command(f'Ruolo {role.name} ({role.id}) rimosso correttamente da {counter} utenti.', 'role', 'remove-all')
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante la la rimozione del ruolo.\n{e}'
            await self.log.error(error_message, 'COMMAND - ROLE - REMOVE-ALL')
            await communication_channel.send(self.log.error_message(command='COMMAND - ROLE - REMOVE-ALL', message=error_message))