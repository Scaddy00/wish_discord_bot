
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ui import View, Select, ChannelSelect, RoleSelect, Button
from discord import SelectOption, ButtonStyle
# ----------------------------- Custom Libraries -----------------------------
from cogs.modals.input_modal import InputModal
from cogs.modals.channel_view import ChannelView
from cogs.modals.role_view import RoleView

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

