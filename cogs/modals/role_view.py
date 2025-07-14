
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ui import View, RoleSelect
from discord import ButtonStyle
# ----------------------------- Custom Libraries -----------------------------
from .confirm_button import ConfirmButton

# ============================= Role View =============================
class RoleView(View):
    def __init__(self, author: discord.User, min_values = 0, max_values = 40, timeout = 180):
        super().__init__(timeout=timeout)
        self.author = author
        self.values: list[int] = []
        self.confirmed: bool = False
        
        self.role_select: RoleSelect = RoleSelect(
            placeholder="Seleziona il ruolo",
            custom_id="role_select",
            min_values=min_values,
            max_values=max_values
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