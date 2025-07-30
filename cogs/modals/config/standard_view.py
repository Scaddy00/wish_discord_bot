
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ui import View, ChannelSelect, Button
from discord import ButtonStyle
# ----------------------------- Custom Libraries -----------------------------
from cogs.modals.confirm_button import ConfirmButton

# ============================= Setup View =============================
class SetupView(View):
    def __init__(self, author: discord.User, tags: list[str], timeout = 180):
        super().__init__(timeout=timeout)
        self.author = author
        self.tags = tags
        self.values: dict = {}
        self.current_page = 0
        self.items_per_page = 4  # Massimo 4 elementi per pagina (5° riga per bottoni)
        self.total_pages = (len(tags) + self.items_per_page - 1) // self.items_per_page
        
        self.select_channels: list[ChannelSelect] = []
        self.setup_current_page()
    
    def setup_current_page(self):
        """Configura gli elementi per la pagina corrente"""
        self.clear_items()
        self.select_channels.clear()
        
        # Calcola gli elementi da mostrare nella pagina corrente
        start_idx = self.current_page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.tags))
        current_tags = self.tags[start_idx:end_idx]
        
        # Crea i ChannelSelect per la pagina corrente
        for i, tag in enumerate(current_tags):
            channel_select = ChannelSelect(
                placeholder=f"Seleziona il canale per la sezione {tag}",
                custom_id=f"select_channel_{tag}",
                channel_types=[discord.ChannelType.text, discord.ChannelType.news],
                row=i
            )
            channel_select.callback = self.select_channel_callback
            self.select_channels.append(channel_select)
            self.add_item(channel_select)
        
        # Aggiungi bottoni di navigazione e conferma
        self.add_navigation_buttons()
    
    def add_navigation_buttons(self):
        """Aggiunge i bottoni di navigazione e conferma"""
        # Bottone Conferma (sempre presente)
        confirm_button = ConfirmButton(
            label="Conferma",
            custom_id="confirm_button",
            style=discord.ButtonStyle.green,
            row=4
        )
        self.add_item(confirm_button)
        
        # Bottoni di navigazione (solo se necessario)
        if self.total_pages > 1:
            # Bottone Indietro
            if self.current_page > 0:
                prev_button = Button(
                    label="◀️ Indietro",
                    custom_id="prev_page",
                    style=discord.ButtonStyle.secondary,
                    row=4
                )
                prev_button.callback = self.prev_page_callback
                self.add_item(prev_button)
            
            # Bottone Avanti
            if self.current_page < self.total_pages - 1:
                next_button = Button(
                    label="Avanti ▶️",
                    custom_id="next_page",
                    style=discord.ButtonStyle.secondary,
                    row=4
                )
                next_button.callback = self.next_page_callback
                self.add_item(next_button)
            
            # Indicatore di pagina
            page_indicator = Button(
                label=f"Pagina {self.current_page + 1}/{self.total_pages}",
                custom_id="page_indicator",
                style=discord.ButtonStyle.primary,
                disabled=True,
                row=4
            )
            self.add_item(page_indicator)
    
    async def select_channel_callback(self, interaction: discord.Interaction) -> None:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Questa selezione non ti appartiene.", ephemeral=True)
            return
        
        tag = interaction.data['custom_id'].split('_', 2)[-1]
        selected_channel_id = int(interaction.data['values'][0])
        self.values[tag] = selected_channel_id
        await interaction.response.defer(ephemeral=True)
    
    async def prev_page_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Solo l'autore può navigare.", ephemeral=True)
            return
        
        if self.current_page > 0:
            self.current_page -= 1
            self.setup_current_page()
            await interaction.response.edit_message(view=self)
        else:
            await interaction.response.send_message("Sei già alla prima pagina.", ephemeral=True)
    
    async def next_page_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Solo l'autore può navigare.", ephemeral=True)
            return
        
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.setup_current_page()
            await interaction.response.edit_message(view=self)
        else:
            await interaction.response.send_message("Sei già all'ultima pagina.", ephemeral=True)
        
