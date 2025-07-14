
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ui import View, Select
from discord import SelectOption
# ----------------------------- Custom Libraries -----------------------------

# ============================= Setup View =============================
class SetupView(View):
    def __init__(self, author: discord.User, tags: list[str], timeout = 180):
        super().__init__(timeout=timeout)
        self.author = author
        self.selection_complete: bool = False
        self.selected_tag: str = ''
        
        options = [SelectOption(label=tag.capitalize(), value=tag) for tag in tags]
        
        self.tag_select = Select(
            placeholder="Seleziona il tag della sezione",
            custom_id="admin_check_select",
            options=options
        )
        self.tag_select.callback = self.select_callback
        self.add_item(self.tag_select)
    
    async def select_callback(self, interaction: discord.Interaction) -> None:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Questa selezione non ti appartiene.", ephemeral=True)
            return

        self.selected_tag = self.tag_select.values[0]
        self.selection_complete = True
        self.stop()