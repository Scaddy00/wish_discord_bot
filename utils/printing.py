
# ----------------------------- Standard library -----------------------------
from datetime import datetime
from os import getenv
from discord import Embed
import discord
from os import path
# ----------------------------- Custom Libraries -----------------------------
from .file_io import read_file

italian_month: list = ["", "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]

# ============================= Format Datetime Now =============================
def format_datetime_now() -> str:
    str_format: str = str(getenv('DATETIME_FORMAT'))
    return datetime.now().strftime(str_format)

# ============================= Format Datetime Now Extended =============================
def format_datetime_now_extended() -> str:
    converted_datetime: datetime = datetime.now()
    return converted_datetime.strftime(f"%H:%M %d {italian_month[converted_datetime.month]} %Y")

# ============================= Format Datetime Extended =============================
def format_datetime_extended(time: str) -> str:
    converted_datetime: datetime = datetime.fromisoformat(time)
    return converted_datetime.strftime(f"%H:%M %d {italian_month[converted_datetime.month]} %Y")

# ============================= Embed data load =============================
async def load_embed_text(guild: discord.Guild, item: str, config) -> list[dict]:
    # Load communication channel
    communication_channel = guild.get_channel(config.communication_channel)
    
    # Load embed text file
    embed_text_path: str = path.join(str(getenv('DATA_PATH')), str(getenv('EMBED_TEXT_FILE_NAME')))
    text: dict = read_file(embed_text_path)
    
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