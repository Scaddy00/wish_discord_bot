
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ui import Modal, View, TextInput, Select, Button
from discord import SelectOption

class InputModal(Modal):
    def __init__(self, selected: str):
        super().__init__(title="Modifica un titolo")
        self.selected = selected
        self.text_input = TextInput(
            label=f'Inserisci il titolo per "{selected}"',
            placeholder="Scrivi qui...",
            required=True
        )
        self.add_item(self.text_input)
        # Response
        self.input_value: str = None
        
    async def on_submit(self, interaction: discord.Interaction):
        self.input_value = self.text_input.value
        await interaction.response.defer()
        

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
        modal: InputModal = InputModal(self.tag)
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.title = modal.input_value

        if self.title and self.tag:
            self.selection_complete = True
            self.stop()
            await interaction.followup.send("✅ Selezione confermata!", ephemeral=True)
        else:
            await interaction.followup.send("⚠️ Completa tutte le selezioni prima di confermare.", ephemeral=True)