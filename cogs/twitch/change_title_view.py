
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ui import View, Select
from discord import SelectOption
from cogs.modals.input_modal import InputModal

class SetupView(View):
    def __init__(self, author: discord.User):
        super().__init__(timeout=180.0)
        self.author = author
        self.selection_complete: bool = False
        self.tag: str = None
        self.title: str = None

    @discord.ui.select(
        placeholder="Tipologia titolo",
        custom_id="tag_select",
        options=[
            SelectOption(label="On Live", value="on"),
            SelectOption(label="Off Live", value="off")
        ]
    )
    async def tag_callback(self, interaction: discord.Interaction, select: Select):
        self.tag = select.values[0]
        modal: InputModal = InputModal(
            title="Modifica un titolo",
            label=[f'Inserisci il titolo per "{self.tag}"']
        )
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.title = modal.input_values[0]

        if self.title and self.tag:
            self.selection_complete = True
            self.stop()
            await interaction.followup.send("✅ Selezione confermata!", ephemeral=True)
        else:
            await interaction.followup.send("⚠️ Completa tutte le selezioni prima di confermare.", ephemeral=True)