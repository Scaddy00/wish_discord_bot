# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ui import View, Button, Modal, TextInput

class TwitchTitlesModal(Modal):
    """
    Modal for entering both Twitch titles: 'on' (live) and 'off' (not live).
    """
    def __init__(self):
        super().__init__(title="Imposta titoli Twitch")
        self.input_on = TextInput(label="Titolo ON", placeholder="Titolo per live attiva", required=True)
        self.input_off = TextInput(label="Titolo OFF", placeholder="Titolo per live non attiva", required=True)
        self.add_item(self.input_on)
        self.add_item(self.input_off)
        self.titles = {}

    async def on_submit(self, interaction: discord.Interaction):
        self.titles = {
            'on': self.input_on.value.strip(),
            'off': self.input_off.value.strip()
        }
        await interaction.response.send_message("✅ Titoli Twitch salvati!", ephemeral=True)

class TwitchTitlesView(View):
    """
    View with a button to open the TwitchTitlesModal for entering both titles.
    """
    def __init__(self, author: discord.User):
        super().__init__(timeout=180)
        self.author = author
        self.titles = {}

    @discord.ui.button(label="Imposta titoli Twitch", style=discord.ButtonStyle.primary)
    async def set_titles(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Questa azione non ti appartiene.", ephemeral=True)
            return
        modal = TwitchTitlesModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.titles = modal.titles
        self.stop() 