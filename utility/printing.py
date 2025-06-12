
# ----------------------------- Standard library -----------------------------
from datetime import datetime
from os import getenv
from discord import Embed

# ============================= Datetime format =============================
def format_datetime_now() -> str:
    str_format: str = str(getenv('DATETIME_FORMAT'))
    return datetime.now().strftime(str_format)

# ============================= Embed creator =============================
def create_embed(title: str, description: str, color: int, url: str | None = None, fields: list = [], footer: dict = {}, thumbnail: str = '', image: str = '') -> Embed:
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
                         type='rich',
                         description=description,
                         color=color,
                         url=url,
                         )
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