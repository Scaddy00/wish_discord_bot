
# ----------------------------- Standard libraries -----------------------------
import asyncio
from datetime import datetime, timezone
from os import path, getenv
import discord
# ----------------------------- Custom libraries -----------------------------
from utils.file_io import read_file, write_file
from logger import Logger
from config_manager import ConfigManager

class VerificationManager:
    """
    Manages the Discord user verification system.
    
    Handles user verification process including temporary roles, timeouts,
    and verification status tracking.
    """
    
    def __init__(self, bot, log: Logger, config: ConfigManager):
        """
        Initialize the VerificationManager.
        
        Args:
            bot: Discord bot instance
            log (Logger): Logger instance for logging verification events
            config (ConfigManager): Configuration manager instance
        """
        self.bot = bot
        self.log = log
        self.config = config
        self.timeout = 0
        self.temp_role_id = 0
        self.verified_role_id = 0
        self.waiting_users = {}
        self.file_path = path.join(getenv('DATA_PATH'), getenv('VERIFICATION_DATA_FILE_NAME'))
        self.setup()
    
    # ============================= Load Data =============================
    def load_data(self) -> dict:
        if path.exists(self.file_path):
            return read_file(self.file_path)
        else:
            return {}
    
    # ============================= Save Data =============================
    def save_data(self) -> None:
        data: dict = self.load_data()
        data['pending'] = self.waiting_users
        write_file(self.file_path, data)
    
    # ============================= Reload Data =============================
    def reload_data(self, data) -> None:
        self.timeout = data['config'].get('timeout', 0)
        temp_role_id = self.config.load_admin('roles', 'in_verification')
        verified_role_id = self.config.load_admin('roles', 'verified')
        
        # Convert to int if not None, otherwise set to 0
        self.temp_role_id = int(temp_role_id) if temp_role_id and temp_role_id != '' else 0
        self.verified_role_id = int(verified_role_id) if verified_role_id and verified_role_id != '' else 0
        
        self.waiting_users = data.get('pending', {})
    
    # ============================= Setup =============================
    def setup(self) -> None:
        default: dict = {}
        if not path.exists(self.file_path):
            default = {
                'config': {
                    'timeout': '',
                    'temp_role_id': '',
                    'verified_role_id': ''
                },
                'pending': {}
            }
            write_file(self.file_path, default)
        else:
            # Load default data
            default = self.load_data()
            self.reload_data(default)
    
    # ============================= Update Config =============================
    def update_timeout(self, new_timeout: str) -> None:
        config: dict = self.load_data()
        
        config['config']['timeout'] = new_timeout
        write_file(self.file_path, config)
        self.reload_data(config)
    
    # ============================= Start Timer =============================
    async def start_timer(self, guild_id: int, user_id: int) -> None:
        now = datetime.now(timezone.utc)
        self.waiting_users[str(user_id)] = {
            'guild_id': guild_id,
            'start_time': now.isoformat()
        }
        self.save_data()
        
        await asyncio.sleep(self.timeout)
        await self.verify_user(user_id)
    
    # ============================= Verify User =============================
    async def verify_user(self, user_id: int) -> None:
        entry = self.waiting_users.get(str(user_id))
        if not entry:
            return
        
        guild: discord.Guild = self.bot.get_guild(entry['guild_id'])
        member: discord.Member = guild.get_member(user_id)
        
        if member:
            # Only remove temp role if it's configured
            if self.temp_role_id != 0:
                temp_role = guild.get_role(self.temp_role_id)
                if temp_role and temp_role in member.roles:
                    await member.remove_roles(temp_role)
            
            # Only add verified role if it's configured
            if self.verified_role_id != 0:
                verified_role = guild.get_role(self.verified_role_id)
                if verified_role and verified_role not in member.roles:
                    await member.add_roles(verified_role)
            
            # INFO Log that the user has been verified
            await self.log.verification(f'User {member.name} ({member.id}) has been verified', 'verification', str(member.id))
            try:
                await member.send('✅ Verifica completata! Ora hai accesso al server. Buon divertimento!')
            except:
                pass
        
        # Cleanup
        del self.waiting_users[str(user_id)]
        self.save_data()
    
    # ============================= Restore Pending Tasks =============================
    async def restore_pending_tasks(self) -> None:
        async def delayed_verify(self, user_id: int, delay: int) -> None:
            await asyncio.sleep(delay)
            await self.verify_user(user_id)        
        
        now = datetime.now(timezone.utc)
        for user_id, data in list(self.waiting_users.items()):
            start_time: datetime = datetime.fromisoformat(data['start_time'])
            elapsed: int = (now - start_time).total_seconds()
            remaining: int = self.timeout - elapsed
            
            if remaining <= 0:
                await self.verify_user(int(user_id))
            else:
                asyncio.create_task(delayed_verify(int(user_id), remaining))
    
