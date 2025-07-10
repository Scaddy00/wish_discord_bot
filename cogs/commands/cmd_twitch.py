
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from discord import app_commands
from os import getenv
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from cogs.twitch import TwitchApp
from cogs.twitch.add_tag_modal import SetupModal as TagModal
from cogs.twitch.change_title_view import SetupView as TitleView

class CmdTwitch(commands.GroupCog, name="twitch"):
    def __init__(self, bot: commands.bot, log: Logger, twitch_app: TwitchApp):
        super().__init__()
        self.bot = bot
        self.log = log
        self.twitch_app = twitch_app
    
    @app_commands.command(name="add-tag", description="Aggiunge un nuovo tag per le live e la scelta delle immagini")
    async def add_tag(self, interaction: discord.Interaction) -> None:
        # Get the guild from interaction
        guild: discord.Guild = interaction.guild
        # Load communication channel
        communication_channel = guild.get_channel(int(getenv('BOT_COMMUNICATION_CHANNEL_ID')))
        
        try:
            modal = TagModal(author=interaction.user)
            await interaction.response.send_modal(modal)
            await modal.wait()
            
            if not getattr(modal, 'selection_complete', False):
                await interaction.followup.send("Selezione non confermata o tempo scaduto.")
                return
            
            # Send confirmation message with selected values
            await interaction.followup.send(
                f'#️⃣ Tag: {modal.tag}'
                f'\n🌌 Url immagine: {modal.url}'
            )
            
            data: dict = {
                'tag': f'{modal.tag}',
                'url': f'{modal.url}'
            }
            
            # Update data in twitch_app images
            self.twitch_app.add_image(data)
            
            # Respond with success
            await interaction.followup.send('✅ Dati salvati con successo!')
            
            # INFO Log that the operation is completed
            await self.log.command(f'Aggiunti un nuovo tag e una nuova immagine:\n - tag: {data["tag"]} \n - url: {data["url"]}', 'twitch', 'add-tag')
            
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante l\'aggiunta di un nuovo tag.\n{e}'
            await self.log.error(error_message, 'COMMAND - TWITCH - ADD-TAG')
            await communication_channel.send(self.log.error_message(command='COMMAND - TWITCH - ADD-TAG', message=error_message))
    
    @app_commands.command(name="change-title", description="Cambio il titolo che viene usato quando la live è attiva")
    async def change_title(self, interaction: discord.Interaction) -> None:
        # Get the guild from interaction
        guild: discord.Guild = interaction.guild
        # Load communication channel
        communication_channel = guild.get_channel(int(getenv('BOT_COMMUNICATION_CHANNEL_ID')))
        
        try:
            view: TitleView = TitleView(author=interaction.user)
            await interaction.response.send_message(
                'Seleziona la tipologia di titolo che vuoi modificare.',
                view=view,
                ephemeral=True
            )
            
            await view.wait()
            if not view.selection_complete:
                await interaction.followup.send("Dati incompleti o tempo scaduto.")
                return

            # Send confirmation message with selected values
            await interaction.followup.send(
                f'#️⃣ Tag: {view.tag}'
                f'\n✅ Titolo: {view.title}'
            )
            
            data: dict = {
                'tag': view.tag,
                'title': view.title
            }
            
            # Update data in twitch_app images
            self.twitch_app.add_title(data)
            
            # Respond with success
            await interaction.followup.send('✅ Dati salvati con successo!')
            
            # INFO Log that the operation is completed
            await self.log.command(f'Modificato un titolo:\n - tag: {data["tag"]} \n - titolo: {data["title"]}', 'twitch', 'change-title')
            
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante l\'aggiunta di un nuovo tag.\n{e}'
            await self.log.error(error_message, 'COMMAND - TWITCH - ADD-TAG')
            await communication_channel.send(self.log.error_message(command='COMMAND - TWITCH - ADD-TAG', message=error_message))