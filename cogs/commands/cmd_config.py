
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from discord import app_commands
from os import getenv
import re
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from utils.config import add_exception
from cogs.modals.exception_view import SetupView as ExceptionView

class CmdConfig(commands.GroupCog, name="config"):
    def __init__(self, bot: commands.bot, log: Logger):
        super().__init__()
        self.bot = bot
        self.log = log
    
    @app_commands.command(name="add-exception", description="Aggiunge una lista di ruoli o canali alle eccezioni")
    async def add_exception(self, interaction: discord.Interaction) -> None:
        # Get the guild from interaction
        guild: discord.Guild = interaction.guild
        # Load communication channel
        communication_channel = guild.get_channel(int(getenv('BOT_COMMUNICATION_CHANNEL_ID')))
        
        try:            
            view: ExceptionView = ExceptionView(author=interaction.user)
            await interaction.response.send_message(
                "Aggiungi l'eccezione",
                view=view,
                ephemeral=True
            )
            await view.wait()

            tag: str = view.tag
            values: list[int] = view.values
            
            # Respond with selected data
            await interaction.followup.send(
                "Dati inseriti:\n"
                f"#️⃣ Tag: {tag} \n"
                f"🆚 Tipologia: {view.type} \n"
                f"🆔 Id: {values} \n",
                ephemeral=True
            )
            
            # Update data in config exceptions
            add_exception(tag, values)
            
            # Respond with success
            await interaction.followup.send(
                '✅ Dati salvati con successo!',
                ephemeral=True
            )
            
            # INFO Log that operation is completed
            await self.log.command(f'Aggiunta una nuova eccezione: \n - tag: {tag} \n - values: {values}', 'config', 'EXCEPTION')

        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante l\'aggiunta di nuove eccezioni al file config.\n{e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - EXCEPTION')
            await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - EXCEPTION', message=error_message))