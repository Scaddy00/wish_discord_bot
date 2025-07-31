
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
        
        # Dictionary containing all commands and their descriptions
        self.commands_info = {
            "user": "Invia un embed con le info di un utente"
        }
    
    # ============================= Help Command =============================
    @app_commands.command(name="help", description="Mostra l'elenco dei comandi info disponibili")
    async def help(self, interaction: discord.Interaction) -> None:
        """Mostra un embed con tutti i comandi info e le loro descrizioni"""
        guild: discord.Guild = interaction.guild
        communication_channel = guild.get_channel(self.config.communication_channel) if self.config.communication_channel else None
        
        try:
            # Create embed with commands info
            embed = create_embed(
                title="ℹ️ Comandi Info",
                description="Elenco di tutti i comandi per le informazioni",
                color=self.bot.color,
                fields=[]
            )
            
            # Add each command to the embed
            for command_name, description in self.commands_info.items():
                embed.add_field(
                    name=f"`/info {command_name}`",
                    value=description,
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await self.log.command('Visualizzato help comandi info', 'info', 'HELP')
            
        except discord.NotFound as e:
            error_message = f'Risorsa non trovata: {e}'
            await self.log.error(error_message, 'COMMAND - INFO - HELP')
            await interaction.response.send_message(f"❌ {error_message}", ephemeral=True)
            
        except discord.Forbidden as e:
            error_message = f'Permessi insufficienti: {e}'
            await self.log.error(error_message, 'COMMAND - INFO - HELP')
            await interaction.response.send_message(f"❌ {error_message}", ephemeral=True)
            
        except Exception as e:
            error_message: str = f'Errore durante la visualizzazione dell\'help: {e}'
            await self.log.error(error_message, 'COMMAND - INFO - HELP')
            await interaction.response.send_message(f"❌ {error_message}", ephemeral=True)
            
            # Try to send error to communication channel if available
            if communication_channel:
                try:
                    await communication_channel.send(self.log.error_message(command='COMMAND - INFO - HELP', message=error_message))
                except Exception as comm_error:
                    await self.log.error(f'Impossibile inviare errore al canale di comunicazione: {comm_error}', 'COMMAND - INFO - HELP')

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
            banner_info = "✅ Banner personalizzato" if user.banner else "❌ Nessun banner"
            
            # Colore accent (se disponibile)
            accent_color = f"#{user.accent_color.value:06x}" if user.accent_color else "Non impostato"
            
            embed = create_embed(
                title = f"Info utente {user.name}",
                description = f"Informazioni dettagliate sull'utente {user.mention}",
                color = f"#{user.accent_color.value:06x}" if user.accent_color else self.bot.color,
                fields = [
                    {
                        'name': '📋 Dati principali',
                        'value': f'**Nome:** {user.name}\n**ID:** {user.id}\n**Tipo:** {user_type}\n**Menzione:** {user.mention}',
                        'inline': False
                    },
                    {
                        'name': '📅 Informazioni account',
                        'value': f'**Creato il:** {created_date}\n**Avatar:** {avatar_info}\n**Banner:** {banner_info}\n**Colore accent:** {accent_color}',
                        'inline': False
                    },
                    {
                        'name': '🏳️ Flags',
                        'value': self._get_user_flags_info(user),
                        'inline': False
                    }
                ],
                thumbnail = user.avatar.url if user.avatar else user.default_avatar.url,
                image = user.banner.url if user.banner else None
            )
            
            await interaction.response.send_message(embed=embed)
        except discord.NotFound as e:
            await interaction.response.send_message(f"❌ Utente non trovato: {e}", ephemeral=True)
            await self.log.error(f"Utente non trovato: {e}", "COMMAND - INFO - USER")
        except discord.HTTPException as e:
            await interaction.response.send_message(f"❌ Errore durante la richiesta: {e}", ephemeral=True)
            await self.log.error(f"Errore durante la richiesta: {e}", "COMMAND - INFO - USER")
    
    def _get_user_flags_info(self, user: discord.User) -> str:
        """Restituisce le flag dell'utente con emoji e nomi in italiano"""
        flags_mapping = {
            'staff': ('👨‍💼', 'Staff Discord'),
            'partner': ('🤝', 'Partner Discord'),
            'bug_hunter': ('🐛', 'Bug Hunter'),
            'bug_hunter_gold': ('🏆', 'Bug Hunter Gold'),
            'early_supporter': ('🎗️', 'Early Supporter'),
            'team_user': ('👥', 'Team User'),
            'system': ('⚙️', 'Sistema'),
            'hypesquad': ('🏠', 'HypeSquad'),
            'hypesquad_bravery': ('💙', 'HypeSquad Bravery'),
            'hypesquad_brilliance': ('💛', 'HypeSquad Brilliance'),
            'hypesquad_balance': ('💜', 'HypeSquad Balance'),
            'verified_bot': ('✅', 'Bot Verificato'),
            'verified_bot_developer': ('🤖', 'Sviluppatore Bot'),
            'discord_certified_moderator': ('🛡️', 'Moderatore Certificato'),
            'bot_http_interactions': ('🔗', 'Bot HTTP'),
            'active_developer': ('💻', 'Active Developer')
        }
        
        flags_info = []
        for flag in user.public_flags.all():
            if flag.name in flags_mapping:
                emoji, name = flags_mapping[flag.name]
                flags_info.append(f"{emoji} {name}")
        
        return "\n".join(flags_info) if flags_info else "❌ Nessun flag speciale"
