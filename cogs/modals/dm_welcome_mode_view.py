
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ui import View, Button
from discord import ButtonStyle

# ============================= DM Welcome Mode View =============================
class DmWelcomeModeView(View):
    def __init__(self, author: discord.User, timeout: int = 180):
        super().__init__(timeout=timeout)
        self.author = author
        self.confirmed: bool = False
        self.selected_mode: str | None = None  # "user" or "bulk"

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Questa azione non ti appartiene.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Invia a utente", style=ButtonStyle.primary, custom_id="dm_welcome_user_btn")
    async def choose_user(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Questa azione non ti appartiene.", ephemeral=True)
            return
        self.selected_mode = "user"
        self.confirmed = True
        await interaction.response.send_message("Modalità selezionata: utente.", ephemeral=True)
        self.stop()

    @discord.ui.button(label="Invia a non verificati", style=ButtonStyle.secondary, custom_id="dm_welcome_bulk_btn")
    async def choose_bulk(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Questa azione non ti appartiene.", ephemeral=True)
            return
        self.selected_mode = "bulk"
        self.confirmed = True
        await interaction.response.send_message("Modalità selezionata: non verificati.", ephemeral=True)
        self.stop()


