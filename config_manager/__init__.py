
# ----------------------------- Imported Libraries -----------------------------
import discord
from os import getenv, path
from typing import Union, List, Dict, Any, Optional, Tuple
# ----------------------------- Custom Libraries -----------------------------
from utils.file_io import read_file, write_file
from logger import Logger

default_config = {
    'admin': {
        'roles': {
            'server_booster': 0,
            'in_verification': 0,
            'verified': 0,
            'not_verified': 0
        },
        'channels': {
            'communication': 0,
            'report': 0,
            'rule': 0,
            'live': 0,
            'bye-bye': 0
        }
    },
    'roles': {},
    'rules': {
        'emoji': '',
        'message_id': 0,
        'embed_id': 0,
        'channel_id': 0
    },
    'exception': {},
    'message_logging': {
        'enabled': False,
        'channels': []
    },
    'retention_days': 90
}

class ConfigManager:
    """
    Class for managing the Discord bot configuration file.
    Handles CRUD operations on roles, rules, exceptions and other configurations.
    """
    
    def __init__(self):
        """Initialize the ConfigManager and create the configuration file if it doesn't exist."""
        self._config_path = self._get_config_path()
        self._initialize_config()
        
        self.communication_channel = self._load_communication_channel()
        self.report_channel = self._load_report_channel()
    
    def _get_config_path(self) -> str:
        """Returns the complete path of the configuration file."""
        return path.join(str(getenv('DATA_PATH')), str(getenv('CONFIG_FILE_NAME')))
    
    def _initialize_config(self) -> None:
        """Initialize the configuration file with the basic structure if it doesn't exist."""
        if not path.exists(self._config_path):
            write_file(self._config_path, default_config)
        else:
            config = self._load_config()
            
            # Check and add missing fields from default_config
            self._ensure_config_structure(config, default_config)
            
            self._save_config(config)
    
    def _ensure_config_structure(self, config: Dict[str, Any], default_structure: Dict[str, Any]) -> None:
        """
        Recursively ensure that all fields from default_structure exist in config.
        
        Args:
            config: Current configuration dictionary
            default_structure: Default configuration structure to check against
        """
        for key, default_value in default_structure.items():
            if key not in config:
                # Add missing key with default value
                config[key] = default_value
            elif isinstance(default_value, dict) and isinstance(config[key], dict):
                # Recursively check nested dictionaries
                self._ensure_config_structure(config[key], default_value)
            elif isinstance(default_value, list) and isinstance(config[key], list):
                # For lists, ensure they exist (don't modify content)
                pass
            # For other types (str, int, bool), the key exists so no action needed
    
    def _load_config(self) -> Dict[str, Any]:
        """Load and return the content of the configuration file."""
        return read_file(self._config_path)
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save the configuration to the file."""
        write_file(self._config_path, config)
    
    def _load_communication_channel(self) -> int:
        """Load the communication channel from the configuration file."""
        comm_channel_str = self.load_admin('channels', 'communication')
        if comm_channel_str and str(comm_channel_str).isdigit():
            return int(comm_channel_str)
        else:
            return None
    
    def _load_report_channel(self) -> int:
        """Load the report channel from the configuration file."""
        report_channel_str = self.load_admin('channels', 'report')
        if report_channel_str and str(report_channel_str).isdigit():
            return int(report_channel_str)
        else:
            return None
    
    # ============================= Generic Data Operations =============================
    
    async def load_data(self, first_sec: str, second_sec: str = '', third_sec: str = '') -> Optional[Any]:
        """
        Load data from configuration by navigating through nested sections.
        
        Args:
            log: Logger instance
            guild: Discord guild
            event: Event name
            first_sec: First section
            second_sec: Second section (optional)
            third_sec: Third section (optional)
            
        Returns:
            The requested data or None if not found
        """
        config = self._load_config()
        
        if first_sec not in config:
            return None
        
        if second_sec == '':
            return config[first_sec]
        
        if second_sec not in config[first_sec]:
            return None
        
        if third_sec == '':
            return config[first_sec][second_sec]
        
        if third_sec not in config[first_sec][second_sec]:
            return None
        
        return config[first_sec][second_sec][third_sec]
    
    async def update_data(self, log: Logger, guild: discord.Guild, new_data: Union[str, Dict], section: List[str]) -> None:
        """
        Update data in the configuration.
        
        Args:
            log: Logger instance
            guild: Discord guild
            new_data: New data to save
            section: List of sections to navigate
        """
        communication_channel = guild.get_channel(self.config.communication_channel)
        config = self._load_config()
        
        try:
            if len(section) == 1:
                config[section[0]] = new_data
            elif len(section) == 2:
                config[section[0]][section[1]] = new_data
            elif len(section) == 3:
                config[section[0]][section[1]][section[2]] = new_data
            
            self._save_config(config)
            
        except Exception as e:
            error_message = f'Errore durante l\'update dei dati nel file config.json.\n{e}'
            await log.error(error_message, 'CONFIG - UPDATE DATA')
            await communication_channel.send(log.error_message(command='CONFIG - UPDATE DATA', message=error_message))
    
    # ============================= Admin Management =============================

    def load_admin(self, section: str = '', tag: str = '') -> Union[dict, str, int, None]:
        """
        Load admin configuration data from a specific section.
        
        Args:
            section (str): The configuration section to load from
            tag (str, optional): Specific tag within the section. If empty, returns entire section
        
        Returns:
            Union[dict, str, int, None]: Configuration data for the specified section/tag
        """
        config = self._load_config()
        
        if section == '':
            return config['admin']
        
        if tag == '':
            return config['admin'][section]
        
        return config['admin'][section].get(tag, None)

    def add_admin(self, section: str, tag: str, data: str) -> None:
        """
        Add or replace an entire admin section with new data.
        
        Args:
            section (str): The configuration section to add/replace
            data (dict): The data to store in the section
        """
        config = self._load_config()
        config['admin'][section][tag] = data
        self._save_config(config)

    def remove_admin(self, section: str, tag: str = '') -> None:
        """
        Remove a specific tag from an admin section.
        
        Args:
            section (str): The configuration section to modify
            tag (str, optional): The specific tag to remove. If empty, no action is taken
        """
        config = self._load_config()
        # Check if the tag exists before attempting to delete it
        if tag != '' and tag in config['admin'][section]:
            del config['admin'][section][tag]
            self._save_config(config)

    def update_admin(self, section: str, value: str | dict, tag: str = '') -> None:
        """
        Update admin configuration with new values.
        
        Args:
            section (str): The configuration section to update
            value (str | dict): The new value to set
            tag (str, optional): Specific tag to update. If empty, updates entire section
        """
        config = self._load_config()
        # If no tag specified and value is a dictionary, replace entire section
        if tag == '' and isinstance(value, dict):
            config['admin'][section] = value
        else:
            # Update specific tag within the section
            config['admin'][section][tag] = value
        
        self._save_config(config)
            
    # ============================= Exception Management =============================
    
    def load_exception(self, tag: str) -> List[int]:
        """
        Load exceptions for a specific tag.
        
        Parameters:
            tag: Exception tag
            
        Returns:
            List of exception IDs
        """
        config = self._load_config()
        return config['exception'].get(tag, [])
    
    def add_exception(self, tag: str, data: List[int]) -> None:
        """
        Add exceptions for a specific tag.
        
        Parameters:
            tag: Exception tag
            data: List of IDs to add
        """
        config = self._load_config()
        config['exception'][tag] = data
        self._save_config(config)
    
    def remove_exception(self, tag: str) -> None:
        """
        Remove all exceptions for a specific tag.
        
        Parameters:
            tag: Exception tag to remove
        """
        config = self._load_config()
        if tag in config['exception']:
            del config['exception'][tag]
            self._save_config(config)
    
    def update_exception(self, tag: str, user_id: int, add: bool = True) -> None:
        """
        Add or remove a single ID from exceptions.
        
        Parameters:
            tag: Exception tag
            user_id: User ID to add/remove
            add: True to add, False to remove
        """
        config = self._load_config()
        exceptions = config['exception'].get(tag, [])
        
        if add and user_id not in exceptions:
            exceptions.append(user_id)
        elif not add and user_id in exceptions:
            exceptions.remove(user_id)
        
        config['exception'][tag] = exceptions
        self._save_config(config)
    
    # ============================= Rules Management =============================
    
    def load_rules(self, tag: str = '') -> Union[Dict[str, Any], str]:
        """
        Load rules from configuration.
        
        Parameters:
            tag: Specific rule tag (optional)
            
        Returns:
            All rules or a specific rule
        """
        config = self._load_config()
        
        if tag == '':
            return config['rules']
        else:
            return config['rules'].get(tag, '')
    
    def add_rules(self, data: Union[Dict[str, Any], str], tag: str = '') -> None:
        """
        Add rules to configuration.
        
        Parameters:
            data: Rule data
            tag: Specific tag (optional)
        """
        config = self._load_config()
        
        if tag == '':
            config['rules'] = data
        else:
            config['rules'][tag] = data
        
        self._save_config(config)
    
    def remove_rule(self, tag: str) -> None:
        """
        Remove a specific rule.
        
        Parameters:
            tag: Rule tag to remove
        """
        config = self._load_config()
        if tag in config['rules']:
            del config['rules'][tag]
            self._save_config(config)
    
    # ============================= Role Management =============================
    
    def load_roles(self, tag: str = '') -> Union[Dict[str, Any], Any]:
        """
        Load roles from configuration.
        
        Parameters:
            tag: Specific role tag (optional)
            
        Returns:
            All roles or a specific role
        """
        config = self._load_config()
        
        if tag == '':
            return config['roles']
        else:
            return config['roles'].get(tag, None)
    
    def add_role(self, tag: str, data: Any) -> None:
        """
        Add a role to configuration.
        
        Parameters:
            tag: Role tag
            data: Role data
        """
        config = self._load_config()
        config['roles'][tag] = data
        self._save_config(config)
    
    def remove_role(self, tag: str) -> None:
        """
        Remove a role from configuration.
        
        Parameters:
            tag: Role tag to remove
        """
        config = self._load_config()
        if tag in config['roles']:
            del config['roles'][tag]
            self._save_config(config)
    
    # ============================= Message Logging Management =============================
    def load_message_logging(self) -> dict:
        """
        Load message logging configuration.
        
        Returns:
            Message logging configuration
        """
        config = self._load_config()
        return config['message_logging']
    
    def enable_message_logging(self) -> None:
        """
        Enable message logging.
        """
        config = self._load_config()
        config['message_logging']['enabled'] = True
        self._save_config(config)
    
    def disable_message_logging(self) -> None:
        """
        Disable message logging.
        """
        config = self._load_config()
        config['message_logging']['enabled'] = False
        self._save_config(config)
    
    def load_message_logging_channels(self) -> List[int]:
        """
        Load message logging channels.
        
        Returns:
            List of channel IDs
        """
        config = self._load_config()
        return config['message_logging']['channels']
    
    def add_message_logging_channel(self, channel_id: int) -> None:
        """
        Add a channel to message logging.
        
        Parameters:
            channel_id: Channel ID to add
        """
        config = self._load_config()
        config['message_logging']['channels'].append(channel_id)
        self._save_config(config)
    
    def remove_message_logging_channel(self, channel_id: int) -> None:
        """
        Remove a channel from message logging.
        
        Parameters:
            channel_id: Channel ID to remove
        """
        config = self._load_config()
        config['message_logging']['channels'].remove(channel_id)
        self._save_config(config)
    
    # ============================= Retention Days Management =============================
    def load_retention_days(self) -> int:
        """
        Load the retention period (in days)
        Returns:
            int: Number of days to retain log messages
        """
        config = self._load_config()
        return config['retention_days']
    
    def update_retention_days(self, days: int) -> None:
        """
        Update the retention period (in days)
        """
        config = self._load_config()
        config['retention_days'] = days
        self._save_config(config)
    
    # ============================= Utility Methods =============================
    
    def get_config_path(self) -> str:
        """Returns the configuration file path."""
        return self._config_path
    
    def config_exists(self) -> bool:
        """Check if the configuration file exists."""
        return path.exists(self._config_path)
    
    def get_full_config(self) -> Dict[str, Any]:
        """Returns the entire configuration."""
        return self._load_config()
    
    def backup_config(self, backup_path: str) -> None:
        """
        Create a backup of the configuration.
        
        Parameters:
            backup_path: Path where to save the backup
        """
        config = self._load_config()
        write_file(backup_path, config)