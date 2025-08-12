
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ui import View, UserSelect
from discord import ButtonStyle
# ----------------------------- Custom Libraries -----------------------------
from .confirm_button import ConfirmButton

# ============================= User View =============================
class UserView(View):
    def __init__(self, author: discord.User, min_values: int = 1, max_values: int = 1, timeout: int = 180):
        super().__init__(timeout=timeout)
        self.author = author
        self.confirmed: bool = False
        self.selected_user_id: int | None = None

        self.user_select: UserSelect = UserSelect(
            placeholder="Seleziona l'utente",
            custom_id="user_select",
            min_values=min_values,
            max_values=max_values
        )
        self.user_select.callback = self.user_callback
        self.add_item(self.user_select)

        # Confirm button with overridden callback
        self.confirm_button = ConfirmButton(label="Conferma", style=ButtonStyle.success)
        self.confirm_button.callback = self.confirm_callback
        self.add_item(self.confirm_button)

    async def user_callback(self, interaction: discord.Interaction) -> None:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Questa selezione non ti appartiene.", ephemeral=True)
            return
        # Take the first selected user
        if self.user_select.values:
            selected = self.user_select.values[0]
            # values can be discord.Member or discord.User
            self.selected_user_id = getattr(selected, 'id', None)
        await interaction.response.defer(ephemeral=True)

    async def confirm_callback(self, interaction: discord.Interaction) -> None:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Questo pulsante non ti appartiene.", ephemeral=True)
            return
        if self.selected_user_id is None:
            await interaction.response.send_message("Seleziona un utente prima di confermare.", ephemeral=True)
            return
        self.confirmed = True
        await interaction.response.send_message("Selezione confermata.", ephemeral=True)
        self.stop()


