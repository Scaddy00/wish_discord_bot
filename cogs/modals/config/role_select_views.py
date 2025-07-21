# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ui import View, Select, RoleSelect, Button
from discord import SelectOption

class NotVerifiedRoleSelect(discord.ui.View):
    """
    View for selecting the 'not_verified' role using RoleSelect.
    """
    def __init__(self, author: discord.User):
        super().__init__(timeout=60)
        self.author = author
        self.selected_role_id = None
        self.add_item(self.NotVerifiedRoleDropdown(self))

    class NotVerifiedRoleDropdown(discord.ui.RoleSelect):
        def __init__(self, parent_view):
            super().__init__(placeholder="Seleziona il ruolo 'not_verified'", min_values=1, max_values=1)
            self.parent_view = parent_view
        async def callback(self, interaction: discord.Interaction):
            if interaction.user.id != self.parent_view.author.id:
                await interaction.response.send_message("Questa selezione non ti appartiene.", ephemeral=True)
                return
            selected_role = self.values[0]
            self.parent_view.selected_role_id = str(selected_role.id)
            await interaction.response.send_message(f"Ruolo 'not_verified' selezionato: {selected_role.mention}", ephemeral=True)
            self.parent_view.stop()

class NotVerifiedAndVerificationSetupView(View):
    def __init__(self, author: discord.User):
        super().__init__(timeout=180)
        self.author = author
        self.selection_complete = False
        self.not_verified_role: discord.Role = None
        self.timeout: int = None
        self.temp_role: discord.Role = None
        self.verified_role: discord.Role = None

        # Timeout select (row 0)
        select_timeout: Select = Select(
            placeholder="Seleziona timeout verifica",
            custom_id="timeout_select",
            options=[
                SelectOption(label="5 minuti", value="300"),
                SelectOption(label="10 minuti", value="600"),
                SelectOption(label="15 minuti", value="900"),
                SelectOption(label="30 minuti", value="1800"),
            ],
            row=0
        )
        select_timeout.callback = self.timeout_callback
        self.add_item(select_timeout)

        # Not verified role select (row 1)
        self.not_verified_select = RoleSelect(
            placeholder="Seleziona il ruolo 'not_verified'",
            custom_id="not_verified_role_select",
            min_values=1,
            max_values=1,
            row=1
        )
        self.not_verified_select.callback = self.not_verified_callback
        self.add_item(self.not_verified_select)

        # Temp role select (row 2)
        self.temp_role_select = RoleSelect(
            placeholder="Seleziona ruolo 'in_verification'",
            custom_id="temp_role_select",
            min_values=1,
            max_values=1,
            row=2
        )
        self.temp_role_select.callback = self.temp_role_callback
        self.add_item(self.temp_role_select)

        # Verified role select (row 3)
        self.verified_role_select = RoleSelect(
            placeholder="Seleziona ruolo 'verified'",
            custom_id="verified_role_select",
            min_values=1,
            max_values=1,
            row=3
        )
        self.verified_role_select.callback = self.verified_role_callback
        self.add_item(self.verified_role_select)

        # Confirm button (row 4)
        button_confirm = Button(
            label="Conferma",
            style=discord.ButtonStyle.green,
            row=4
        )
        button_confirm.callback = self.confirm_callback
        self.add_item(button_confirm)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Solo l'autore può usare questa interfaccia.", ephemeral=True)
            return False
        return True

    async def not_verified_callback(self, interaction: discord.Interaction):
        role_id = int(interaction.data["values"][0])
        self.not_verified_role = interaction.guild.get_role(role_id)
        await interaction.response.defer()

    async def timeout_callback(self, interaction: discord.Interaction):
        self.timeout = int(interaction.data["values"][0])
        await interaction.response.defer()

    async def temp_role_callback(self, interaction: discord.Interaction):
        role_id = int(interaction.data["values"][0])
        self.temp_role = interaction.guild.get_role(role_id)
        await interaction.response.defer()

    async def verified_role_callback(self, interaction: discord.Interaction):
        role_id = int(interaction.data["values"][0])
        self.verified_role = interaction.guild.get_role(role_id)
        await interaction.response.defer()

    async def confirm_callback(self, interaction: discord.Interaction):
        if self.not_verified_role and self.timeout and self.temp_role and self.verified_role:
            self.selection_complete = True
            self.stop()
            await interaction.response.send_message("✅ Selezione confermata!", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ Completa tutte le selezioni prima di confermare.", ephemeral=True) 