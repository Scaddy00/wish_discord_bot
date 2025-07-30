# ----------------------------- Imported Libraries -----------------------------
import discord

class BoosterRoleSelect(discord.ui.View):
    """
    View for selecting the server booster role using RoleSelect.
    """
    def __init__(self, author: discord.User):
        super().__init__(timeout=60)
        self.author = author
        self.selected_role_id: int = None
        self.add_item(self.BoosterRoleDropdown(self))

    class BoosterRoleDropdown(discord.ui.RoleSelect):
        def __init__(self, parent_view):
            super().__init__(placeholder="Seleziona il ruolo booster", min_values=1, max_values=1)
            self.parent_view = parent_view
        async def callback(self, interaction: discord.Interaction):
            if interaction.user.id != self.parent_view.author.id:
                await interaction.response.send_message("Questa selezione non ti appartiene.", ephemeral=True)
                return
            selected_role = self.values[0]
            self.parent_view.selected_role_id = selected_role.id
            await interaction.response.send_message(f"Ruolo booster selezionato: {selected_role.mention}", ephemeral=True)
            self.parent_view.stop() 