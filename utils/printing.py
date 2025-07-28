
# ----------------------------- Standard library -----------------------------
from datetime import datetime, timezone
from os import getenv
from discord import Embed
import discord
from os import path
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from .file_io import read_file

italian_month: list = ["", "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]

# ============================= Safe Send Message =============================
async def safe_send_message(interaction: discord.Interaction, message: str = None, ephemeral: bool = True, embed: discord.Embed = None, logger: Logger = None, log_command: str = "SAFE-SEND") -> None:
    """
    Safely send a message to the interaction, handling webhook errors.
    
    Args:
        interaction (discord.Interaction): The Discord interaction to respond to
        message (str, optional): The message to send. Defaults to None.
        ephemeral (bool, optional): Whether the message should be ephemeral. Defaults to True.
        embed (discord.Embed, optional): The embed to send. Defaults to None.
        logger: Logger instance for error logging. Defaults to None.
        log_command (str, optional): Command name for logging. Defaults to "SAFE-SEND".
    """
    try:
        if embed:
            await interaction.followup.send(embed=embed, ephemeral=ephemeral)
        else:
            await interaction.followup.send(message, ephemeral=ephemeral)
    except discord.NotFound:
        # If webhook is invalid, try to send a new response
        try:
            if embed:
                await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
            else:
                await interaction.response.send_message(message, ephemeral=ephemeral)
        except Exception as e:
            # If even that fails, just log the error
            if logger:
                await logger.error(f'Impossibile inviare messaggio all\'utente: {e}', log_command)
            else:
                print(f'SAFE-SEND ERROR: Impossibile inviare messaggio all\'utente: {e}')

# ============================= Format Datetime Now =============================
def format_datetime_now() -> str:
    """
    Get current datetime formatted according to DATETIME_FORMAT environment variable.
    
    Returns:
        str: Current datetime in the specified format
    """
    str_format: str = str(getenv('DATETIME_FORMAT'))
    return datetime.now().strftime(str_format)

# ============================= Format Datetime Now Extended =============================
def format_datetime_now_extended() -> str:
    """
    Get current datetime in extended Italian format.
    
    Returns:
        str: Current datetime in format "HH:MM DD month YYYY" (Italian)
    """
    converted_datetime: datetime = datetime.now()
    return converted_datetime.strftime(f"%H:%M %d {italian_month[converted_datetime.month]} %Y")

# ============================= Format Datetime Extended =============================
def format_datetime_extended(time: str) -> str:
    """
    Convert ISO format datetime string to extended Italian format.
    
    Args:
        time (str): ISO format datetime string (UTC timezone)
        
    Returns:
        str: Datetime in format "HH:MM DD month YYYY" (Italian, local timezone)
    """
    # Parse the ISO format string and handle timezone properly
    if time.endswith('Z'):
        # Remove 'Z' and parse as UTC
        utc_time = time[:-1]
        converted_datetime: datetime = datetime.fromisoformat(utc_time).replace(tzinfo=timezone.utc)
    else:
        # Parse as is (assuming it's already in the correct timezone)
        converted_datetime: datetime = datetime.fromisoformat(time)
    
    # Convert to local timezone
    local_datetime = converted_datetime.astimezone()
    return local_datetime.strftime(f"%H:%M %d {italian_month[local_datetime.month]} %Y")

# ============================= Embed data load =============================
async def load_embed_text(guild: discord.Guild, item: str, config) -> list[dict]:
    """
    Load embed text data from the embed_text.json file.
    
    Args:
        guild (discord.Guild): Discord guild instance
        item (str): Key to look up in the embed text file
        config: Configuration manager instance
        
    Returns:
        list[dict]: List of embed data dictionaries, or empty list if item not found
    """
    # Load communication channel
    communication_channel = guild.get_channel(config.communication_channel)
    
    # Load embed text file
    embed_text_path: str = path.join(str(getenv('DATA_PATH')), str(getenv('EMBED_TEXT_FILE_NAME')))
    text: dict = read_file(embed_text_path)
    
    # Check if text was loaded successfully
    if not text:
        await communication_channel.send(f'Errore nel caricamento del file embed_text.json. Verificare che il file esista e sia valido.')
        return []
    
    if item not in text:
        await communication_channel.send(f'L\'elemento "{item}" non è presente nel file embed_text.json.')
        return []

    data: list | dict = text[item]
    
    # Return the content if is already a list
    if isinstance(data, list):
        return data
    elif isinstance(data, dict): # Make the content a list and return it
        return [data]

# ============================= Embed data load (SINGLE) =============================
async def load_single_embed_text(guild: discord.Guild, item: str, config) -> dict:
    """
    Load a single embed text data item from the embed_text.json file.
    
    Args:
        guild (discord.Guild): Discord guild instance
        item (str): Key to look up in the embed text file
        config: Configuration manager instance
        
    Returns:
        dict: Single embed data dictionary, or empty dict if item not found
    """
    embeds = await load_embed_text(guild, item, config)
    return embeds[0] if embeds else {}

# ============================= Embed creator =============================
def create_embed(title: str, description: str, color: str, url: str | None = None, fields: list = [], footer: dict = {}, thumbnail: str = '', image: str = '') -> Embed:
    """Function for creating Discord Embeds

    Args:
        title (str): Title of the embed
        description (str): Description of the embed
        color (int): Color of the embed. Color format ...
        url (str | None, optional): Insert a url in the embed. Defaults to None.
        fields (list, optional): A list of fields. Defaults to [].
        footer (dict, optional): Footer of the embed. Defaults to {}.
        thumbnail (str, optional): Thumbnail url of the embed. Defaults to ''.
        image (str, optional): Image url of the embed. Defaults to ''.

    Returns:
        Embed: _description_
    """
    
    # Create the embed with the standard information
    embed: Embed = Embed(title=title,
                         description=description,
                         color=discord.Colour.from_str(color),
                         url=url)
    # Add fields to the embed
    if len(fields) > 0:
        for field in fields:
            embed.add_field(name=field['name'],
                            value=field['value'],
                            inline=field['inline'])
    # Add footer to the embed
    if footer:
        embed.set_footer(text=footer['text'],
                         icon_url=footer['icon_url'])
    # Add thumbnail to the embed
    if thumbnail != '':
        embed.set_thumbnail(url=thumbnail)
    # Add image to the embed
    if image != '':
        embed.set_image(url=image)

    return embed

# ============================= Embed creator (DICT) =============================
def create_embed_from_dict(data: dict) -> Embed:
    """
    Create a Discord embed from a dictionary of embed data.
    
    Args:
        data (dict): Dictionary containing embed configuration
        
    Returns:
        Embed: Discord embed object with the specified configuration
        
    Note:
        Handles missing or None values gracefully by providing defaults.
    """
    # Ensure data is not None and provide defaults for all required fields
    if not data:
        data = {}
    
    # Create the embed with the standard information
    embed: Embed = Embed(
        title=data.get('title', '') or '',
        description=data.get('description', '') or '',
        color=discord.Colour.from_str(data.get('color', '0x000000')),
        url=data.get('url', None) or None
    )
    # Add fields to the embed
    if 'fields' in data and data['fields']:
        for field in data['fields']:
            embed.add_field(
                name=field.get('name', '') or '',
                value=field.get('value', '') or '',
                inline=field.get('inline', True)
            )
    # Add footer to the embed
    if 'footer' in data and data['footer']:
        footer = data['footer']
        embed.set_footer(
            text=footer.get('text', '') or '',
            icon_url=footer.get('icon_url', '') or None
        )
    # Add thumbnail to the embed
    if data.get('thumbnail'):
        embed.set_thumbnail(url=data.get('thumbnail', '') or '')
    # Add image to the embed
    if data.get('image'):
        embed.set_image(url=data.get('image', '') or '')

    return embed