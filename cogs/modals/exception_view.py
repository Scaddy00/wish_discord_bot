
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ui import View, Select, ChannelSelect, RoleSelect
from discord import SelectOption
# ----------------------------- Custom Libraries -----------------------------
from .input_modal import InputModal

# ============================= Channel View =============================
class ChannelView(View):
    def __init__(self, author: discord.User, timeout = 180):
        super().__init__(timeout=timeout)
        self.author = author
        self.values: list[int] = []
        
        self.channel_select: ChannelSelect = ChannelSelect(
            placeholder="Seleziona il canale",
            custom_id="channel_select",
            max_values=20
        )
        self.channel_select.callback = self.channel_callback
        self.add_item(self.channel_select)
    
    async def channel_callback(self, interaction: discord.Interaction) -> None:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Questa selezione non ti appartiene.", ephemeral=True)
            return
        self.values = [channel.id for channel in self.channel_select.values]
        await interaction.response.defer()

# ============================= Role View =============================
class RoleView(View):
    def __init__(self, author: discord.User, timeout = 180):
        super().__init__(timeout=timeout)
        self.author = author
        self.values: list[int] = []
        
        self.role_select: RoleSelect = RoleSelect(
            placeholder="Seleziona il ruolo",
            custom_id="role_select",
            max_values=20
        )
        self.role_select.callback = self.role_callback
        self.add_item(self.role_select)    

    async def role_callback(self, interaction: discord.Interaction) -> None:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Questa selezione non ti appartiene.", ephemeral=True)
            return
        self.values = [role.id for role in self.role_select.values]
        await interaction.response.defer()

# ============================= Setup View =============================
class SetupView(View):
    def __init__(self, author: discord.User, timeout = 180):
        super().__init__(timeout=timeout)
        self.author = author
        self.selection_complete: bool = False
        self.tag: str = None
        self.values: list[int] = []
    
    @discord.ui.select(
        placeholder="Seleziona il tipo di eccezione",
        custom_id="exception_select",
        options=[
            SelectOption(label="Canale", value="channel"),
            SelectOption(label="Ruolo", value="role")
        ]
    )
    async def exception_callback(self, interaction: discord.Interaction, selection: Select) -> None:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Questa selezione non ti appartiene.", ephemeral=True)
            return

        # Get the tag
        modal: InputModal = InputModal(
            title="Inserimento del tag",
            labels=["Inserisci il tag."]
        )
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.tag = modal.input_values[0]
        
        # Get the ids
        view = None
        if selection.values[0] == 'channel':
            view = ChannelView(author=interaction.user)
        else:
            view = RoleView(author=interaction.user)
        
        await interaction.followup.send(
            content="Seleziona ora gli elementi dal menu sottostante:",
            view=view,
            ephemeral=True
        )
        await view.wait()
        self.values = view.values
        self.selection_complete = True

