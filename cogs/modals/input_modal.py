
# ----------------------------- Imported Libraries -----------------------------
# Third-party library imports
import discord
from discord.ui import Modal, TextInput

class InputModal(Modal):
    """
    A modal dialog for collecting user input with multiple text fields.
    
    Creates a Discord modal with multiple text input fields based on the provided labels.
    """
    
    def __init__(self, title: str, labels: list[str]) -> None:
        """
        Initialize the InputModal.
        
        Args:
            title (str): Title of the modal dialog
            labels (list[str]): List of labels for each text input field
        """
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

    async def on_submit(self, interaction: discord.Interaction) -> None:
        """
        Handle modal submission.
        
        Validates that all fields are filled and stores the input values.
        If any field is empty, shows an error message and clears the values.
        
        Args:
            interaction (discord.Interaction): The interaction that submitted the modal
        """
        self.input_values = [t_input.value.strip() for t_input in self.text_input]

        if not all(self.input_values):
            await interaction.response.send_message(
                "Hai lasciato uno o più campi vuoti. Riprova.", ephemeral=True
            )
            self.input_values = []
            return

        await interaction.response.defer()