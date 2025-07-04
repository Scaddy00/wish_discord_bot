
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from os import getenv
# ----------------------------- Custom Libraries -----------------------------
from utility import printing
from logger.logger import Logger

class MemberEvents(commands.Cog):
    def __init__(self, bot: commands.Bot, log: Logger):
        self.bot = bot
        self.log = log
    
    # ============================= ON_MEMBER_JOIN (Welcome) =============================
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        # Load bot communication channel
        communication_channel = self.bot.get_channel(int(getenv('BOT_COMMUNICATION_CHANNEL_ID')))
        # Get guild
        guild: discord.Guild = member.guild
        
        try:
            welcome_channel: discord.TextChannel = guild.system_channel
            rule_channel: discord.TextChannel = guild.get_channel(int(getenv('RULE_CHANNEL_ID')))
            # Load embed message content
            message_content: dict = await printing.load_single_embed_text(guild, 'welcome')
            
            message: discord.Embed = printing.create_embed(title=message_content['title'], # Load title
                                                        description=message_content['description'].format(user=member.mention, rule=rule_channel.mention), # Load description adding the mentions required
                                                        color=message_content['color'], # Load the color from str
                                                        image=message_content['image_url'], # Load image url
                                                        thumbnail=message_content['thumbnail_url']) # Load thumbnail url
            
            await welcome_channel.send(embed=message)
            # INFO LOG
            await self.bot.log.event(f'Nuovo utente aggiunto, {member.name} ({member.id})', 'welcome')
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante l\'invio del messaggio di benvenuto. \nUtente: {member.name} ({member.id}) \n{e}'
            await self.bot.log.error(error_message, 'EVENT - MEMBER WELCOME')
            await communication_channel.send(self.bot.log.error_message(command = 'EVENT - WELCOME', message = error_message))
    
    # ============================= ON_MEMBER_REMOVE (ByeBye) =============================
    @commands.Cog.listener()
    async def on_raw_member_remove(self, payload: discord.RawMemberRemoveEvent) -> None:
        # Load bot communication channel
        communication_channel = self.bot.get_channel(int(getenv('BOT_COMMUNICATION_CHANNEL_ID')))
        # Get the user
        user: discord.User = payload.user
        
        try:
            await communication_channel.send(f'COMUNICAZIONE -> L\'utente {user.mention} ha lasciato il server')
            # INFO LOG
            await self.bot.log.event(f'Utente uscito dal server, {user.name} ({user.id})', 'remove')
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante l\'invio del messaggio di ByeBye. \nUtente: {user.name} ({user.id})\n{e}'
            await self.bot.log.error(error_message, 'EVENT - MEMBER REMOVE')
            await communication_channel.send(self.bot.log.error_message(command = 'EVENT - MEMBER REMOVE', message = error_message))
