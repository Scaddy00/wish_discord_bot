
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from discord import app_commands
from os import getenv
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from cogs.verification import VerificationManager
from cogs.verification.verification_setup_view import SetupView
from config_manager import ConfigManager
from utils.printing import safe_send_message, create_embed

class CmdVerification(commands.GroupCog, name="verification"):
    def __init__(self, bot: commands.bot, log: Logger, config: ConfigManager, verification: VerificationManager):
        super().__init__()
        self.bot = bot
        self.log = log
        self.config = config
        self.verification = verification
        
        # Dictionary containing all commands and their descriptions
        self.commands_info = {
            "setup": "Inserisce i dati necessari per il sistema di verifica"
        }
    
    # ============================= Help Command =============================
    @app_commands.command(name="help", description="Mostra l'elenco dei comandi verification disponibili")
    async def help(self, interaction: discord.Interaction) -> None:
        """Mostra un embed con tutti i comandi verification e le loro descrizioni"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel) if self.config.communication_channel else None
        
        try:
            # Create embed with commands info
            embed = create_embed(
                title="✅ Comandi Verification",
                description="Elenco di tutti i comandi per la gestione della verifica",
                color=self.bot.color,
                fields=[]
            )
            
            # Add each command to the embed
            for command_name, description in self.commands_info.items():
                embed.add_field(
                    name=f"`/verification {command_name}`",
                    value=description,
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await self.log.command('Visualizzato help comandi verification', 'verification', 'HELP')
            
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - VERIFICATION - HELP')
            await interaction.response.send_message(f"❌ {error_message}", ephemeral=True)
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - VERIFICATION - HELP')
            await interaction.response.send_message(f"❌ {error_message}", ephemeral=True)
            
        except Exception as e:
            error_message: str = f'Errore durante la visualizzazione dell\'help: {e}'
            await self.log.error(error_message, 'COMMAND - VERIFICATION - HELP')
            await interaction.response.send_message(f"❌ {error_message}", ephemeral=True)
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - VERIFICATION - HELP', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - VERIFICATION - HELP')
        
    # ============================= Verification Setup =============================
    @app_commands.command(name="setup", description="Inserisce i dati necessari per il sistema di verifica")
    async def setup(self, interaction: discord.Interaction) -> None:
        """Configura il sistema di verifica con timeout e ruoli"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel)
        
        try:
            view = SetupView(author=interaction.user)
            await interaction.response.send_message(
                "Configura il sistema: seleziona il timeout, il ruolo temporaneo e il ruolo verificato.",
                view=view,
                ephemeral=True
            )

            await view.wait()
            if not view.selection_complete:
                await safe_send_message(interaction, "Selezione non confermata o tempo scaduto.")
                return

            # Send confirmation message with selected values
            await safe_send_message(
                interaction,
                f"✅ Timeout selezionato: **{view.timeout} secondi**\n"
                f"🛑 Ruolo temporaneo: {view.temp_role.mention}\n"
                f"✔️ Ruolo verificato: {view.verified_role.mention}"
            )
            
            timeout = view.timeout
            temp_role_id = view.temp_role.id
            verified_role_id = view.verified_role.id
            
            # Update temp role in verification config
            self.config.add_admin('roles', 'in_verification', temp_role_id)
            # Update verified role in verification config
            self.config.add_admin('roles', 'verified', verified_role_id)
            # Update timeout in verification config
            self.verification.update_timeout(timeout)
            
            # Respond with success
            await safe_send_message(interaction, 'Dati salvati con successo!')
            
            # INFO Log that the operation is completed
            await self.log.command(f'Configurazione aggiornata con i seguenti dati: \n - timeout: {timeout} \n - temp_role_id: {temp_role_id} ({view.temp_role.name}) \n - verified_role_id: {verified_role_id} ({view.verified_role.name})', 'verification', 'setup')
            
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - VERIFICATION - SETUP')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - VERIFICATION - SETUP')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante la creazione di un nuovo messaggio: {e}'
            await self.log.error(error_message, 'COMMAND - VERIFICATION - SETUP')
            await safe_send_message(interaction, f"❌ {error_message}")
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - VERIFICATION - SETUP', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - VERIFICATION - SETUP')