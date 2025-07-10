
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ui import Modal, TextInput
# ----------------------------- Custom Libraries -----------------------------

class SetupModal(Modal):
    def __init__(self):
        super().__init__(title="Aggiungi un nuovo tag", timeout=180.0)
        
        self.tag_input = TextInput(
            label="TAG",
            placeholder="Scrivi qui il tag...",
            max_length=200
        )
        self.url_input = TextInput(
            label="URL immagine",
            placeholder="Scrivi qui l'URL dell'immagine...",
            max_length=500
        )
        
        self.add_item(self.tag_input)
        self.add_item(self.url_input)

    async def on_submit(self, interaction: discord.Interaction):
        self.tag = self.tag_input.value
        self.url = self.url_input.value
        
        await interaction.response.send_message("✅ Selezione confermata!", ephemeral=True)
        
        self.selection_complete = True
        self.stop()