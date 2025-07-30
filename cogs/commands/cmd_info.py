
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from config_manager import ConfigManager
from utils.printing import create_embed

class CmdInfo(commands.GroupCog, name="info"):
    def __init__(self, bot: commands.Bot, log: Logger, config: ConfigManager):
        self.bot = bot
        self.log = log
        self.config = config

    @app_commands.command(name="user", description="Invia un embed con le info di un utente")
    async def user(self, interaction: discord.Interaction, user_id: str) -> None:
        try:
            user: discord.User = await self.bot.fetch_user(int(user_id))
            
            if user is None:
                await interaction.response.send_message("❌ Utente non trovato")
                return
            
            # Formatta la data di creazione
            created_date = user.created_at.strftime("%d/%m/%Y %H:%M:%S")
            
            # Determina il tipo di utente
            user_type = "🤖 Bot" if user.bot else "👤 Utente"
            
            # Informazioni sull'avatar
            avatar_info = "✅ Avatar personalizzato" if user.avatar else "❌ Avatar di default"
            
            # Colore accent (se disponibile)
            accent_color = f"#{user.accent_color.value:06x}" if user.accent_color else "Non impostato"
            
            embed = create_embed(
                title = f"Info utente {user.name}",
                description = f"Informazioni dettagliate sull'utente {user.mention}",
                color = self.bot.color,
                fields = [
                    {
                        'name': '📋 Dati principali',
                        'value': f'**Nome:** {user.name}\n**ID:** {user.id}\n**Tipo:** {user_type}\n**Menzione:** {user.mention}',
                        'inline': True
                    },
                    {
                        'name': '📅 Informazioni account',
                        'value': f'**Creato il:** {created_date}\n**Avatar:** {avatar_info}\n**Colore accent:** {accent_color}',
                        'inline': True
                    }
                ],
                thumbnail = user.avatar.url if user.avatar else user.default_avatar.url
            )
            
            await interaction.response.send_message(embed=embed)
        except discord.NotFound as e:
            await interaction.response.send_message(f"❌ Utente non trovato: {e}", ephemeral=True)
            await self.log.error(f"Utente non trovato: {e}", "COMMAND - INFO - USER")
        except discord.HTTPException as e:
            await interaction.response.send_message(f"❌ Errore durante la richiesta: {e}", ephemeral=True)
            await self.log.error(f"Errore durante la richiesta: {e}", "COMMAND - INFO - USER")