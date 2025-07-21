# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from discord import app_commands
from os import getenv
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from config_manager import ConfigManager
from cogs.modals.config.exception_view import SetupView as ExceptionView
from cogs.modals.config.admin_check_view import SetupView as AdminCheckView
from cogs.modals.config.admin_add_view import SetupView as AdminAddView
from cogs.modals.config.standard_view import SetupView as StandardView
from cogs.modals.config.message_logging_view import SetupView as MessageLoggingView
from cogs.modals.config.retention_select_view import RetentionSelectView
from cogs.twitch.views_modals.titles_view import TwitchTitlesView
from cogs.twitch.views_modals.streamer_name_view import StreamerNameView
from utils.printing import create_embed_from_dict
from cogs.modals.config.booster_role_select_view import BoosterRoleSelect
from cogs.verification.verification_setup_view import SetupView as VerificationSetupView
from discord.ui import View, Select, RoleSelect, Button
from discord import SelectOption

class NotVerifiedRoleSelect(discord.ui.View):
    """
    View for selecting the 'not_verified' role using RoleSelect.
    """
    def __init__(self, author: discord.User):
        super().__init__(timeout=60)
        self.author = author
        self.selected_role_id = None
        self.add_item(self.NotVerifiedRoleDropdown(self))

    class NotVerifiedRoleDropdown(discord.ui.RoleSelect):
        def __init__(self, parent_view):
            super().__init__(placeholder="Seleziona il ruolo 'not_verified'", min_values=1, max_values=1)
            self.parent_view = parent_view
        async def callback(self, interaction: discord.Interaction):
            if interaction.user.id != self.parent_view.author.id:
                await interaction.response.send_message("Questa selezione non ti appartiene.", ephemeral=True)
                return
            selected_role = self.values[0]
            self.parent_view.selected_role_id = str(selected_role.id)
            await interaction.response.send_message(f"Ruolo 'not_verified' selezionato: {selected_role.mention}", ephemeral=True)
            self.parent_view.stop()

class NotVerifiedAndVerificationSetupView(View):
    def __init__(self, author: discord.User):
        super().__init__(timeout=180)
        self.author = author
        self.selection_complete = False
        self.not_verified_role: discord.Role = None
        self.timeout: int = None
        self.temp_role: discord.Role = None
        self.verified_role: discord.Role = None

        # Not verified role select
        self.not_verified_select = RoleSelect(
            placeholder="Seleziona il ruolo 'not_verified'",
            custom_id="not_verified_role_select",
            min_values=1,
            max_values=1,
            row=0
        )
        self.not_verified_select.callback = self.not_verified_callback
        self.add_item(self.not_verified_select)

        # Timeout select
        select_timeout: Select = Select(
            placeholder="Seleziona timeout verifica",
            custom_id="timeout_select",
            options=[
                SelectOption(label="5 minuti", value="300"),
                SelectOption(label="10 minuti", value="600"),
                SelectOption(label="15 minuti", value="900"),
                SelectOption(label="30 minuti", value="1800"),
            ],
            row=1
        )
        select_timeout.callback = self.timeout_callback
        self.add_item(select_timeout)

        # Temp role select
        self.temp_role_select = RoleSelect(
            placeholder="Seleziona ruolo temporaneo",
            custom_id="temp_role_select",
            min_values=1,
            max_values=1,
            row=2
        )
        self.temp_role_select.callback = self.temp_role_callback
        self.add_item(self.temp_role_select)

        # Verified role select
        self.verified_role_select = RoleSelect(
            placeholder="Seleziona ruolo verificato",
            custom_id="verified_role_select",
            min_values=1,
            max_values=1,
            row=3
        )
        self.verified_role_select.callback = self.verified_role_callback
        self.add_item(self.verified_role_select)

        # Confirm button
        button_confirm = Button(
            label="Conferma",
            style=discord.ButtonStyle.green,
            row=4
        )
        button_confirm.callback = self.confirm_callback
        self.add_item(button_confirm)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Solo l'autore può usare questa interfaccia.", ephemeral=True)
            return False
        return True

    async def not_verified_callback(self, interaction: discord.Interaction):
        role_id = int(interaction.data["values"][0])
        self.not_verified_role = interaction.guild.get_role(role_id)
        await interaction.response.defer()

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
        if self.not_verified_role and self.timeout and self.temp_role and self.verified_role:
            self.selection_complete = True
            self.stop()
            await interaction.response.send_message("✅ Selezione confermata!", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ Completa tutte le selezioni prima di confermare.", ephemeral=True)

class CmdConfig(commands.GroupCog, name="config"):
    def __init__(self, bot: commands.bot, log: Logger, config: ConfigManager, twitch_app):
        super().__init__()
        self.bot = bot
        self.log = log
        self.config = config
        self.twitch_app = twitch_app
    
    # ============================= Standard =============================
    @app_commands.command(name="standard", description="Esegui la configurazione standard del bot")
    async def standard(self, interaction: discord.Interaction) -> None:
        # Get the guild from interaction
        guild: discord.Guild = interaction.guild

        # Get admin channels to configure
        admin_channels: dict = self.config.load_admin('channels')
        
        view: StandardView = StandardView(
            author=interaction.user,
            tags=admin_channels.keys()
        )
        await interaction.response.send_message(
            "Seleziona i canali",
            view=view,
            ephemeral=True
        )
        await view.wait()
        
        # Save selected channels
        for tag, channel_id in view.values.items():
            self.config.add_admin('channels', tag, channel_id)
            if tag == 'communication':
                self.config._load_communication_channel()
            
        # Respond with success
        await interaction.followup.send(
            '✅ Dati salvati con successo!',
            ephemeral=True
        )
        
        # INFO Log that operation is completed
        await self.log.command(f'Configurazione standard completata.', 'config', 'STANDARD')
    
    # ============================= Admin Management =============================
    @app_commands.command(name="admin-check", description="Visualizza tutti i dati inseriti come config di admin")
    async def admin_check(self, interaction: discord.Interaction) -> None:
        # Get the guild from interaction
        guild: discord.Guild = interaction.guild
        # Load communication channel
        communication_channel = guild.get_channel(self.config.communication_channel) if self.config.communication_channel else None
        
        try:
            # Get config/admin tags
            admin_data: dict = self.config.load_admin()
            tags: list = [tag for tag in admin_data.keys()]
            
            view: AdminCheckView = AdminCheckView(
                author=interaction.user,
                tags=tags
            )
            await interaction.response.send_message(
                "Seleziona il tag",
                view=view,
                ephemeral=True
            )
            await view.wait()
            # Save selected tag
            selected_tag: str = view.selected_tag
            # Get the section corresponding the selected tag
            selected_data: dict = self.config.load_admin(section=selected_tag)
            
            # Start the creation of the response embed
            description: str = ''
            if selected_tag == 'roles':
                for tag, role_id in selected_data.items():
                    role: discord.Role = guild.get_role(int(role_id))
                    description += f'\n**{tag}**:   {role.mention} ({role_id})'
            if selected_data == 'channels':
                for tag, channel_id in selected_data.items():
                    channel: discord.TextChannel = guild.get_channel(int(channel_id))
                    description += f'\n**{tag}**:   {channel.mention} ({channel_id})'
            
            embed_data: dict = {
                'title': f'Controllo Admin - {selected_tag.capitalize()}',
                'description': description,
                'color': self.bot.color
            }
            embed: discord.Embed = create_embed_from_dict(embed_data)
            # Respond with the embed
            await interaction.followup.send(embed=embed)
            
            # INFO Log that operation is completed
            await self.log.command(f'Risposto alla richiesta con i dati del seguente tag: "{selected_tag}"', 'config', 'ADMIN-CHECK')
            
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante la visualizzazione dei dati da config/admin.\n{e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - ADMIN-CHECK')
            await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - ADMIN-CHECK', message=error_message))
    
    @app_commands.command(name="admin-add", description="Aggiunge un ruolo o un canale ai config/admin.")
    async def admin_add(self, interaction: discord.Interaction) -> None:
        # Get the guild from interaction
        guild: discord.Guild = interaction.guild
        # Load communication channel
        communication_channel = guild.get_channel(self.config.communication_channel) if self.config.communication_channel else None
        
        try:
            # Get config/admin tags
            admin_data: dict = self.config.load_admin()
            tags: list = [tag for tag in admin_data.keys()]
            
            view: AdminAddView = AdminAddView(
                author=interaction.user,
                tags=tags
            )
            await interaction.response.send_message(
                "Seleziona il tag",
                view=view,
                ephemeral=True
            )
            await view.wait()
            
            config_tag: str = view.selected_tag
            tag: str = view.new_tag
            value: str = f'{view.values[0]}'
            
            # Respond with selected data
            await interaction.followup.send(
                "Dati inseriti:\n"
                f"#️⃣ Sezione: {config_tag} \n"
                f"🆚 Tag: {tag} \n"
                f"🆔 Id: {value} \n",
                ephemeral=True
            )
            
            # Save data in config
            self.config.add_admin(config_tag, tag, value)
            if config_tag == 'channels' and tag == 'communication':
                self.config._load_communication_channel()
            
            # Respond with success
            await interaction.followup.send(
                '✅ Dati salvati con successo!',
                ephemeral=True
            )
            
            # INFO Log that operation is completed
            await self.log.command(f'Nuovi dati aggiungi a config/admin.', 'config', 'ADMIN-ADD')
            
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante la visualizzazione dei dati da config/admin.\n{e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - ADMIN-ADD')
            await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - ADMIN-ADD', message=error_message))
    
    # ============================= Exception Management =============================
    @app_commands.command(name="exception-add", description="Aggiunge una lista di ruoli o canali alle eccezioni")
    async def exception_add(self, interaction: discord.Interaction) -> None:
        # Get the guild from interaction
        guild: discord.Guild = interaction.guild
        # Load communication channel
        communication_channel = guild.get_channel(self.config.communication_channel) if self.config.communication_channel else None
        
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
            self.config.add_exception(tag, values)
            
            # Respond with success
            await interaction.followup.send(
                '✅ Dati salvati con successo!',
                ephemeral=True
            )
            
            # INFO Log that operation is completed
            await self.log.command(f'Aggiunta una nuova eccezione: \n - tag: {tag} \n - values: {values}', 'config', 'EXCEPTION-ADD')

        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante l\'aggiunta di nuove eccezioni al file config.\n{e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - EXCEPTION-ADD')
            await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - EXCEPTION-ADD', message=error_message))
    
    # ============================= Message Logging Management =============================
    @app_commands.command(name="message-logging-setup", description="Configura la registrazione dei messaggi")
    async def message_logging_setup(self, interaction: discord.Interaction) -> None:
        # Get the guild from interaction
        guild: discord.Guild = interaction.guild
        # Load communication channel
        communication_channel = guild.get_channel(self.config.communication_channel) if self.config.communication_channel else None
        
        try:
            # Get config/message_logging tags
            message_logging_data: dict = self.config.load_message_logging()
            
            view: MessageLoggingView = MessageLoggingView(
                author=interaction.user
            )
            await interaction.response.send_message(
                f"Seleziona se abilitare o disabilitare la registrazione dei messaggi e i canali in cui verranno registrati i messaggi.\nAl momento la registrazione dei messaggi è {'**abilitata**' if message_logging_data['enabled'] else '**disabilitata**'}.",
                view=view,
                ephemeral=True
            )
            await view.wait()
            
            # Save selected data
            if view.selected_enabled:
                self.config.enable_message_logging()
            else:
                self.config.disable_message_logging()
            for channel_id in view.selected_channels:
                self.config.add_message_logging_channel(channel_id)
            
            # Respond with success
            await interaction.followup.send(
                '✅ Dati salvati con successo!',
                ephemeral=True
            )
            
            # INFO Log that operation is completed
            await self.log.command(f'Configurazione della registrazione dei messaggi completata.', 'config', 'MESSAGE-LOGGING-SETUP')
            
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante la configurazione della registrazione dei messaggi.\n{e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - MESSAGE-LOGGING-SETUP')
            await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - MESSAGE-LOGGING-SETUP', message=error_message))
    
    # ============================= Retention Days =============================
    @app_commands.command(name="retention", description="Aggiorna il periodo di conservazione dei log (1, 2, 3, 6 mesi)")
    async def retention(self, interaction: discord.Interaction) -> None:
        """Permette di aggiornare il periodo di conservazione dei log tramite una select."""
        # Get the guild from interaction
        guild: discord.Guild = interaction.guild
        # Load communication channel
        communication_channel = guild.get_channel(self.config.communication_channel) if self.config.communication_channel else None
        
        try:
            view = RetentionSelectView(author=interaction.user)
            await interaction.response.send_message(
                "Seleziona il periodo di conservazione dei log:",
                view=view,
                ephemeral=True
            )
            await view.wait()
            
            # Save selected data
            if view.selection_complete and view.selected_days:
                self.config.update_retention_days(view.selected_days)
                
                # Respond with success
                await interaction.followup.send(f"✅ Periodo di conservazione aggiornato a {view.selected_days} giorni.", ephemeral=True)
                
                # INFO Log that operation is completed
                await self.log.command(f'Periodo di conservazione aggiornato a {view.selected_days} giorni.', 'config', 'RETENTION')
                
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante l\'aggiornamento del periodo di conservazione dei log.\n{e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - RETENTION')
            await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - RETENTION', message=error_message))
    
    @app_commands.command(name="set-not-verified-role", description="Salva l'ID del ruolo 'not_verified' del server")
    async def set_not_verified_role(self, interaction: discord.Interaction) -> None:
        """
        Permette all'admin di selezionare e salvare il ruolo 'not_verified'.
        """
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
                await interaction.followup.send(f"✅ Ruolo 'not_verified' salvato: <@&{view.selected_role_id}> (ID: {view.selected_role_id})", ephemeral=True)
                # INFO Log that operation is completed
                await self.log.command(f"Ruolo 'not_verified' impostato: {view.selected_role_id}", 'config', 'SET-NOT-VERIFIED-ROLE')
            else:
                await interaction.followup.send("Nessun ruolo selezionato.", ephemeral=True)
        except Exception as e:
            error_message = f"Errore durante la selezione del ruolo 'not_verified'.\n{e}"
            await self.log.error(error_message, 'COMMAND - CONFIG - SET-NOT-VERIFIED-ROLE')
            if communication_channel:
                await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - SET-NOT-VERIFIED-ROLE', message=error_message))
    
    @app_commands.command(name="setup-iniziale", description="Esegui la configurazione iniziale completa del bot")
    async def setup_iniziale(self, interaction: discord.Interaction) -> None:
        """
        Runs the initial setup wizard for the bot, guiding the user through all main configuration steps.
        """
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel) if self.config.communication_channel else None
        try:
            # Step 1: Standard configuration (channels)
            admin_channels: dict = self.config.load_admin('channels')
            view_standard = StandardView(
                author=interaction.user,
                tags=admin_channels.keys()
            )
            await interaction.response.send_message(
                "Step 1/5: Seleziona i canali principali.",
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

            # Step 2: Selezione ruolo 'not_verified' + verifica
            view_nv_verif = NotVerifiedAndVerificationSetupView(author=interaction.user)
            await interaction.followup.send(
                "Step 2/5: Seleziona il ruolo 'not_verified' e configura la verifica (timeout, ruoli)",
                view=view_nv_verif,
                ephemeral=True
            )
            await view_nv_verif.wait()
            not_verified_role_mention = "Non selezionato"
            verification_data = {"timeout": "Non selezionato", "temp_role": "Non selezionato", "verified_role": "Non selezionato"}
            if view_nv_verif.selection_complete:
                # Salva not_verified
                self.config.add_admin('roles', 'not_verified', view_nv_verif.not_verified_role.id)
                not_verified_role_mention = view_nv_verif.not_verified_role.mention
                # Salva verifica
                self.config.add_admin('roles', 'in_verification', view_nv_verif.temp_role.id)
                self.config.add_admin('roles', 'verified', view_nv_verif.verified_role.id)
                self.verification.update_timeout(view_nv_verif.timeout)
                verification_data['timeout'] = f"{view_nv_verif.timeout} secondi"
                verification_data['temp_role'] = view_nv_verif.temp_role.mention
                verification_data['verified_role'] = view_nv_verif.verified_role.mention

            # Step 3: Retention days
            view_retention = RetentionSelectView(author=interaction.user)
            await interaction.followup.send(
                "Step 3/5: Seleziona il periodo di conservazione dei log:",
                view=view_retention,
                ephemeral=True
            )
            await view_retention.wait()
            retention_days = None
            if view_retention.selection_complete and view_retention.selected_days:
                self.config.update_retention_days(view_retention.selected_days)
                retention_days = view_retention.selected_days
            else:
                retention_days = "Non selezionato"

            # Step 4: Message logging
            view_logging = MessageLoggingView(author=interaction.user)
            await interaction.followup.send(
                "Step 4/5: Configura la registrazione dei messaggi.",
                view=view_logging,
                ephemeral=True
            )
            await view_logging.wait()
            logging_enabled = None
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
                    channel = guild.get_channel(channel_id)
                    logging_channels.append(channel.mention if channel else f"ID: {channel_id}")
            else:
                logging_enabled = "Non selezionato"

            # Step 5: Twitch titles (View + Modal)
            view_titles = TwitchTitlesView(author=interaction.user)
            await interaction.followup.send(
                "Step 5/5: Imposta i titoli Twitch (on/off).",
                view=view_titles,
                ephemeral=True
            )
            await view_titles.wait()
            twitch_titles = {}
            if view_titles.titles:
                self.twitch_app.change_title({'tag': 'on', 'title': view_titles.titles['on']})
                self.twitch_app.change_title({'tag': 'off', 'title': view_titles.titles['off']})
                twitch_titles['on'] = view_titles.titles['on']
                twitch_titles['off'] = view_titles.titles['off']
            else:
                twitch_titles['on'] = twitch_titles['off'] = "Non selezionato"

            # Step 6: Twitch streamer name (View + Modal)
            view_streamer = StreamerNameView(author=interaction.user)
            await interaction.followup.send(
                "Ultimo step: Inserisci il nome dello streamer Twitch.",
                view=view_streamer,
                ephemeral=True
            )
            await view_streamer.wait()
            streamer_name = view_streamer.streamer_name if view_streamer.streamer_name else "Non selezionato"
            if view_streamer.streamer_name:
                self.twitch_app.change_streamer_name(view_streamer.streamer_name)

            # Recap finale
            recap = """🎉 **Configurazione iniziale completata!**

**Canali configurati:**
"""
            for tag, channel_id in selected_channels.items():
                channel = guild.get_channel(channel_id)
                recap += f"- {tag}: {channel.mention if channel else f'ID: {channel_id}'}\n"
            recap += f"\n**Ruolo not_verified:** {not_verified_role_mention}\n"
            recap += f"\n**Sistema di verifica:**\n- Timeout: {verification_data['timeout']}\n- Ruolo temporaneo: {verification_data['temp_role']}\n- Ruolo verificato: {verification_data['verified_role']}\n"
            recap += f"\n**Retention giorni:** {retention_days}\n"
            recap += f"\n**Message logging:** {logging_enabled}\n"
            if logging_channels:
                recap += f"- Canali logging: {', '.join(logging_channels)}\n"
            recap += f"\n**Twitch titles:**\n- ON: {twitch_titles['on']}\n- OFF: {twitch_titles['off']}\n"
            recap += f"\n**Streamer Twitch:** {streamer_name}\n"

            await interaction.followup.send(recap, ephemeral=True)
            await self.log.command('Configurazione iniziale completata.', 'config', 'SETUP-INIZIALE')
        except Exception as e:
            # EXCEPTION
            error_message = f'Errore durante la configurazione iniziale.\n{e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - SETUP-INIZIALE')
            if communication_channel:
                await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - SETUP-INIZIALE', message=error_message))
    
    # ============================= Booster Role =============================
    @app_commands.command(name="set-booster-role", description="Salva l'ID del ruolo booster del server")
    async def set_booster_role(self, interaction: discord.Interaction) -> None:
        """
        Allows the admin to select and save the server booster role ID.
        """
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
                await interaction.followup.send(f"✅ Ruolo booster salvato: <@&{view.selected_role_id}> (ID: {view.selected_role_id})", ephemeral=True)
                # INFO Log that operation is completed
                await self.log.command(f"Ruolo booster impostato: {view.selected_role_id}", 'config', 'SET-BOOSTER-ROLE')
            else:
                await interaction.followup.send("Nessun ruolo selezionato.", ephemeral=True)
        except Exception as e:
            # EXCEPTION
            error_message = f'Errore durante la selezione del ruolo booster.\n{e}'
            await self.log.error(error_message, 'COMMAND - CONFIG - SET-BOOSTER-ROLE')
            if communication_channel:
                await communication_channel.send(self.log.error_message(command='COMMAND - CONFIG - SET-BOOSTER-ROLE', message=error_message))