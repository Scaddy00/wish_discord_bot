
# ----------------------------- Imported Libraries -----------------------------
# Third-party library imports
import discord

# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from config_manager import ConfigManager

# ============================= ADD_ROLE =============================
async def add_role(log: Logger, guild: discord.Guild, role_id: int, member_id: int, config: ConfigManager) -> None:
    """
    Add a role to a Discord member.
    
    Args:
        log (Logger): Logger instance for error logging
        guild (discord.Guild): Discord guild instance
        role_id (int): ID of the role to add
        member_id (int): ID of the member to add the role to
        config (ConfigManager): Configuration manager instance
        
    Note:
        Logs errors to both database and communication channel if operation fails.
    """
    # Load communication channel
    communication_channel = guild.get_channel(config.communication_channel)
    
    # Get the role
    role = guild.get_role(role_id)
    
    # Get the member
    member = guild.get_member(member_id)
    
    # Check if role_id is None or invalid
    if role_id is None or role_id == 0:
        error_message: str = f'Errore durante l\'aggiunta di un nuovo ruolo.\nRole ID è None o 0 per il membro {member.name if member else "Unknown"} ({member_id})'
        await log.error(error_message, 'EVENT - ROLE ASSIGN AUTO')
        if communication_channel:
            await communication_channel.send(log.error_message(command='EVENT - ROLE ASSIGN AUTO', message=error_message))
        return
    
    # Check if role exists
    if role is None:
        error_message: str = f'Errore durante l\'aggiunta di un nuovo ruolo.\nRuolo con ID {role_id} non trovato nel server per il membro {member.name if member else "Unknown"} ({member_id})'
        await log.error(error_message, 'EVENT - ROLE ASSIGN AUTO')
        if communication_channel:
            await communication_channel.send(log.error_message(command='EVENT - ROLE ASSIGN AUTO', message=error_message))
        return
    
    # Check if member exists
    if member is None:
        error_message: str = f'Errore durante l\'aggiunta di un nuovo ruolo.\nMembro con ID {member_id} non trovato nel server per il ruolo {role.name} ({role.id})'
        await log.error(error_message, 'EVENT - ROLE ASSIGN AUTO')
        if communication_channel:
            await communication_channel.send(log.error_message(command='EVENT - ROLE ASSIGN AUTO', message=error_message))
        return
    
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
        if communication_channel:
            await communication_channel.send(log.error_message(command='EVENT - ROLE ASSIGN AUTO', message=error_message))

# ============================= REMOVE_ROLE =============================
async def remove_role(log: Logger, guild: discord.Guild, role_id: int, member_id: int, config: ConfigManager) -> None:
    """
    Remove a role from a Discord member.
    
    Args:
        log (Logger): Logger instance for error logging
        guild (discord.Guild): Discord guild instance
        role_id (int): ID of the role to remove
        member_id (int): ID of the member to remove the role from
        config (ConfigManager): Configuration manager instance
        
    Note:
        Logs errors to both database and communication channel if operation fails.
    """
    # Load communication channel
    communication_channel = guild.get_channel(config.communication_channel)
    
    # Get the role
    role = guild.get_role(role_id)
    
    # Get the member
    member = guild.get_member(member_id)
    
    # Check if role_id is None or invalid
    if role_id is None or role_id == 0:
        error_message: str = f'Errore durante la rimozione di un ruolo.\nRole ID è None o 0 per il membro {member.name if member else "Unknown"} ({member_id})'
        await log.error(error_message, 'EVENT - ROLE ASSIGN AUTO')
        if communication_channel:
            await communication_channel.send(log.error_message(command='EVENT - ROLE ASSIGN AUTO', message=error_message))
        return
    
    # Check if role exists
    if role is None:
        error_message: str = f'Errore durante la rimozione di un ruolo.\nRuolo con ID {role_id} non trovato nel server per il membro {member.name if member else "Unknown"} ({member_id})'
        await log.error(error_message, 'EVENT - ROLE ASSIGN AUTO')
        if communication_channel:
            await communication_channel.send(log.error_message(command='EVENT - ROLE ASSIGN AUTO', message=error_message))
        return
    
    # Check if member exists
    if member is None:
        error_message: str = f'Errore durante la rimozione di un ruolo.\nMembro con ID {member_id} non trovato nel server per il ruolo {role.name} ({role.id})'
        await log.error(error_message, 'EVENT - ROLE ASSIGN AUTO')
        if communication_channel:
            await communication_channel.send(log.error_message(command='EVENT - ROLE ASSIGN AUTO', message=error_message))
        return
    
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
        if communication_channel:
            await communication_channel.send(log.error_message(command='EVENT - ROLE ASSIGN AUTO', message=error_message))

# ============================= ADD_ROLE_EVENT =============================
async def add_role_event(log: Logger, config: ConfigManager, guild: discord.Guild, message_id: int, emoji: discord.PartialEmoji, member_id: str) -> None:
    """
    Handle role addition event from reaction.
    
    Args:
        log (Logger): Logger instance for error logging
        config (ConfigManager): Configuration manager instance
        guild (discord.Guild): Discord guild instance
        message_id (int): ID of the message that was reacted to
        emoji (discord.PartialEmoji): Emoji that was used in the reaction
        member_id (str): ID of the member who reacted
        
    Note:
        Loads role ID from configuration based on message ID and emoji,
        then calls add_role function.
    """
    
    # Load role id
    role_id = await config.load_data('roles', str(message_id), emoji.__str__().replace(' ', ''))
    
    # Check if the role id is None
    if role_id == None:
        return
    
    # Call to the function that add the new role
    await add_role(log, guild, int(role_id), member_id, config)

# ============================= REMOVE_ROLE_EVENT =============================
async def remove_role_event(log: Logger, guild: discord.Guild, config: ConfigManager, message_id: int, emoji: discord.PartialEmoji, member_id: int) -> None:
    """
    Handle role removal event from reaction.
    
    Args:
        log (Logger): Logger instance for error logging
        guild (discord.Guild): Discord guild instance
        config (ConfigManager): Configuration manager instance
        message_id (int): ID of the message that was reacted to
        emoji (discord.PartialEmoji): Emoji that was used in the reaction
        member_id (int): ID of the member who reacted
        
    Note:
        Loads role ID from configuration based on message ID and emoji,
        then calls remove_role function.
    """
    # Load role id
    role_id = await config.load_data('roles', str(message_id), emoji.__str__().replace(' ', ''))
    
    # Check if the role id is None
    if role_id == None:
        return
    
    # Call to the function that remove the role
    await remove_role(log, guild, int(role_id), member_id, config)