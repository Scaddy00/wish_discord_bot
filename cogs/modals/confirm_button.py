
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ui import Button
from discord import ButtonStyle

# ============================= Confirm Button =============================
class ConfirmButton(Button):
    def __init__(self, *, style = ButtonStyle.secondary, label = None, disabled = False, custom_id = None, url = None, emoji = None, row = None, sku_id = None):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row, sku_id=sku_id)
        
    async def callback(self, interaction: discord.Interaction):
        if hasattr(self.view, "author") and interaction.user.id != self.view.author.id:
            await interaction.response.send_message("Questo pulsante non ti appartiene.", ephemeral=True)
            return

        if hasattr(self.view, "values") and self.view.values:
            await interaction.response.send_message("Conferma completata con successo.", ephemeral=True)
            self.view.confirmed = True
            self.view.stop()
        else:
            await interaction.response.send_message("Non hai selezionato alcun elemento.", ephemeral=True)