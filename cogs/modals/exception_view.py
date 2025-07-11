
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ui import View, Select, ChannelSelect, RoleSelect, Button
from discord import SelectOption, ButtonStyle
# ----------------------------- Custom Libraries -----------------------------
from .input_modal import InputModal

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

# ============================= Channel View =============================
class ChannelView(View):
    def __init__(self, author: discord.User, timeout = 180):
        super().__init__(timeout=timeout)
        self.author = author
        self.values: list[int] = []
        self.confirmed: bool = False
        
        self.channel_select: ChannelSelect = ChannelSelect(
            placeholder="Seleziona il canale",
            custom_id="channel_select",
            max_values=20
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

# ============================= Role View =============================
class RoleView(View):
    def __init__(self, author: discord.User, timeout = 180):
        super().__init__(timeout=timeout)
        self.author = author
        self.values: list[int] = []
        self.confirmed: bool = False
        
        self.role_select: RoleSelect = RoleSelect(
            placeholder="Seleziona il ruolo",
            custom_id="role_select",
            max_values=20
        )
        self.role_select.callback = self.role_callback
        self.add_item(self.role_select)    
        self.add_item(ConfirmButton(label="Conferma", style=ButtonStyle.success))

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
        self.type: str = None
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

        # Save selected type
        self.type = selection.values[0].capitalize()
        
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

        if not view.confirmed:
            await interaction.followup.send("Operazione annullata o nessuna conferma ricevuta.", ephemeral=True)
            return

        self.values = view.values
        self.selection_complete = True
        self.stop()

