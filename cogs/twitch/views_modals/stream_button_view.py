
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from discord.ui import View, Button

class StreamButtonView(View):
    def __init__(self, url: str, text: str = 'Guarda la live'):
        super().__init__(timeout=None)
        
        button: Button = Button(
            label=text,
            url=url,
            style=discord.ButtonStyle.link
        )
        self.add_item(button)