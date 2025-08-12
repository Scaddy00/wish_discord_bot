
# ----------------------------- Imported Libraries -----------------------------
# Standard library imports
from os import getenv

# Third-party library imports
import discord
from discord.ext import commands
from discord import app_commands

# ----------------------------- Custom Libraries -----------------------------
from cogs.commands import add_commands
from cogs.events import add_events
from cogs.tasks import setup_all_tasks

# ============================= BOT SETUP HOOK =============================
class WishBot(commands.Bot):
    """
    Main Discord bot class for the Wish Discord Bot.
    
    Handles all bot functionality including commands, events, tasks,
    verification system, and Twitch integration.
    """
    
    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize the WishBot with all necessary components.
        
        Sets up logger, config manager, verification system, and Twitch app.
        """
        super().__init__(*args, **kwargs)
        from logger import Logger
        from config_manager import ConfigManager
        from cogs.verification import VerificationManager
        from cogs.twitch import TwitchApp

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Instance Variables ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.color: str = '0xA6BBF0'

        self.log: Logger = Logger()
        self.config: ConfigManager = ConfigManager()
        self.verification: VerificationManager = VerificationManager(self, self.log, self.config)
        self.twitch_app: TwitchApp = TwitchApp(self, self.log, self.config)

    async def setup_hook(self) -> None:
        """
        Setup hook called when the bot is starting up.
        
        Loads all commands, events, and tasks. Handles command synchronization
        for both debug and production modes.
        """
        # COMMANDS
        await add_commands(self, self.log, self.config, self.verification, self.twitch_app)
        # EVENTS
        await add_events(self, self.log, self.config, self.verification, self.twitch_app)
        # TASKS
        await setup_all_tasks(self, self.log, self.config, self.twitch_app)
        
        # Register a centralized error handler for app (slash) commands
        @self.tree.error
        async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:  # type: ignore[unused-ignore]
            async def _reply_ephemeral(message: str) -> None:
                try:
                    if not interaction.response.is_done():
                        await interaction.response.send_message(message, ephemeral=True)
                    else:
                        await interaction.followup.send(message, ephemeral=True)
                except Exception:
                    # Avoid raising further errors in the handler
                    pass

            # Map known errors to friendly Italian messages
            if isinstance(error, app_commands.CommandOnCooldown):
                await _reply_ephemeral(f"⏳ Comando in cooldown. Riprova tra {error.retry_after:.1f} secondi.")
                await self.log.error(f"Cooldown: {interaction.command} - {error}", "APP-COMMAND-ERROR")
                return

            if isinstance(error, app_commands.MissingPermissions):
                missing = ', '.join(error.missing_permissions)
                await _reply_ephemeral(f"❌ Permessi mancanti: {missing}.")
                await self.log.error(f"MissingPermissions: {interaction.command} - {missing}", "APP-COMMAND-ERROR")
                return

            if isinstance(error, app_commands.BotMissingPermissions):
                missing = ', '.join(error.missing_permissions)
                await _reply_ephemeral(f"❌ Il bot non ha i permessi necessari: {missing}.")
                await self.log.error(f"BotMissingPermissions: {interaction.command} - {missing}", "APP-COMMAND-ERROR")
                return

            if isinstance(error, app_commands.CheckFailure):
                await _reply_ephemeral("❌ Non hai i permessi per eseguire questo comando.")
                await self.log.error(f"CheckFailure: {interaction.command}", "APP-COMMAND-ERROR")
                return

            # Unhandled errors → generic message and log details
            await _reply_ephemeral("⚠️ Si è verificato un errore imprevisto. Riprova più tardi.")
            await self.log.error(f"Unhandled error in command {interaction.command}: {error}", "APP-COMMAND-ERROR")
        
        if getenv("DEBUG_MODE") == "1":
            dev_guild = discord.Object(id=int(getenv('GUILD_ID')))
            self.tree.clear_commands(guild=dev_guild)
            self.tree.copy_global_to(guild=dev_guild)
            synced = await self.tree.sync(guild=dev_guild)
            await self.log.event(f"Comandi sincronizzati con la dev guild: {len(synced)}", "setup")
            
            tree = self.tree._get_all_commands()
            commands_names: list[str] = [command.name for command in tree]
            await self.log.event(f"Nomi dei comandi: {commands_names}", "setup")
        else:
            synced = await self.tree.sync()
            await self.log.event(f"Comandi globali sincronizzati: {len(synced)}", "setup")