
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
import asyncio
from datetime import datetime
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from utils.roles import add_role, remove_role
from config_manager import ConfigManager
from cogs.tasks.welcome import create_welcome_message

class MemberEvents(commands.Cog):
    def __init__(self, bot: commands.Bot, log: Logger, config: ConfigManager):
        self.bot = bot
        self.log = log
        self.config = config
    
    # ============================= ON_MEMBER_JOIN (Welcome) =============================
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        await asyncio.sleep(1)  # Wait 1 second to allow Discord to propagate the user info
        # Get guild
        guild: discord.Guild = member.guild
        # Load bot communication channel
        communication_channel = guild.get_channel(self.config.communication_channel)

        # Assign 'not_verified' role if configured
        not_verified_role_id = self.config.load_admin('roles', 'not_verified')
        if not_verified_role_id and not_verified_role_id != '':
            try:
                await add_role(self.log, guild, int(not_verified_role_id), member.id, self.config)
            except Exception as e:
                error_message: str = f"Errore durante l'assegnazione del ruolo 'not_verified'.\nUtente: {member.name} ({member.id})\n{e}"
                await self.log.error(error_message, 'EVENT - MEMBER NOT VERIFIED ROLE')
                if communication_channel:
                    await communication_channel.send(self.log.error_message(command = 'EVENT - MEMBER NOT VERIFIED ROLE', message = error_message))

        try:
            # Get welcome channel
            welcome_channel: discord.TextChannel = guild.system_channel
            
            # Create welcome message
            message = await create_welcome_message(member, self.config, guild)
            # Send welcome message to user
            await welcome_channel.send(embeds=message)
            # Insert welcome message into database
            self.log.db.insert_welcome(datetime.now().isoformat(), str(member.id), member.name)
            # INFO LOG
            await self.log.event(f'Nuovo utente aggiunto, {member.name} ({member.id})', 'guild_join')
        except Exception as e:
            # EXCEPTION
            error_message: str = f"Errore durante l'invio del messaggio di benvenuto. \nUtente: {member.name} ({member.id}) \n{e}"
            await self.log.error(error_message, 'EVENT - MEMBER WELCOME')
            if communication_channel:
                await communication_channel.send(self.log.error_message(command = 'EVENT - MEMBER WELCOME', message = error_message))
    
    # ============================= ON_MEMBER_REMOVE (ByeBye) =============================
    @commands.Cog.listener()
    async def on_raw_member_remove(self, payload: discord.RawMemberRemoveEvent) -> None:
        # Get guild
        guild: discord.Guild = self.bot.get_guild(payload.guild_id)
        # Load bot communication channel
        communication_channel = guild.get_channel(self.config.communication_channel)
        # Get the user
        user: discord.User = payload.user
        
        try:
            await communication_channel.send(f'COMUNICAZIONE -> L\'utente {user.mention} ha lasciato il server')
            # INFO LOG
            await self.log.event(f'Utente uscito dal server, {user.name} ({user.id})', 'remove')
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante l\'invio del messaggio di ByeBye. \nUtente: {user.name} ({user.id})\n{e}'
            await self.log.error(error_message, 'EVENT - MEMBER REMOVE')
            if communication_channel:
                await communication_channel.send(self.log.error_message(command = 'EVENT - MEMBER REMOVE', message = error_message))
    
    # ============================= ON_MEMBER_UPDATE (Server Booster) =============================
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        # Get guild
        guild: discord.Guild = after.guild
        # Load bot communication channel
        communication_channel = guild.get_channel(self.config.communication_channel)
        
        if before.premium_since is None and after.premium_since is not None: # Check if Member boosted the server
            # Add the role
            booster_role_id = self.config.load_admin('roles', 'server_booster')
            if booster_role_id and booster_role_id != '':
                await add_role(self.log, guild, int(booster_role_id), after.id, self.config)
            # INFO LOG - User became booster
            await self.log.event(f'Utente diventato server booster, {after.name} ({after.id})', 'boost')
        elif before.premium_since is not None and after.premium_since is not None: # Check if Member not boosted the server
            # Remove the role
            booster_role_id = self.config.load_admin('roles', 'server_booster')
            if booster_role_id and booster_role_id != '':
                await remove_role(self.log, guild, int(booster_role_id), after.id, self.config)
