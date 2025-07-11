
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ui import Modal, TextInput

class InputModal(Modal):
    def __init__(self, title: str, label: str):
        super().__init__(title=title)
        self.text_input = TextInput(
            label=label,
            placeholder="Scrivi qui...",
            required=True
        )
        self.add_item(self.text_input)
        # Response
        self.input_value: str = None
        
    async def on_submit(self, interaction: discord.Interaction):
        self.input_value = self.text_input.value
        await interaction.response.defer()