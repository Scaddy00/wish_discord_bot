# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ui import Modal, TextInput

class SetupTitleByTagModal(Modal):
    """
    Modal for entering a Twitch title for a specific tag ('on' or 'off').
    """
    def __init__(self, tag: str):
        super().__init__(title=f"Imposta titolo Twitch: {tag.upper()}")
        self.tag = tag
        self.input_title = TextInput(
            label=f"Titolo per '{tag}'",
            placeholder=f"Inserisci il titolo per '{tag}'",
            required=True
        )
        self.add_item(self.input_title)
        self.title_value = None

    async def on_submit(self, interaction: discord.Interaction):
        self.title_value = self.input_title.value.strip()
        await interaction.response.send_message(f"✅ Titolo '{self.tag}' salvato!", ephemeral=True) 