# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from discord import app_commands
from os import getenv
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from config_manager import ConfigManager
from cogs.twitch import TwitchApp
from cogs.verification import VerificationManager
from utils.printing import create_embed_from_dict, safe_send_message
# ----------------------------- Modals -----------------------------
from cogs.modals.config.exception_view import SetupView as ExceptionView
from cogs.modals.config.admin_check_view import SetupView as AdminCheckView
from cogs.modals.config.admin_add_view import SetupView as AdminAddView
from cogs.modals.config.standard_view import SetupView as StandardView
from cogs.modals.config.message_logging_view import SetupView as MessageLoggingView
from cogs.modals.config.retention_select_view import RetentionSelectView
from cogs.modals.config.booster_role_select_view import BoosterRoleSelect
from cogs.modals.config.role_select_views import NotVerifiedRoleSelect, NotVerifiedAndVerificationSetupView
from cogs.twitch.views_modals.titles_view import TwitchTitlesView
from cogs.twitch.views_modals.streamer_name_view import StreamerNameView
from cogs.twitch.views_modals.add_tag_modal import SetupModal as TagModal
from cogs.twitch.views_modals.change_title_view import SetupView as TitleView
from cogs.modals.input_modal import InputModal

class CmdConfig(commands.GroupCog, name="config"):
    def __init__(self, bot: commands.bot, log: Logger, config: ConfigManager, twitch_app: TwitchApp, verification: VerificationManager):
        super().__init__()
        self.bot = bot
        self.log = log
        self.config = config
        self.twitch_app = twitch_app
        self.verification = verification
        
        # Dictionary containing all commands and their descriptions
        self.commands_info = {
            "standard": "Configura i canali principali del bot",
            "retention": "Configura il periodo di conservazione dei log",
            "message-logging": "Configura la registrazione dei messaggi",
            "set-not-verified-role": "Configura il ruolo 'not_verified'",
            "set-booster-role": "Configura il ruolo booster del server",
            "verification-setup": "Configura il sistema di verifica",
            "admin-check": "Visualizza i dati di configurazione admin",
            "admin-add": "Aggiunge un ruolo o canale alla configurazione admin",
            "exception-add": "Aggiunge eccezioni per ruoli o canali",
            "twitch-titles": "Configura i titoli Twitch per stream on/off",
            "twitch-streamer": "Configura il nome dello streamer Twitch",
            "twitch-add-tag": "Aggiunge un nuovo tag per le live e immagini",
            "twitch-reset-info": "Reset delle informazioni dell'ultima stream",
            "setup-iniziale": "Esegui la configurazione iniziale completa del bot"
        }
    
    # ============================= Help Command =============================
    @app_commands.command(name="help", description="Mostra l'elenco dei comandi config disponibili")
    async def help(self, interaction: discord.Interaction) -> None:
        """Mostra un embed con tutti i comandi config e le loro descrizioni"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel) if self.config.communication_channel else None
        
        try:
            # Create embed with commands info
            embed = create_embed_from_dict({
                'title': '⚙️ Comandi Config',
                'description': 'Elenco di tutti i comandi di configurazione disponibili',
                'color': self.bot.color,
                'fields': []
            })
            
            # Add each command to the embed
            for command_name, description in self.commands_info.items():
                embed.add_field(
                    name=f"`/config {command_name}`",
                    value=description,
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await self.log.command('Visualizzato help comandi config', 'config', 'HELP')
            
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - HELP')
            await interaction.response.send_message(f"❌ {error_message}", ephemeral=True)
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - HELP')
            await interaction.response.send_message(f"❌ {error_message}", ephemeral=True)
            
        except Exception as e:
            error_message: str = f'Errore durante la visualizzazione dell\'help: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - HELP')
            await interaction.response.send_message(f"❌ {error_message}", ephemeral=True)
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - HELP', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - CONFIG - HELP')
    
    # ============================= Core Configuration =============================
    @app_commands.command(name="standard", description="Configura i canali principali del bot")
    async def standard(self, interaction: discord.Interaction) -> None:
        """Configura i canali principali del bot (communication, report, rule, live)"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel) if self.config.communication_channel else None
        
        try:
            # Defer la risposta immediatamente per evitare timeout
            await interaction.response.defer(ephemeral=True)
            
            selected_channels = await self._setup_standard_config(interaction)
            
            if selected_channels:
                await safe_send_message(interaction, '✅ Canali configurati con successo!', logger=self.log, log_command='COMMAND - CONFIG - STANDARD')
                await self.log.command('Configurazione canali principali completata.', 'config', 'STANDARD')
            else:
                await safe_send_message(interaction, '⚠️ Configurazione non completata o annullata.', logger=self.log, log_command='COMMAND - CONFIG - STANDARD')
            
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - STANDARD')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - STANDARD')
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - STANDARD')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - STANDARD')
            
        except Exception as e:
            error_message = f'Errore durante la configurazione dei canali: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - STANDARD')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - STANDARD')
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - STANDARD', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - CONFIG - STANDARD')
    
    @app_commands.command(name="retention", description="Configura il periodo di conservazione dei log")
    async def retention(self, interaction: discord.Interaction) -> None:
        """Configura il periodo di conservazione dei log (1, 2, 3, 6 mesi)"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel) if self.config.communication_channel else None
        
        try:
            retention_days = await self._setup_retention_config(interaction)
            if retention_days != "Non selezionato":
                await safe_send_message(interaction, f"✅ Periodo di conservazione aggiornato a {retention_days} giorni.", logger=self.log, log_command='COMMAND - CONFIG - RETENTION')
                await self.log.command(f'Periodo di conservazione aggiornato a {retention_days} giorni.', 'config', 'RETENTION')
            else:
                await safe_send_message(interaction, "Nessun periodo selezionato.", logger=self.log, log_command='COMMAND - CONFIG - RETENTION')
                
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - RETENTION')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - RETENTION')
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - RETENTION')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - RETENTION')
            
        except Exception as e:
            error_message = f'Errore durante l\'aggiornamento del periodo di conservazione: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - RETENTION')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - RETENTION')
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - RETENTION', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - CONFIG - RETENTION')
    
    @app_commands.command(name="message-logging", description="Configura la registrazione dei messaggi")
    async def message_logging(self, interaction: discord.Interaction) -> None:
        """Configura la registrazione dei messaggi e i canali di logging"""
        guild: discord.Guild = interaction.guild
        
        # Check if communication channel is configured
        if not self.config.communication_channel:
            await interaction.response.send_message(
                "❌ Canale di comunicazione non configurato. Configura prima il canale di comunicazione con `/config standard`.",
                ephemeral=True
            )
            return
            
        communication_channel = guild.get_channel(self.config.communication_channel)
        if not communication_channel:
            await interaction.response.send_message(
                f"❌ Canale di comunicazione (ID: {self.config.communication_channel}) non trovato. Verifica la configurazione.",
                ephemeral=True
            )
            return
        
        try:
            logging_enabled, logging_channels = await self._setup_message_logging_config(interaction)
            if logging_enabled != "Non selezionato":
                await safe_send_message(interaction, '✅ Configurazione logging completata!', logger=self.log, log_command='COMMAND - CONFIG - MESSAGE-LOGGING')
                await self.log.command('Configurazione logging messaggi completata.', 'config', 'MESSAGE-LOGGING')
            else:
                await safe_send_message(interaction, "Configurazione non completata.", logger=self.log, log_command='COMMAND - CONFIG - MESSAGE-LOGGING')
            
        except discord.NotFound as e:
            if "webhook" in str(e).lower():
                error_message = f'Errore webhook: Il canale di comunicazione potrebbe non essere configurato correttamente.\n{e}'
            else:
                error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - MESSAGE-LOGGING')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - MESSAGE-LOGGING')
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - MESSAGE-LOGGING')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - MESSAGE-LOGGING')
            
        except Exception as e:
            error_message = f'Errore durante la configurazione del logging: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - MESSAGE-LOGGING')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - MESSAGE-LOGGING')
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - MESSAGE-LOGGING', message=error_message))
                except Exception as comm_error:
                    # If we can't send to communication channel, just log it
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - CONFIG - MESSAGE-LOGGING')
    
    # ============================= Role Management =============================
    @app_commands.command(name="set-not-verified-role", description="Configura il ruolo 'not_verified'")
    async def set_not_verified_role(self, interaction: discord.Interaction) -> None:
        """Configura il ruolo per utenti non verificati"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel) if self.config.communication_channel else None
        
        try:
            view = NotVerifiedRoleSelect(author=interaction.user)
            await interaction.response.send_message(
                "Seleziona il ruolo 'not_verified' del server:",
                view=view,
                ephemeral=True
            )
            await view.wait()
            
            if view.selected_role_id:
                self.config.add_admin('roles', 'not_verified', view.selected_role_id)
                await safe_send_message(interaction, f"✅ Ruolo 'not_verified' configurato: <@&{view.selected_role_id}>", logger=self.log, log_command='COMMAND - CONFIG - SET-NOT-VERIFIED-ROLE')
                await self.log.command(f"Ruolo 'not_verified' configurato: {view.selected_role_id}", 'config', 'SET-NOT-VERIFIED-ROLE')
            else:
                await safe_send_message(interaction, "Nessun ruolo selezionato.", logger=self.log, log_command='COMMAND - CONFIG - SET-NOT-VERIFIED-ROLE')
                
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - SET-NOT-VERIFIED-ROLE')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - SET-NOT-VERIFIED-ROLE')
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - SET-NOT-VERIFIED-ROLE')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - SET-NOT-VERIFIED-ROLE')
            
        except Exception as e:
            error_message = f"Errore durante la configurazione del ruolo 'not_verified': {e}"
            await self.log.error(error_message, 'COMMAND - CONFIG - SET-NOT-VERIFIED-ROLE')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - SET-NOT-VERIFIED-ROLE')
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - SET-NOT-VERIFIED-ROLE', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - CONFIG - SET-NOT-VERIFIED-ROLE')
    
    @app_commands.command(name="set-booster-role", description="Configura il ruolo booster del server")
    async def set_booster_role(self, interaction: discord.Interaction) -> None:
        """Configura il ruolo per i server booster"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel) if self.config.communication_channel else None
        
        try:
            view = BoosterRoleSelect(author=interaction.user)
            await interaction.response.send_message(
                "Seleziona il ruolo booster del server:",
                view=view,
                ephemeral=True
            )
            await view.wait()
            
            if view.selected_role_id:
                self.config.add_admin('roles', 'server_booster', view.selected_role_id)
                await safe_send_message(interaction, f"✅ Ruolo booster configurato: <@&{view.selected_role_id}>", logger=self.log, log_command='COMMAND - CONFIG - SET-BOOSTER-ROLE')
                await self.log.command(f"Ruolo booster configurato: {view.selected_role_id}", 'config', 'SET-BOOSTER-ROLE')
            else:
                await safe_send_message(interaction, "Nessun ruolo selezionato.", logger=self.log, log_command='COMMAND - CONFIG - SET-BOOSTER-ROLE')
                
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - SET-BOOSTER-ROLE')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - SET-BOOSTER-ROLE')
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - SET-BOOSTER-ROLE')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - SET-BOOSTER-ROLE')
            
        except Exception as e:
            error_message = f'Errore durante la configurazione del ruolo booster: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - SET-BOOSTER-ROLE')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - SET-BOOSTER-ROLE')
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - SET-BOOSTER-ROLE', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - CONFIG - SET-BOOSTER-ROLE')
    
    @app_commands.command(name="verification-setup", description="Configura il sistema di verifica")
    async def verification_setup(self, interaction: discord.Interaction) -> None:
        """Configura il sistema di verifica con timeout e ruoli"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel) if self.config.communication_channel else None
        
        try:
            verification_data = await self._setup_verification_config(interaction)
            if verification_data["timeout"] != "Non selezionato":
                await safe_send_message(
                    interaction,
                    f"✅ Sistema di verifica configurato:\n"
                    f"⏱️ Timeout: {verification_data['timeout']}\n"
                    f"🛑 Ruolo temporaneo: {verification_data['temp_role']}\n"
                    f"✔️ Ruolo verificato: {verification_data['verified_role']}",
                    logger=self.log,
                    log_command='COMMAND - CONFIG - VERIFICATION-SETUP'
                )
                
                await self.log.command(f'Sistema di verifica configurato: timeout={verification_data["timeout"]}, temp_role={verification_data["temp_role"]}, verified_role={verification_data["verified_role"]}', 'config', 'VERIFICATION-SETUP')
            else:
                await safe_send_message(interaction, "Configurazione non completata.", logger=self.log, log_command='COMMAND - CONFIG - VERIFICATION-SETUP')
                
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - VERIFICATION-SETUP')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - VERIFICATION-SETUP')
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - VERIFICATION-SETUP')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - VERIFICATION-SETUP')
            
        except Exception as e:
            error_message = f'Errore durante la configurazione del sistema di verifica: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - VERIFICATION-SETUP')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - VERIFICATION-SETUP')
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - VERIFICATION-SETUP', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - CONFIG - VERIFICATION-SETUP')
    
    # ============================= Admin Management =============================
    @app_commands.command(name="admin-check", description="Visualizza i dati di configurazione admin")
    async def admin_check(self, interaction: discord.Interaction) -> None:
        """Visualizza tutti i dati inseriti nella configurazione admin"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel) if self.config.communication_channel else None
        
        try:
            admin_data: dict = self.config.load_admin()
            tags: list = [tag for tag in admin_data.keys()]
            
            view: AdminCheckView = AdminCheckView(author=interaction.user, tags=tags)
            await interaction.response.send_message("Seleziona la sezione da visualizzare:", view=view, ephemeral=True)
            await view.wait()
            
            selected_tag: str = view.selected_tag
            selected_data: dict = self.config.load_admin(section=selected_tag)
            
            description: str = ''
            if selected_tag == 'roles':
                for tag, role_id in selected_data.items():
                    role: discord.Role = guild.get_role(int(role_id))
                    description += f'\n**{tag}**: {role.mention} ({role_id})'
            elif selected_tag == 'channels':
                for tag, channel_id in selected_data.items():
                    channel: discord.TextChannel = guild.get_channel(int(channel_id))
                    description += f'\n**{tag}**: {channel.mention} ({channel_id})'
            
            embed_data: dict = {
                'title': f'Configurazione Admin - {selected_tag.capitalize()}',
                'description': description,
                'color': self.bot.color
            }
            embed: discord.Embed = create_embed_from_dict(embed_data)
            await safe_send_message(interaction, embed=embed, logger=self.log, log_command='COMMAND - CONFIG - ADMIN-CHECK')
            
            await self.log.command(f'Visualizzati dati admin per: {selected_tag}', 'config', 'ADMIN-CHECK')
            
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - ADMIN-CHECK')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - ADMIN-CHECK')
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - ADMIN-CHECK')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - ADMIN-CHECK')
            
        except Exception as e:
            error_message = f'Errore durante la visualizzazione dei dati admin: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - ADMIN-CHECK')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - ADMIN-CHECK')
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - ADMIN-CHECK', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - CONFIG - ADMIN-CHECK')
    
    @app_commands.command(name="admin-add", description="Aggiunge un ruolo o canale alla configurazione admin")
    async def admin_add(self, interaction: discord.Interaction) -> None:
        """Aggiunge un ruolo o canale alla configurazione admin"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel) if self.config.communication_channel else None
        
        try:
            admin_data: dict = self.config.load_admin()
            tags: list = [tag for tag in admin_data.keys()]
            
            view: AdminAddView = AdminAddView(author=interaction.user, tags=tags)
            await interaction.response.send_message("Configura un nuovo elemento admin:", view=view, ephemeral=True)
            await view.wait()
            
            config_tag: str = view.selected_tag
            tag: str = view.new_tag
            value: str = f'{view.values[0]}'
            
            await safe_send_message(
                interaction,
                f"Dati inseriti:\n"
                f"📁 Sezione: {config_tag}\n"
                f"🏷️ Tag: {tag}\n"
                f"🆔 ID: {value}",
                logger=self.log,
                log_command='COMMAND - CONFIG - ADMIN-ADD'
            )
            
            self.config.add_admin(config_tag, tag, value)
            if config_tag == 'channels' and tag == 'communication':
                self.config._load_communication_channel()
            
            await safe_send_message(interaction, '✅ Dati salvati con successo!', logger=self.log, log_command='COMMAND - CONFIG - ADMIN-ADD')
            await self.log.command(f'Nuovo elemento aggiunto a config/admin: {config_tag}/{tag}={value}', 'config', 'ADMIN-ADD')
            
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - ADMIN-ADD')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - ADMIN-ADD')
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - ADMIN-ADD')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - ADMIN-ADD')
            
        except Exception as e:
            error_message = f'Errore durante l\'aggiunta di dati admin: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - ADMIN-ADD')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - ADMIN-ADD')
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - ADMIN-ADD', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - CONFIG - ADMIN-ADD')
    
    @app_commands.command(name="exception-add", description="Aggiunge eccezioni per ruoli o canali")
    async def exception_add(self, interaction: discord.Interaction) -> None:
        """Aggiunge una lista di ruoli o canali alle eccezioni"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel) if self.config.communication_channel else None
        
        try:            
            view: ExceptionView = ExceptionView(author=interaction.user)
            await interaction.response.send_message("Aggiungi un'eccezione:", view=view, ephemeral=True)
            await view.wait()

            tag: str = view.tag
            values: list[int] = view.values
            
            await safe_send_message(
                interaction,
                f"Dati inseriti:\n"
                f"🏷️ Tag: {tag}\n"
                f"📋 Tipologia: {view.type}\n"
                f"🆔 ID: {values}",
                logger=self.log,
                log_command='COMMAND - CONFIG - EXCEPTION-ADD'
            )
            
            self.config.add_exception(tag, values)
            await safe_send_message(interaction, '✅ Eccezione aggiunta con successo!', logger=self.log, log_command='COMMAND - CONFIG - EXCEPTION-ADD')
            await self.log.command(f'Eccezione aggiunta: tag={tag}, values={values}', 'config', 'EXCEPTION-ADD')

        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - EXCEPTION-ADD')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - EXCEPTION-ADD')
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - EXCEPTION-ADD')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - EXCEPTION-ADD')
            
        except Exception as e:
            error_message = f'Errore durante l\'aggiunta dell\'eccezione: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - EXCEPTION-ADD')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - EXCEPTION-ADD')
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - EXCEPTION-ADD', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - CONFIG - EXCEPTION-ADD')
    
    # ============================= Twitch Configuration =============================
    @app_commands.command(name="twitch-titles", description="Configura i titoli Twitch per stream on/off")
    async def twitch_titles(self, interaction: discord.Interaction) -> None:
        """Configura i titoli Twitch per quando lo stream è attivo o inattivo"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel) if self.config.communication_channel else None
        
        try:
            twitch_titles = await self._setup_twitch_titles_config(interaction)
            if twitch_titles["on"] != "Non selezionato":
                await safe_send_message(
                    interaction,
                    f"✅ Titoli Twitch configurati:\n"
                    f"🟢 ON: {twitch_titles['on']}\n"
                    f"🔴 OFF: {twitch_titles['off']}",
                    logger=self.log,
                    log_command='COMMAND - CONFIG - TWITCH-TITLES'
                )
                await self.log.command(f'Titoli Twitch configurati: ON="{twitch_titles["on"]}", OFF="{twitch_titles["off"]}"', 'config', 'TWITCH-TITLES')
            else:
                await safe_send_message(interaction, "Configurazione titoli non completata.", logger=self.log, log_command='COMMAND - CONFIG - TWITCH-TITLES')
                
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - TWITCH-TITLES')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - TWITCH-TITLES')
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - TWITCH-TITLES')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - TWITCH-TITLES')
            
        except Exception as e:
            error_message = f'Errore durante la configurazione dei titoli Twitch: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - TWITCH-TITLES')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - TWITCH-TITLES')
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - TWITCH-TITLES', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - CONFIG - TWITCH-TITLES')
    
    @app_commands.command(name="twitch-streamer", description="Configura il nome dello streamer Twitch")
    async def twitch_streamer(self, interaction: discord.Interaction) -> None:
        """Configura il nome dello streamer Twitch"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel) if self.config.communication_channel else None
        
        try:
            streamer_name = await self._setup_twitch_streamer_config(interaction)
            if streamer_name != "Non selezionato":
                await safe_send_message(
                    interaction,
                    f"✅ Streamer Twitch configurato: **{streamer_name}**",
                    logger=self.log,
                    log_command='COMMAND - CONFIG - TWITCH-STREAMER'
                )
                await self.log.command(f'Streamer Twitch configurato: {streamer_name}', 'config', 'TWITCH-STREAMER')
            else:
                await safe_send_message(interaction, "Nome streamer non inserito.", logger=self.log, log_command='COMMAND - CONFIG - TWITCH-STREAMER')
                
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - TWITCH-STREAMER')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - TWITCH-STREAMER')
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - TWITCH-STREAMER')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - TWITCH-STREAMER')
            
        except Exception as e:
            error_message = f'Errore durante la configurazione dello streamer Twitch: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - TWITCH-STREAMER')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - TWITCH-STREAMER')
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - TWITCH-STREAMER', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - CONFIG - TWITCH-STREAMER')
    
    @app_commands.command(name="twitch-add-tag", description="Aggiunge un nuovo tag per le live e immagini")
    async def add_tag(self, interaction: discord.Interaction) -> None:
        """Aggiunge un nuovo tag per le live e la scelta delle immagini"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel)
        
        try:
            modal = TagModal()
            await interaction.response.send_modal(modal)
            await modal.wait()
            
            if not getattr(modal, 'selection_complete', False):
                await safe_send_message(interaction, "Selezione non confermata o tempo scaduto.", logger=self.log, log_command='COMMAND - CONFIG - ADD-TAG')
                return
            
            await safe_send_message(
                interaction,
                f'🏷️ Tag: {modal.tag}\n'
                f'🌌 URL immagine: {modal.url}',
                ephemeral=True,
                logger=self.log,
                log_command='COMMAND - CONFIG - ADD-TAG'
            )
            
            data: dict = {
                'tag': f'{modal.tag}',
                'url': f'{modal.url}'
            }
            
            self.twitch_app.add_image(data)
            await safe_send_message(interaction, '✅ Tag aggiunto con successo!', logger=self.log, log_command='COMMAND - CONFIG - ADD-TAG')
            await self.log.command(f'Nuovo tag aggiunto: {data["tag"]} -> {data["url"]}', 'config', 'ADD-TAG')
            
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - ADD-TAG')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - ADD-TAG')
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - ADD-TAG')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - ADD-TAG')
            
        except Exception as e:
            error_message = f'Errore durante l\'aggiunta del tag: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - ADD-TAG')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - ADD-TAG')
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - ADD-TAG', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - CONFIG - ADD-TAG')
    
    @app_commands.command(name="twitch-reset-info", description="Reset delle informazioni dell'ultima stream")
    async def reset_info(self, interaction: discord.Interaction) -> None:
        """Reset delle informazioni riguardanti l'ultima stream"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel)
        
        try:
            self.twitch_app.set_default_stream_info()
            await safe_send_message(interaction, '✅ Informazioni della stream resettate!', logger=self.log, log_command='COMMAND - CONFIG - RESET-INFO')
            await self.log.command('Reset informazioni ultima stream completato', 'config', 'RESET-INFO')

        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - RESET-INFO')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - RESET-INFO')
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - RESET-INFO')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - RESET-INFO')
            
        except Exception as e:
            error_message = f'Errore durante il reset delle informazioni stream: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - RESET-INFO')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - RESET-INFO')
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - RESET-INFO', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - CONFIG - RESET-INFO')
    
    # ============================= Setup Wizard =============================
    @app_commands.command(name="setup-iniziale", description="Esegui la configurazione iniziale completa del bot")
    async def setup_iniziale(self, interaction: discord.Interaction) -> None:
        """Esegue la configurazione iniziale completa del bot"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel) if self.config.communication_channel else None
        try:
            # Step 1: Standard configuration (channels)
            await self._setup_standard_config(interaction)
            
            # Step 2: Verification setup
            await self._setup_verification_config(interaction)
            
            # Step 3: Retention days
            await self._setup_retention_config(interaction)
            
            # Step 4: Message logging
            await self._setup_message_logging_config(interaction)
            
            # Step 5: Twitch titles
            await self._setup_twitch_titles_config(interaction)
            
            # Step 6: Twitch streamer name
            await self._setup_twitch_streamer_config(interaction)
            
            # Final recap
            await self._send_setup_recap(interaction)
            
            await self.log.command('Configurazione iniziale completata.', 'config', 'SETUP-INIZIALE')
            
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - SETUP-INIZIALE')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - SETUP-INIZIALE')
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - SETUP-INIZIALE')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - SETUP-INIZIALE')
            
        except Exception as e:
            error_message = f'Errore durante la configurazione iniziale: {e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - SETUP-INIZIALE')
            await safe_send_message(interaction, f"❌ {error_message}", logger=self.log, log_command='COMMAND - CONFIG - SETUP-INIZIALE')
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - SETUP-INIZIALE', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - CONFIG - SETUP-INIZIALE')
    
    # ============================= Private Setup Methods =============================
    async def _setup_standard_config(self, interaction: discord.Interaction) -> dict:
        """Setup standard configuration (channels)"""
        try:
            admin_channels: dict = self.config.load_admin('channels')
            
            # Controlla se ci sono canali da configurare
            if not admin_channels:
                await interaction.followup.send(
                    "❌ Nessun canale da configurare trovato. Verifica la configurazione admin.",
                    ephemeral=True
                )
                return {}
            
            view_standard = StandardView(
                author=interaction.user,
                tags=list(admin_channels.keys())
            )
            
            await interaction.followup.send(
                "Step 1/6: Seleziona i canali principali.\n\n"
                "💡 **Istruzioni:**\n"
                "• Seleziona un canale per ogni sezione\n"
                "• Usa i bottoni di navigazione se ci sono più pagine\n"
                "• Clicca 'Conferma' quando hai finito",
                view=view_standard,
                ephemeral=True
            )
            
            # Aspetta che la view sia completata o timeout
            await view_standard.wait()
            
            selected_channels = {}
            if hasattr(view_standard, 'confirmed') and view_standard.confirmed:
                for tag, channel_id in view_standard.values.items():
                    self.config.add_admin('channels', tag, channel_id)
                    if tag == 'communication':
                        self.config._load_communication_channel()
                    selected_channels[tag] = channel_id
                
                await interaction.followup.send(
                    f"✅ Configurazione completata! Configurati {len(selected_channels)} canali.",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    "⏰ Timeout o configurazione annullata.",
                    ephemeral=True
                )
            
            return selected_channels
            
        except Exception as e:
            await interaction.followup.send(
                f"❌ Errore durante la configurazione: {str(e)}",
                ephemeral=True
            )
            return {}
    
    async def _setup_verification_config(self, interaction: discord.Interaction) -> dict:
        """Setup verification configuration"""
        view_nv_verif = NotVerifiedAndVerificationSetupView(author=interaction.user)
        await interaction.followup.send(
            "Step 2/6: Seleziona il ruolo 'not_verified' e configura la verifica (timeout, ruoli)",
            view=view_nv_verif,
            ephemeral=True
        )
        await view_nv_verif.wait()
        
        verification_data = {"timeout": "Non selezionato", "temp_role": "Non selezionato", "verified_role": "Non selezionato"}
        if view_nv_verif.selection_complete:
            # Salva not_verified
            self.config.add_admin('roles', 'not_verified', view_nv_verif.not_verified_role.id)
            # Salva verifica
            self.config.add_admin('roles', 'in_verification', view_nv_verif.temp_role.id)
            self.config.add_admin('roles', 'verified', view_nv_verif.verified_role.id)
            self.verification.update_timeout(view_nv_verif.timeout)
            verification_data['timeout'] = f"{view_nv_verif.timeout} secondi"
            verification_data['temp_role'] = view_nv_verif.temp_role.mention
            verification_data['verified_role'] = view_nv_verif.verified_role.mention
        
        return verification_data
    
    async def _setup_retention_config(self, interaction: discord.Interaction) -> str:
        """Setup retention configuration"""
        view_retention = RetentionSelectView(author=interaction.user)
        await interaction.followup.send(
            "Step 3/6: Seleziona il periodo di conservazione dei log:",
            view=view_retention,
            ephemeral=True
        )
        await view_retention.wait()
        
        retention_days = "Non selezionato"
        if view_retention.selection_complete and view_retention.selected_days:
            self.config.update_retention_days(view_retention.selected_days)
            retention_days = view_retention.selected_days
        
        return retention_days
    
    async def _setup_message_logging_config(self, interaction: discord.Interaction) -> tuple:
        """Setup message logging configuration"""
        try:
            view_logging = MessageLoggingView(author=interaction.user)
            
            # Use response.send_message instead of followup.send to avoid webhook issues
            await interaction.response.send_message(
                "Step 4/6: Configura la registrazione dei messaggi.",
                view=view_logging,
                ephemeral=True
            )
            await view_logging.wait()
            
            logging_enabled = "Non selezionato"
            logging_channels = []
            
            if view_logging.selected_enabled is not None:
                if view_logging.selected_enabled:
                    self.config.enable_message_logging()
                    logging_enabled = "Abilitata"
                else:
                    self.config.disable_message_logging()
                    logging_enabled = "Disabilitata"
                
                for channel_id in view_logging.selected_channels:
                    try:
                        self.config.add_message_logging_channel(channel_id)
                        channel = interaction.guild.get_channel(channel_id)
                        if channel:
                            logging_channels.append(channel.mention)
                        else:
                            logging_channels.append(f"ID: {channel_id} (canale non trovato)")
                    except Exception as e:
                        # Log error but continue with other channels
                        await self.log.error(f'Errore nell\'aggiunta del canale {channel_id}: {e}', 'CONFIG-MESSAGE-LOGGING')
                        logging_channels.append(f"ID: {channel_id} (errore)")
            
            return logging_enabled, logging_channels
            
        except discord.NotFound as e:
            if "webhook" in str(e).lower():
                # If webhook is invalid, try to send a new response
                try:
                    await interaction.followup.send("⚠️ Errore webhook. Riprovando...", ephemeral=True)
                except:
                    # If even followup fails, try to send a new response
                    try:
                        await interaction.response.send_message("⚠️ Errore webhook. Riprovando...", ephemeral=True)
                    except:
                        pass
            raise e
        except Exception as e:
            # Log the specific error
            await self.log.error(f'Errore nella configurazione del message logging: {e}', 'CONFIG-MESSAGE-LOGGING')
            raise e
    
    async def _setup_twitch_titles_config(self, interaction: discord.Interaction) -> dict:
        """Setup Twitch titles configuration"""
        view_titles = TwitchTitlesView(author=interaction.user)
        await interaction.followup.send(
            "Step 5/6: Imposta i titoli Twitch (on/off).",
            view=view_titles,
            ephemeral=True
        )
        await view_titles.wait()
        
        twitch_titles = {"on": "Non selezionato", "off": "Non selezionato"}
        if view_titles.titles:
            self.twitch_app.change_title({'tag': 'on', 'title': view_titles.titles['on']})
            self.twitch_app.change_title({'tag': 'off', 'title': view_titles.titles['off']})
            twitch_titles['on'] = view_titles.titles['on']
            twitch_titles['off'] = view_titles.titles['off']
        
        return twitch_titles
    
    async def _setup_twitch_streamer_config(self, interaction: discord.Interaction) -> str:
        """Setup Twitch streamer configuration"""
        view_streamer = StreamerNameView(author=interaction.user)
        await interaction.followup.send(
            "Step 6/6: Inserisci il nome dello streamer Twitch.",
            view=view_streamer,
            ephemeral=True
        )
        await view_streamer.wait()
        
        streamer_name = "Non selezionato"
        if view_streamer.streamer_name:
            self.twitch_app.change_streamer_name(view_streamer.streamer_name)
            streamer_name = view_streamer.streamer_name
        
        return streamer_name
    
    async def _send_setup_recap(self, interaction: discord.Interaction) -> None:
        """Send final setup recap"""
        recap = """🎉 **Configurazione iniziale completata!**

Tutti i passaggi sono stati completati con successo. Il bot è ora configurato e pronto all'uso."""
        
        await interaction.followup.send(recap, ephemeral=True)