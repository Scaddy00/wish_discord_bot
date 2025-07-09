
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from discord import app_commands
from os import getenv
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger

class CmdUtility(commands.GroupCog, name="utility"):
    def __init__(self, bot: discord.Client, log: Logger):
        super().__init__()
        self.bot = bot
        self.log = log
    
    @app_commands.command(name="emoji-to-unicode", description="Ottiene il valore unicode di un emoji")
    async def emoji_unicode(self, interaction: discord.Interaction, emoji_input: str) -> None:
        # Load communication channel
        communication_channel = interaction.guild.get_channel(int(getenv('BOT_COMMUNICATION_CHANNEL_ID')))
        
        try:
            emoji = discord.PartialEmoji.from_str(emoji_input)
            if emoji.id:  # Emoji custom
                await interaction.response.send_message(
                    f'🧩 **Emoji personalizzata**\n'
                    f'Nome: `{emoji.name}`\n'
                    f'ID: `{emoji.id}`\n'
                    f'Animata: `{emoji.animated}`\n'
                    f'Rappresentazione: `<{'a' if emoji.animated else ''}:{emoji.name}:{emoji.id}>`'
                )
            else:  # Emoji Unicode standard
                unicode_repr = ' '.join(f'U+{ord(char):04X}' for char in emoji_input)
                await interaction.response.send_message(
                    f'🔤 **Emoji Unicode**\n'
                    f'Emoji: `{emoji_input}`\n'
                    f'Codepoint: `{unicode_repr}`'
                )
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Non sono riuscito a interpretare l\'emoji.\nErrore: `{e}`'
            await self.log.error(error_message, 'COMMAND - UTILITY - EMOJI-TO-UNICODE')
            await communication_channel.send(self.log.error_message(command='COMMAND - UTILITY - EMOJI-TO-UNICODE', message=error_message))