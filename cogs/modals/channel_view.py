
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ui import View, ChannelSelect
from discord import ButtonStyle
# ----------------------------- Imported Libraries -----------------------------
from .confirm_button import ConfirmButton

# ============================= Channel View =============================
class ChannelView(View):
    def __init__(self, author: discord.User, min_values = 0, max_values = 40, timeout = 180):
        super().__init__(timeout=timeout)
        self.author = author
        self.values: list[int] = []
        self.confirmed: bool = False
        
        self.channel_select: ChannelSelect = ChannelSelect(
            placeholder="Seleziona il canale",
            custom_id="channel_select",
            min_values=min_values,
            max_values=max_values
        )
        self.channel_select.callback = self.channel_callback
        self.add_item(self.channel_select)
        self.add_item(ConfirmButton(label="Conferma", style=ButtonStyle.success))
        
    async def channel_callback(self, interaction: discord.Interaction) -> None:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Questa selezione non ti appartiene.", ephemeral=True)
            return
        self.values = [channel.id for channel in self.channel_select.values]
        await interaction.response.defer()