
# ----------------------------- Imported Libraries -----------------------------
# Third-party library imports
import discord
from discord.ext import commands

# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from config_manager import ConfigManager

class GuildEvents(commands.Cog):
    """
    Cog that handles guild-level events such as joins.
    
    Sends a getting-started message and logs the event when the bot joins a guild.
    """

    def __init__(self, bot: commands.Bot, log: Logger, config: ConfigManager) -> None:
        self.bot: commands.Bot = bot
        self.log: Logger = log
        self.config: ConfigManager = config
    
    # ============================= ON_GUILD_JOIN =============================
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        """
        Send a welcome message on guild join and log the event.
        """
        channel: discord.TextChannel | None = None
        # Find a channel where the bot can send messages
        for candidate in guild.text_channels:
            if candidate.permissions_for(guild.me).send_messages:
                channel = candidate
                break

        if channel is not None:
            await channel.send(
                f'Ciao! Sono {self.bot.user.name} e sono qui per aiutarti!\n'
                f'Per iniziare, puoi inviare il comando `/config standard` per eseguire la configurazione del bot.'
            )

        # INFO LOG
        await self.log.event(f'Bot aggiunto in {guild.name} ({guild.id})', 'guild_join')