# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ui import View, Button, Modal, TextInput

class StreamerNameModal(Modal):
    """
    Modal for entering the Twitch streamer name.
    """
    def __init__(self):
        super().__init__(title="Imposta nome streamer Twitch")
        self.input_name = TextInput(label="Nome streamer", placeholder="Inserisci il nome dello streamer Twitch", required=True)
        self.add_item(self.input_name)
        self.streamer_name = None
    async def on_submit(self, interaction: discord.Interaction):
        self.streamer_name = self.input_name.value.strip()
        await interaction.response.send_message("✅ Nome streamer salvato!", ephemeral=True)

class StreamerNameView(View):
    """
    View with a button to open the StreamerNameModal for entering the streamer name.
    """
    def __init__(self, author: discord.User):
        super().__init__(timeout=180)
        self.author = author
        self.streamer_name = None
    @discord.ui.button(label="Imposta nome streamer", style=discord.ButtonStyle.primary)
    async def set_name(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Questa azione non ti appartiene.", ephemeral=True)
            return
        modal = StreamerNameModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.streamer_name = modal.streamer_name
        self.stop() 