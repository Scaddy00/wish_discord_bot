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
from utils.printing import create_embed_from_dict
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
    
    # ============================= Core Configuration =============================
    @app_commands.command(name="standard", description="Configura i canali principali del bot")
    async def standard(self, interaction: discord.Interaction) -> None:
        """Configura i canali principali del bot (communication, report, rule, live)"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel) if self.config.communication_channel else None
        
        try:
            admin_channels: dict = self.config.load_admin('channels')
            view: StandardView = StandardView(
                author=interaction.user,
                tags=admin_channels.keys()
            )
            await interaction.response.send_message(
                "Seleziona i canali principali del bot",
                view=view,
                ephemeral=True
            )
            await view.wait()
            
            # Save selected channels
            for tag, channel_id in view.values.items():
                self.config.add_admin('channels', tag, channel_id)
                if tag == 'communication':
                    self.config._load_communication_channel()
            
            await interaction.followup.send('✅ Canali configurati con successo!', ephemeral=True)
            await self.log.command('Configurazione canali principali completata.', 'config', 'STANDARD')
            
        except Exception as e:
            error_message = f'Errore durante la configurazione dei canali.\n{e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - STANDARD')
            if communication_channel:
                await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - STANDARD', message=error_message))
    
    @app_commands.command(name="retention", description="Configura il periodo di conservazione dei log")
    async def retention(self, interaction: discord.Interaction) -> None:
        """Configura il periodo di conservazione dei log (1, 2, 3, 6 mesi)"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel) if self.config.communication_channel else None
        
        try:
            view = RetentionSelectView(author=interaction.user)
            await interaction.response.send_message(
                "Seleziona il periodo di conservazione dei log:",
                view=view,
                ephemeral=True
            )
            await view.wait()
            
            if view.selection_complete and view.selected_days:
                self.config.update_retention_days(view.selected_days)
                await interaction.followup.send(f"✅ Periodo di conservazione aggiornato a {view.selected_days} giorni.", ephemeral=True)
                await self.log.command(f'Periodo di conservazione aggiornato a {view.selected_days} giorni.', 'config', 'RETENTION')
            else:
                await interaction.followup.send("Nessun periodo selezionato.", ephemeral=True)
                
        except Exception as e:
            error_message = f'Errore durante l\'aggiornamento del periodo di conservazione.\n{e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - RETENTION')
            if communication_channel:
                await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - RETENTION', message=error_message))
    
    @app_commands.command(name="message-logging", description="Configura la registrazione dei messaggi")
    async def message_logging(self, interaction: discord.Interaction) -> None:
        """Configura la registrazione dei messaggi e i canali di logging"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel) if self.config.communication_channel else None
        
        try:
            message_logging_data: dict = self.config.load_message_logging()
            view: MessageLoggingView = MessageLoggingView(author=interaction.user)
            
            await interaction.response.send_message(
                f"Configura la registrazione dei messaggi.\nAl momento è {'**abilitata**' if message_logging_data['enabled'] else '**disabilitata**'}.",
                view=view,
                ephemeral=True
            )
            await view.wait()
            
            if view.selected_enabled is not None:
                if view.selected_enabled:
                    self.config.enable_message_logging()
                else:
                    self.config.disable_message_logging()
                
                for channel_id in view.selected_channels:
                    self.config.add_message_logging_channel(channel_id)
                
                await interaction.followup.send('✅ Configurazione logging completata!', ephemeral=True)
                await self.log.command('Configurazione logging messaggi completata.', 'config', 'MESSAGE-LOGGING')
            else:
                await interaction.followup.send("Configurazione non completata.", ephemeral=True)
            
        except Exception as e:
            error_message = f'Errore durante la configurazione del logging.\n{e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - MESSAGE-LOGGING')
            if communication_channel:
                await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - MESSAGE-LOGGING', message=error_message))
    
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
                await interaction.followup.send(f"✅ Ruolo 'not_verified' configurato: <@&{view.selected_role_id}>", ephemeral=True)
                await self.log.command(f"Ruolo 'not_verified' configurato: {view.selected_role_id}", 'config', 'SET-NOT-VERIFIED-ROLE')
            else:
                await interaction.followup.send("Nessun ruolo selezionato.", ephemeral=True)
                
        except Exception as e:
            error_message = f"Errore durante la configurazione del ruolo 'not_verified'.\n{e}"
            await self.log.error(error_message, 'COMMAND - CONFIG - SET-NOT-VERIFIED-ROLE')
            if communication_channel:
                await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - SET-NOT-VERIFIED-ROLE', message=error_message))
    
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
                await interaction.followup.send(f"✅ Ruolo booster configurato: <@&{view.selected_role_id}>", ephemeral=True)
                await self.log.command(f"Ruolo booster configurato: {view.selected_role_id}", 'config', 'SET-BOOSTER-ROLE')
            else:
                await interaction.followup.send("Nessun ruolo selezionato.", ephemeral=True)
                
        except Exception as e:
            error_message = f'Errore durante la configurazione del ruolo booster.\n{e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - SET-BOOSTER-ROLE')
            if communication_channel:
                await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - SET-BOOSTER-ROLE', message=error_message))
    
    @app_commands.command(name="verification-setup", description="Configura il sistema di verifica")
    async def verification_setup(self, interaction: discord.Interaction) -> None:
        """Configura il sistema di verifica con timeout e ruoli"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel) if self.config.communication_channel else None
        
        try:
            view = NotVerifiedAndVerificationSetupView(author=interaction.user)
            await interaction.response.send_message(
                "Configura il sistema di verifica: timeout, ruolo temporaneo e ruolo verificato.",
                view=view,
                ephemeral=True
            )
            await view.wait()
            
            if view.selection_complete:
                self.config.add_admin('roles', 'in_verification', view.temp_role.id)
                self.config.add_admin('roles', 'verified', view.verified_role.id)
                self.verification.update_timeout(view.timeout)
                
                await interaction.followup.send(
                    f"✅ Sistema di verifica configurato:\n"
                    f"⏱️ Timeout: {view.timeout} secondi\n"
                    f"🛑 Ruolo temporaneo: {view.temp_role.mention}\n"
                    f"✔️ Ruolo verificato: {view.verified_role.mention}",
                    ephemeral=True
                )
                
                await self.log.command(f'Sistema di verifica configurato: timeout={view.timeout}s, temp_role={view.temp_role.id}, verified_role={view.verified_role.id}', 'config', 'VERIFICATION-SETUP')
            else:
                await interaction.followup.send("Configurazione non completata.", ephemeral=True)
                
        except Exception as e:
            error_message = f'Errore durante la configurazione del sistema di verifica.\n{e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - VERIFICATION-SETUP')
            if communication_channel:
                await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - VERIFICATION-SETUP', message=error_message))
    
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
            await interaction.followup.send(embed=embed)
            
            await self.log.command(f'Visualizzati dati admin per: {selected_tag}', 'config', 'ADMIN-CHECK')
            
        except Exception as e:
            error_message = f'Errore durante la visualizzazione dei dati admin.\n{e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - ADMIN-CHECK')
            if communication_channel:
                await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - ADMIN-CHECK', message=error_message))
    
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
            
            await interaction.followup.send(
                f"Dati inseriti:\n"
                f"📁 Sezione: {config_tag}\n"
                f"🏷️ Tag: {tag}\n"
                f"🆔 ID: {value}",
                ephemeral=True
            )
            
            self.config.add_admin(config_tag, tag, value)
            if config_tag == 'channels' and tag == 'communication':
                self.config._load_communication_channel()
            
            await interaction.followup.send('✅ Dati salvati con successo!', ephemeral=True)
            await self.log.command(f'Nuovo elemento aggiunto a config/admin: {config_tag}/{tag}={value}', 'config', 'ADMIN-ADD')
            
        except Exception as e:
            error_message = f'Errore durante l\'aggiunta di dati admin.\n{e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - ADMIN-ADD')
            if communication_channel:
                await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - ADMIN-ADD', message=error_message))
    
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
            
            await interaction.followup.send(
                f"Dati inseriti:\n"
                f"🏷️ Tag: {tag}\n"
                f"📋 Tipologia: {view.type}\n"
                f"🆔 ID: {values}",
                ephemeral=True
            )
            
            self.config.add_exception(tag, values)
            await interaction.followup.send('✅ Eccezione aggiunta con successo!', ephemeral=True)
            await self.log.command(f'Eccezione aggiunta: tag={tag}, values={values}', 'config', 'EXCEPTION-ADD')

        except Exception as e:
            error_message = f'Errore durante l\'aggiunta dell\'eccezione.\n{e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - EXCEPTION-ADD')
            if communication_channel:
                await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - EXCEPTION-ADD', message=error_message))
    
    # ============================= Twitch Configuration =============================
    @app_commands.command(name="twitch-titles", description="Configura i titoli Twitch per stream on/off")
    async def twitch_titles(self, interaction: discord.Interaction) -> None:
        """Configura i titoli Twitch per quando lo stream è attivo o inattivo"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel) if self.config.communication_channel else None
        
        try:
            view = TwitchTitlesView(author=interaction.user)
            await interaction.response.send_message(
                "Configura i titoli Twitch per stream on/off:",
                view=view,
                ephemeral=True
            )
            await view.wait()
            
            if view.titles:
                self.twitch_app.change_title({'tag': 'on', 'title': view.titles['on']})
                self.twitch_app.change_title({'tag': 'off', 'title': view.titles['off']})
                
                await interaction.followup.send(
                    f"✅ Titoli Twitch configurati:\n"
                    f"🟢 ON: {view.titles['on']}\n"
                    f"🔴 OFF: {view.titles['off']}",
                    ephemeral=True
                )
                
                await self.log.command(f'Titoli Twitch configurati: ON="{view.titles["on"]}", OFF="{view.titles["off"]}"', 'config', 'TWITCH-TITLES')
            else:
                await interaction.followup.send("Configurazione titoli non completata.", ephemeral=True)
                
        except Exception as e:
            error_message = f'Errore durante la configurazione dei titoli Twitch.\n{e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - TWITCH-TITLES')
            if communication_channel:
                await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - TWITCH-TITLES', message=error_message))
    
    @app_commands.command(name="twitch-streamer", description="Configura il nome dello streamer Twitch")
    async def twitch_streamer(self, interaction: discord.Interaction) -> None:
        """Configura il nome dello streamer Twitch"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel) if self.config.communication_channel else None
        
        try:
            view = StreamerNameView(author=interaction.user)
            await interaction.response.send_message(
                "Inserisci il nome dello streamer Twitch:",
                view=view,
                ephemeral=True
            )
            await view.wait()
            
            if view.streamer_name:
                self.twitch_app.change_streamer_name(view.streamer_name)
                
                await interaction.followup.send(
                    f"✅ Streamer Twitch configurato: **{view.streamer_name}**",
                    ephemeral=True
                )
                
                await self.log.command(f'Streamer Twitch configurato: {view.streamer_name}', 'config', 'TWITCH-STREAMER')
            else:
                await interaction.followup.send("Nome streamer non inserito.", ephemeral=True)
                
        except Exception as e:
            error_message = f'Errore durante la configurazione dello streamer Twitch.\n{e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - TWITCH-STREAMER')
            if communication_channel:
                await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - TWITCH-STREAMER', message=error_message))
    
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
                await interaction.followup.send("Selezione non confermata o tempo scaduto.")
                return
            
            await interaction.followup.send(
                f'🏷️ Tag: {modal.tag}\n'
                f'🌌 URL immagine: {modal.url}',
                ephemeral=True
            )
            
            data: dict = {
                'tag': f'{modal.tag}',
                'url': f'{modal.url}'
            }
            
            self.twitch_app.add_image(data)
            await interaction.followup.send('✅ Tag aggiunto con successo!', ephemeral=True)
            await self.log.command(f'Nuovo tag aggiunto: {data["tag"]} -> {data["url"]}', 'config', 'ADD-TAG')
            
        except Exception as e:
            error_message = f'Errore durante l\'aggiunta del tag.\n{e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - ADD-TAG')
            await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - ADD-TAG', message=error_message))
    
    @app_commands.command(name="twitch-reset-info", description="Reset delle informazioni dell'ultima stream")
    async def reset_info(self, interaction: discord.Interaction) -> None:
        """Reset delle informazioni riguardanti l'ultima stream"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel)
        
        try:
            self.twitch_app.set_default_stream_info()
            await interaction.response.send_message('✅ Informazioni della stream resettate!', ephemeral=True)
            await self.log.command('Reset informazioni ultima stream completato', 'config', 'RESET-INFO')

        except Exception as e:
            error_message = f'Errore durante il reset delle informazioni stream.\n{e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - RESET-INFO')
            await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - RESET-INFO', message=error_message))
    
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
            
        except Exception as e:
            error_message = f'Errore durante la configurazione iniziale.\n{e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - SETUP-INIZIALE')
            if communication_channel:
                await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - SETUP-INIZIALE', message=error_message))
    
    # ============================= Private Setup Methods =============================
    async def _setup_standard_config(self, interaction: discord.Interaction) -> dict:
        """Setup standard configuration (channels)"""
        admin_channels: dict = self.config.load_admin('channels')
        view_standard = StandardView(
            author=interaction.user,
            tags=admin_channels.keys()
        )
        await interaction.followup.send(
            "Step 1/6: Seleziona i canali principali.",
            view=view_standard,
            ephemeral=True
        )
        await view_standard.wait()
        
        selected_channels = {}
        for tag, channel_id in view_standard.values.items():
            self.config.add_admin('channels', tag, channel_id)
            if tag == 'communication':
                self.config._load_communication_channel()
            selected_channels[tag] = channel_id
        
        return selected_channels
    
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
        view_logging = MessageLoggingView(author=interaction.user)
        await interaction.followup.send(
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
                self.config.add_message_logging_channel(channel_id)
                channel = interaction.guild.get_channel(channel_id)
                logging_channels.append(channel.mention if channel else f"ID: {channel_id}")
        
        return logging_enabled, logging_channels
    
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