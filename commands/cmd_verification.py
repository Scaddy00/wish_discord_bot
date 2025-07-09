
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from discord import app_commands
from os import getenv
# ----------------------------- Custom Libraries -----------------------------
from logger.logger import Logger
from verification import VerificationManager
from views.verification_setup_view import SetupView

class CmdVerification(commands.GroupCog, name="verification"):
    def __init__(self, bot: discord.Client, log: Logger, verification: VerificationManager):
        super().__init__()
        self.bot = bot
        self.log = log
        self.verification = verification
        
    @app_commands.command(name="setup", description="Inserisce i dati necessari per il sistema di verifica")
    async def setup(self, interaction: discord.Interaction) -> None:
        # Get the guild from interaction
        guild: discord.Guild = interaction.guild
        # Load communication channel
        communication_channel = guild.get_channel(int(getenv('BOT_COMMUNICATION_CHANNEL_ID')))
        
        try:
            view = SetupView(author=interaction.user)
            await interaction.response.send_message(
                "Configura il sistema: seleziona il timeout, il ruolo temporaneo e il ruolo verificato.",
                view=view,
                ephemeral=True
            )

            await view.wait()
            if not view.selection_complete:
                await interaction.followup.send("Selezione non confermata o tempo scaduto.")
                return

            # Send confirmation message with selected values
            await interaction.followup.send(
                f"✅ Timeout selezionato: **{view.timeout} secondi**\n"
                f"🛑 Ruolo temporaneo: {view.temp_role.mention}\n"
                f"✔️ Ruolo verificato: {view.verified_role.mention}"
            )
            
            data: dict = {
                'timeout': view.timeout,
                'temp_role_id': view.temp_role.id,
                'verified_role_id': view.verified_role.id
            }
            
            # Update data in verification config
            self.verification.update_config(data)
            
            # Respond with success
            await interaction.followup.send('Dati salvati con successo!')
            
            # INFO Log that the operation is completed
            await self.log.command(f'Configurazione aggiornata con i seguenti dati: \n - timeout: {data["timeout"]} \n - temp_role_id: {data["temp_role_id"]} ({view.temp_role.name}) \n - verified_role_id: {data["verified_role_id"]} ({view.verified_role.name})', 'verification', 'setup')
            
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante la creazione di un nuovo messaggio.\n{e}'
            await self.log.error(error_message, 'COMMAND - VERIFICATION - SETUP')
            await communication_channel.send(self.log.error_message(command='COMMAND - VERIFICATION - SETUP', message=error_message))