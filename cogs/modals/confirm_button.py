
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ui import Button
from discord import ButtonStyle

# ============================= Confirm Button =============================
class ConfirmButton(Button):
    def __init__(self, *, style = ButtonStyle.secondary, label = None, disabled = False, custom_id = None, url = None, emoji = None, row = None, sku_id = None):
        super().__init__(style=style, label=label, disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, row=row, sku_id=sku_id)
        
    async def callback(self, interaction: discord.Interaction):
        """Callback per il bottone di conferma"""
        if hasattr(self.view, "author") and interaction.user.id != self.view.author.id:
            await interaction.response.send_message("Questo pulsante non ti appartiene.", ephemeral=True)
            return

        # Controlla se ci sono valori selezionati
        if hasattr(self.view, "values") and self.view.values:
            # Mostra un riepilogo delle selezioni
            selected_items = []
            for tag, channel_id in self.view.values.items():
                selected_items.append(f"• **{tag}**: <#{channel_id}>")
            
            summary = "✅ **Configurazione confermata!**\n\n" + "\n".join(selected_items)
            
            await interaction.response.send_message(summary, ephemeral=True)
            self.view.confirmed = True
            self.view.stop()
        else:
            await interaction.response.send_message("❌ Non hai selezionato alcun canale. Seleziona almeno un canale prima di confermare.", ephemeral=True)