
# ----------------------------- Imported Libraries -----------------------------
import discord
from os import getenv
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from .config import load_data

# ============================= ADD_ROLE =============================
async def add_role(log: Logger, guild: discord.Guild, role_id: int, member_id: int) -> None:
    # Load communication channel
    communication_channel = guild.get_channel(int(getenv('BOT_COMMUNICATION_CHANNEL_ID')))
    
    # Get the role
    role = guild.get_role(role_id)
    
    # Get the member
    member = guild.get_member(member_id)
    
    try:
        # Check if the member already has the role
        if role in member.roles:
            return
        
        # Add the new role to the member
        await member.add_roles(role)
        # INFO LOG
        await log.event(f'Nuovo ruolo aggiunto ad un utente.\n{member.name} ({member.id}) - {role.name} ({role.id})', 'role-assign-auto')
    except Exception as e:
        # EXCEPTION
        error_message: str = f'Errore durante l\'aggiunta di un nuovo ruolo.\n{member.name} ({member.id}) - {role.name} ({role.id})\n{e}'
        await log.error(error_message, 'EVENT - ROLE ASSIGN AUTO')
        await communication_channel.send(log.error_message(command='EVENT - ROLE ASSIGN AUTO', message=error_message))

# ============================= REMOVE_ROLE =============================
async def remove_role(log: Logger, guild: discord.Guild, role_id: int, member_id: int) -> None:
    # Load communication channel
    communication_channel = guild.get_channel(int(getenv('BOT_COMMUNICATION_CHANNEL_ID')))
    
    # Get the role
    role = guild.get_role(role_id)
    
    # Get the member
    member = guild.get_member(member_id)
    
    try:
        # Check if the member hasn't the role
        if role not in member.roles:
            return
        
        # Remove the role from the member
        await member.remove_roles(role)
        # INFO LOG
        await log.event(f'Ruolo rimosso ad un utente.\n{member.name} ({member.id}) - {role.name} ({role.id})', 'role-assign-auto')
    except Exception as e:
        # EXCEPTION
        error_message: str = f'Errore durante la rimozione di un ruolo.\n{member.name} ({member.id}) - {role.name} ({role.id})\n{e}'
        await log.error(error_message, 'EVENT - ROLE ASSIGN AUTO')
        await communication_channel.send(log.error_message(command='EVENT - ROLE ASSIGN AUTO', message=error_message))

# ============================= ADD_ROLE_EVENT =============================
async def add_role_event(log: Logger, guild: discord.Guild, message_id: int, emoji: discord.PartialEmoji, member_id: str) -> None:
    
    # Load role id
    role_id = await load_data(log, guild, 'EVENT - ROLE ASSIGN AUTO', 'roles', str(message_id), emoji.__str__().replace(' ', ''))
    
    # Check if the role id is None
    if role_id == None:
        return
    
    # Call to the function that add the new role
    await add_role(log, guild, int(role_id), member_id)

# ============================= REMOVE_ROLE_EVENT =============================
async def remove_role_event(log: Logger, guild: discord.Guild, message_id: int, emoji: discord.PartialEmoji, member_id: int) -> None:
    # Load role id
    role_id = await load_data(log, guild, 'EVENT - ROLE ASSIGN AUTO', 'roles', str(message_id), emoji.__str__().replace(' ', ''))
    
    # Check if the role id is None
    if role_id == None:
        return
    
    # Call to the function that remove the role
    await remove_role(log, guild, int(role_id), member_id)