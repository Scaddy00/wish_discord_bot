
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ui import View, Select
from discord import SelectOption
# ----------------------------- Custom Libraries -----------------------------
from cogs.modals.input_modal import InputModal
from cogs.modals.channel_view import ChannelView
from cogs.modals.role_view import RoleView

# ============================= Setup View =============================
class SetupView(View):
    def __init__(self, author: discord.User, tags: list[str], timeout = 180):
        super().__init__(timeout=timeout)
        self.author = author
        self.selection_complete: bool = False
        self.selected_tag: str = ''
        self.new_tag: str = None
        self.values: list[int] = []
    
        # Add dropdown for tag selection
        options = [SelectOption(label=tag.capitalize(), value=tag) for tag in tags]
        
        self.tag_select = Select(
            placeholder="Seleziona il tag della sezione",
            custom_id="admin_add_tag_select",
            options=options
        )
        self.tag_select.callback = self.select_callback
        self.add_item(self.tag_select)
    
    async def select_callback(self, interaction: discord.Interaction) -> None:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Questa selezione non ti appartiene.", ephemeral=True)
            return
        
        self.selected_tag = self.tag_select.values[0]
        
        # Get the new tag
        modal: InputModal = InputModal(
            title="Nuovo tag",
            labels=["Inserisci il nuovo tag."]
        )
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.new_tag = modal.input_values[0]
        
        # Get the ids
        view = None
        if self.selected_tag == 'channels':
            view = ChannelView(
                author=interaction.user,
                min_values=1,
                max_values=1
            )
        else:
            view = RoleView(
                author=interaction.user,
                min_values=1,
                max_values=1
            )
        
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