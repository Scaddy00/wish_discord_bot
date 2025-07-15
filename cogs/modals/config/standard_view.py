
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ui import View, ChannelSelect
# ----------------------------- Custom Libraries -----------------------------
from cogs.modals.confirm_button import ConfirmButton

# ============================= Setup View =============================
class SetupView(View):
    def __init__(self, author: discord.User, tags: list[str], timeout = 180):
        super().__init__(timeout=timeout)
        self.author = author
        self.values: dict = {}
        
        self.select_channels: list[ChannelSelect] = []
        
        counter: int = 0
        for tag in tags:
            self.select_channels.append(ChannelSelect(
                placeholder=f"Seleziona il canale per la sezione {tag}",
                custom_id=f"select_channel_{tag}",
                channel_types=[discord.ChannelType.text]
            ))
            self.select_channels[counter].callback = self.select_channel_callback
            self.add_item(self.select_channels[counter])
            counter += 1
        
        self.confirm_button = ConfirmButton(
            label="Conferma",
            custom_id="confirm_button",
            style=discord.ButtonStyle.green
        )
        self.add_item(self.confirm_button)
    
    async def select_channel_callback(self, interaction: discord.Interaction) -> None:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Questa selezione non ti appartiene.", ephemeral=True)
            return
        
        tag = interaction.data['custom_id'].split('_', 2)[-1]
        selected_channel_id = int(interaction.data['values'][0])
        self.values[tag] = selected_channel_id
        await interaction.response.defer(ephemeral=True)
        
