
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ui import View, ChannelSelect, Select
from discord import SelectOption
# ----------------------------- Custom Libraries -----------------------------
from cogs.modals.confirm_button import ConfirmButton

# ============================= Setup View =============================
class SetupView(View):
    def __init__(self, author: discord.User, timeout = 180):
        super().__init__(timeout=timeout)
        self.author = author
        self.selection_complete: bool = False
        self.selected_enabled: bool = None
        self.selected_channels: list[int] = []
        
        # Select for enabled/disabled
        options: list[SelectOption] = []
        options.append(SelectOption(label='Abilita', value=True))
        options.append(SelectOption(label='Disabilita', value=False))
        
        self.enabled_select = Select(
            placeholder="Seleziona se abilitare o disabilitare la registrazione dei messaggi",
            custom_id="message_logging_enabled_select",
            options=options
        )
        self.enabled_select.callback = self.select_callback
        self.add_item(self.enabled_select)
        
        # Select for channels
        self.select_channels: ChannelSelect = ChannelSelect(
            placeholder="Seleziona i canali in cui verranno registrati i messaggi",
            custom_id="message_logging_channels_select",
            channel_types=[
                discord.ChannelType.text,
                discord.ChannelType.forum,
                discord.ChannelType.stage_voice,
                discord.ChannelType.voice
            ],
            min_values=1,
            max_values=25
        )
        self.select_channels.callback = self.select_channels_callback
        self.add_item(self.select_channels)
        
        # Confirm button
        self.confirm_button = ConfirmButton(
            label="Conferma",
            custom_id="confirm_button",
            style=discord.ButtonStyle.green
        )
        self.confirm_button.callback = self.confirm_callback
        self.add_item(self.confirm_button)
        
    async def confirm_callback(self, interaction: discord.Interaction) -> None:
        # Check if the user is the author
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Questa selezione non ti appartiene.", ephemeral=True)
            return

        # If the user has set to False, the selection is complete
        if not self.selected_enabled:
            self.selection_complete = True
            await interaction.response.send_message("Selezione completata con successo.", ephemeral=True)
            self.stop()
            return
        # If the user has selected to enable or disable the message logging and has selected at least one channel, the selection is complete
        if self.selected_enabled is not None and self.selected_channels:
            self.selection_complete = True
            await interaction.response.send_message("Selezione completata con successo.", ephemeral=True)
            self.stop()
            return
        # If the user has not selected to enable or disable the message logging or has not selected the channels, the selection is not complete
        else:
            await interaction.response.send_message("Seleziona se abilitare o disabilitare la registrazione dei messaggi e i canali in cui verranno registrati i messaggi.", ephemeral=True)
            return
        
    async def select_callback(self, interaction: discord.Interaction) -> None:
        # Check if the user is the author
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Questa selezione non ti appartiene.", ephemeral=True)
            return

        # Convert the value to boolean
        self.selected_enabled = self.enabled_select.values[0] == "True"
        await interaction.response.defer(ephemeral=True)
        
    async def select_channels_callback(self, interaction: discord.Interaction) -> None:
        # Check if the user is the author
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Questa selezione non ti appartiene.", ephemeral=True)
            return

        # Convert channel objects to their IDs
        self.selected_channels = [channel.id for channel in self.select_channels.values]
        await interaction.response.defer(ephemeral=True)