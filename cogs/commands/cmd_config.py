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
from utils.printing import create_embed_from_dict

class CmdConfig(commands.GroupCog, name="config"):
    def __init__(self, bot: commands.bot, log: Logger, config: ConfigManager):
        super().__init__()
        self.bot = bot
        self.log = log
        self.config = config
    
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