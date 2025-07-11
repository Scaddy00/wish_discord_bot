
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
from cogs.modals.input_modal import InputModal

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
            modal = TagModal()
            await interaction.response.send_modal(modal)
            await modal.wait()
            
            if not getattr(modal, 'selection_complete', False):
                await interaction.followup.send("Selezione non confermata o tempo scaduto.")
                return
            
            # Send confirmation message with selected values
            await interaction.followup.send(
                f'#️⃣ Tag: {modal.tag}'
                f'\n🌌 Url immagine: {modal.url}',
                ephemeral=True
            )
            
            data: dict = {
                'tag': f'{modal.tag}',
                'url': f'{modal.url}'
            }
            
            # Update data in twitch_app images
            self.twitch_app.add_image(data)
            
            # Respond with success
            await interaction.followup.send(
                '✅ Dati salvati con successo!',
                ephemeral=True
            )
            
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
                f'\n✅ Titolo: {view.title}',
                ephemeral=True
            )
            
            data: dict = {
                'tag': view.tag,
                'title': view.title
            }
            
            # Update data in twitch_app images
            self.twitch_app.change_title(data)
            
            # Respond with success
            await interaction.followup.send(
                '✅ Dati salvati con successo!',
                ephemeral=True
            )
            
            # INFO Log that the operation is completed
            await self.log.command(f'Modificato un titolo:\n - tag: {data["tag"]} \n - titolo: {data["title"]}', 'twitch', 'change-title')
            
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante l\'aggiunta di un nuovo tag.\n{e}'
            await self.log.error(error_message, 'COMMAND - TWITCH - CHANGE-TITLE')
            await communication_channel.send(self.log.error_message(command='COMMAND - TWITCH - CHANGE-TITLE', message=error_message))
    
    @app_commands.command(name="change-streamer", description="Cambio il nome dello streamer")
    async def change_streamer(self, interaction: discord.Interaction) -> None:
        # Get the guild from interaction
        guild: discord.Guild = interaction.guild
        # Load communication channel
        communication_channel = guild.get_channel(int(getenv('BOT_COMMUNICATION_CHANNEL_ID')))
        
        try:
            modal: InputModal = InputModal(
                title='Modifica stream',
                label=['Inserisci il nuovo nome dello streamer.']
            )
            await interaction.response.send_modal(modal)
            await modal.wait()
            
            # Send confirmation message with selected value
            await interaction.followup.send(
                f'🟣 Nome Streamer: {modal.input_values[0]}',
                ephemeral=True
            )
            
            # Update data in twitch_app streamer name
            self.twitch_app.change_streamer_name(modal.input_value)
            
            # Respond with success
            await interaction.followup.send(
                '✅ Dati salvati con successo!',
                ephemeral=True
            )
            
            # INFO Log that the operation is completed
            await self.log.command(f'Modificato il nome dello streamer: {modal.input_value}', 'twitch', 'change-streamer')
            
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante la modifica del nome dello streamer.\n{e}'
            await self.log.error(error_message, 'COMMAND - TWITCH - CHANGE-STREAMER')
            await communication_channel.send(self.log.error_message(command='COMMAND - TWITCH - CHANGE-STREAMER', message=error_message))

    @app_commands.command(name="reset-info", description="Reset delle info riguardante l'ultima stream")
    async def reset_info(self, interaction: discord.Interaction) -> None:
        # Get the guild from interaction
        guild: discord.Guild = interaction.guild
        # Load communication channel
        communication_channel = guild.get_channel(int(getenv('BOT_COMMUNICATION_CHANNEL_ID')))\
        
        try:
            # Reset stream info
            self.twitch_app.set_default_stream_info()
            # Respond with success
            await interaction.response.send_message(
                '✅ Informazioni della stream resettate!',
                ephemeral=True
            )
            
            # INFO Log that the operation is completed
            await self.log.command(f'Eseguito un reset dei delle info dell\'ultima stream', 'twitch', 'reset-info')

        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante la modifica del nome dello streamer.\n{e}'
            await self.log.error(error_message, 'COMMAND - TWITCH - RESET-INFO')
            await communication_channel.send(self.log.error_message(command='COMMAND - TWITCH - RESET-INFO', message=error_message))