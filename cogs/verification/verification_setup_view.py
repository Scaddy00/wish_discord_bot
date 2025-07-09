import discord
from discord.ui import View, Select
from discord.ui import RoleSelect

class SetupView(View):
    def __init__(self, author: discord.User):
        super().__init__(timeout=180)
        self.author = author
        self.selection_complete = False
        
        # Add dropdown for timeout value selection
        select_timeout: Select = Select(
            placeholder="Seleziona timeout",
            custom_id="timeout_select",
            options=[
                discord.SelectOption(label="5 minuti", value="300"),
                discord.SelectOption(label="10 minuti", value="600"),
                discord.SelectOption(label="15 minuti", value="900"),
                discord.SelectOption(label="30 minuti", value="1800"),
            ],
            row=0
        )
        select_timeout.callback = self.timeout_callback
        self.add_item(select_timeout)
        
        # Add dropdown for temp role selection
        select_temp_role: RoleSelect = RoleSelect(
            placeholder="Seleziona ruolo temporaneo",
            custom_id="temp_role_select",
            min_values=1,
            max_values=1,
            row=1
        )
        select_temp_role.callback = self.temp_role_callback
        self.add_item(select_temp_role)
        
        # Add dropdown for temp role selection
        select_verified_role: RoleSelect = RoleSelect(
            placeholder="Seleziona ruolo verificato",
            custom_id="verified_role_select",
            min_values=1,
            max_values=1,
            row=2
        )
        select_verified_role.callback = self.verified_role_callback
        self.add_item(select_verified_role)
        
        # Add button to confirm the selection
        button_confirm = discord.ui.Button(label="Conferma", style=discord.ButtonStyle.green, row=3)
        button_confirm.callback = self.confirm_callback
        self.add_item(button_confirm)
        
        # Selected values
        self.timeout: int = None
        self.temp_role: discord.Role = None
        self.verified_role: discord.Role = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Allow only the original user
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Solo l'autore può usare questa interfaccia.")
            return False
        return True

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
        if self.timeout != None and self.temp_role != None and self.verified_role != None:
            self.selection_complete = True
            self.stop()
            await interaction.response.send_message("✅ Selezione confermata!")
        else:
            await interaction.response.send_message("⚠️ Completa tutte le selezioni prima di confermare.")