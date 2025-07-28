
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from discord import app_commands
from os import getenv
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from config_manager import ConfigManager
from utils.printing import safe_send_message

class CmdUtility(commands.GroupCog, name="utility"):
    def __init__(self, bot: commands.bot, log: Logger, config: ConfigManager):
        super().__init__()
        self.bot = bot
        self.log = log
        self.config = config
    
    # ============================= Emoji Tools =============================
    @app_commands.command(name="emoji-to-unicode", description="Ottiene il valore unicode di un emoji")
    async def emoji_unicode(self, interaction: discord.Interaction, emoji_input: str) -> None:
        """Converte un emoji nel suo valore unicode o mostra informazioni per emoji personalizzate"""
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