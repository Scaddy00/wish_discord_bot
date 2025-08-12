
# ----------------------------- Imported Libraries -----------------------------
# Third-party library imports
import discord
from discord.ext import commands
from discord import app_commands

# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from config_manager import ConfigManager
from utils.printing import safe_send_message, create_embed

class CmdUtility(commands.GroupCog, name="utility"):
    """
    Utility commands for emoji tools and other helpers.
    """
    description: str = "Strumenti di utilità (emoji e altro)."

    def __init__(self, bot: commands.Bot, log: Logger, config: ConfigManager) -> None:
        super().__init__()
        self.bot: commands.Bot = bot
        self.log: Logger = log
        self.config: ConfigManager = config
        
        # Dictionary containing all commands and their descriptions
        self.commands_info = {
            "emoji-to-unicode": "Ottiene il valore unicode di un emoji"
        }
    
    # ============================= Help Command =============================
    @app_commands.command(name="help", description="Mostra l'elenco dei comandi utility disponibili")
    async def help(self, interaction: discord.Interaction) -> None:
        """
        Show an embed with all utility commands and their descriptions.
        """
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel) if self.config.communication_channel else None
        
        try:
            # Create embed with commands info
            embed = create_embed(
                title="🔧 Comandi Utility",
                description="Elenco di tutti i comandi utility disponibili",
                color=self.bot.color,
                fields=[]
            )
            
            # Add each command to the embed
            for command_name, description in self.commands_info.items():
                embed.add_field(
                    name=f"`/utility {command_name}`",
                    value=description,
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await self.log.command('Visualizzato help comandi utility', 'utility', 'HELP')
            
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - UTILITY - HELP')
            await interaction.response.send_message(f"❌ {error_message}", ephemeral=True)
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - UTILITY - HELP')
            await interaction.response.send_message(f"❌ {error_message}", ephemeral=True)
            
        except Exception as e:
            error_message: str = f'Errore durante la visualizzazione dell\'help: {e}'
            await self.log.error(error_message, 'COMMAND - UTILITY - HELP')
            await interaction.response.send_message(f"❌ {error_message}", ephemeral=True)
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - UTILITY - HELP', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - UTILITY - HELP')
    
    # ============================= Emoji Tools =============================
    @app_commands.command(name="emoji-to-unicode", description="Ottiene il valore unicode di un emoji")
    async def emoji_unicode(self, interaction: discord.Interaction, emoji_input: str) -> None:
        """
        Convert an emoji to its unicode codepoints or show info for custom emojis.
        """
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel)
        
        try:
            emoji = discord.PartialEmoji.from_str(emoji_input)
            if emoji.id:  # Emoji custom
                await safe_send_message(
                    interaction,
                    f'🧩 **Emoji personalizzata**\n'
                    f'Nome: `{emoji.name}`\n'
                    f'ID: `{emoji.id}`\n'
                    f'Animata: `{emoji.animated}`\n'
                    f'Rappresentazione: `<{"a" if emoji.animated else ""}:{emoji.name}:{emoji.id}>`'
                )
            else:  # Emoji Unicode standard
                unicode_repr = ' '.join(f'U+{ord(char):04X}' for char in emoji_input)
                await safe_send_message(
                    interaction,
                    f'🔤 **Emoji Unicode**\n'
                    f'Emoji: `{emoji_input}`\n'
                    f'Codepoint: `{unicode_repr}`'
                )
                
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - UTILITY - EMOJI-TO-UNICODE')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - UTILITY - EMOJI-TO-UNICODE')
            await safe_send_message(interaction, f"❌ {error_message}")
            
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Non sono riuscito a interpretare l\'emoji: {e}'
            await self.log.error(error_message, 'COMMAND - UTILITY - EMOJI-TO-UNICODE')
            await safe_send_message(interaction, f"❌ {error_message}")
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - UTILITY - EMOJI-TO-UNICODE', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - UTILITY - EMOJI-TO-UNICODE')