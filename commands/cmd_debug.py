import discord
from discord.ext import commands
from discord import app_commands

class CmdDebug(commands.Cog, name="debug"):
    def __init__(self, bot: discord.Client):
        self.bot = bot

    @app_commands.command(name="commands", description="Mostra i comandi slash registrati")
    async def debug_commands(self, interaction: discord.Interaction):
        commands = [
            f"/{cmd.qualified_name}" for cmd in self.bot.tree.walk_commands()
        ]
        await interaction.response.send_message(
            "Comandi registrati:\n" + "\n".join(commands),
            ephemeral=True  # Solo chi esegue il comando può vederlo
        )