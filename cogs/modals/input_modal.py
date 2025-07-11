
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ui import Modal, TextInput

class InputModal(Modal):
    def __init__(self, title: str, labels: list[str]):
        super().__init__(title=title)

        self.text_input: list[TextInput] = []
        self.input_values: list[str] = []

        for label in labels:
            text_input = TextInput(
                label=label,
                placeholder="Scrivi qui...",
                required=True
            )
            self.text_input.append(text_input)
            self.add_item(text_input)

    async def on_submit(self, interaction: discord.Interaction):
        self.input_values = [t_input.value.strip() for t_input in self.text_input]

        if not all(self.input_values):
            await interaction.response.send_message(
                "Hai lasciato uno o più campi vuoti. Riprova.", ephemeral=True
            )
            self.input_values = []
            return

        await interaction.response.defer()