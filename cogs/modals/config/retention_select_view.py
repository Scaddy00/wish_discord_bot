# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ui import View, Select
from discord import SelectOption
from cogs.modals.confirm_button import ConfirmButton

# ============================= Retention Select View =============================
class RetentionSelectView(View):
    def __init__(self, author: discord.User, timeout=180):
        super().__init__(timeout=timeout)
        self.author = author
        self.selection_complete: bool = False
        self.selected_days: int = None

        # Opzioni: 1, 2, 3, 6 mesi
        options = [
            SelectOption(label='1 mese', value='30'),
            SelectOption(label='2 mesi', value='60'),
            SelectOption(label='3 mesi', value='90'),
            SelectOption(label='6 mesi', value='180'),
        ]
        self.retention_select = Select(
            placeholder="Seleziona il periodo di conservazione dei log",
            custom_id="retention_days_select",
            options=options
        )
        self.retention_select.callback = self.select_callback
        self.add_item(self.retention_select)

        # Bottone di conferma
        self.confirm_button = ConfirmButton(
            label="Conferma",
            custom_id="confirm_button_retention",
            style=discord.ButtonStyle.green
        )
        self.confirm_button.callback = self.confirm_callback
        self.add_item(self.confirm_button)

    async def select_callback(self, interaction: discord.Interaction) -> None:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Questa selezione non ti appartiene.", ephemeral=True)
            return
        self.selected_days = int(self.retention_select.values[0])
        await interaction.response.defer(ephemeral=True)

    async def confirm_callback(self, interaction: discord.Interaction) -> None:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Questa selezione non ti appartiene.", ephemeral=True)
            return
        if self.selected_days:
            self.selection_complete = True
            await interaction.response.send_message(f"Periodo di conservazione selezionato: {self.selected_days} giorni.", ephemeral=True)
            self.stop()
        else:
            await interaction.response.send_message("Seleziona un periodo di conservazione.", ephemeral=True) 