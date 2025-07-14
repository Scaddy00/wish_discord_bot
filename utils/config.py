
# ----------------------------- Imported Libraries -----------------------------
import discord
from os import getenv, path
# ----------------------------- Custom Libraries -----------------------------
from .file_io import read_file, write_file
from logger import Logger

# ============================= Load Config File =============================
def config_file_path() -> str:
    return path.join(str(getenv('DATA_PATH')), str(getenv('CONFIG_FILE_NAME')))

# ============================= Load Config File =============================
def config_file() -> dict:
    return read_file(config_file_path())

# ============================= Start =============================
def start() -> None:
    config_path: str = config_file_path()
    
    if path.exists(config_path):
        return
    else:
        config: dict = {
            'roles': {},
            'rules': {},
            'exception': {}
        }
        
        write_file(config_path, config)

# ============================= Load Data =============================
async def load_data(log: Logger, guild: discord.Guild, event: str, first_sec: str, second_sec: str = '', third_sec: str = '') -> tuple[str, dict, None]:
    # Load communication channel
    communication_channel = guild.get_channel(int(getenv('BOT_COMMUNICATION_CHANNEL_ID')))
    
    # Load config file
    config: dict = config_file()
    
    if first_sec not in config:
        return
    else:
        if second_sec not in config[first_sec]:
            return
        elif second_sec == '':
            return config[first_sec]
        else:
            if third_sec not in config[first_sec][second_sec]:
                return
            elif third_sec == '':
                return config[first_sec][second_sec]
            else:
                return config[first_sec][second_sec][third_sec]
    
# ============================= Update Data =============================
async def update_data(log: Logger, guild: discord.Guild, new_data: str | dict, section: list) -> None:
    # Load communication channel
    communication_channel = guild.get_channel(int(getenv('BOT_COMMUNICATION_CHANNEL_ID')))
    
    # Load config file
    config: dict = config_file()
    
    try:
        if len(section) == 1:
            config[section[0]] = new_data
        elif len(section) > 1:
            config[section[0]][section[1]] = new_data
        
        # Save updated config file
        write_file(config_file_path(), config)
        
    except Exception as e:
        # EXCEPTION
        error_message: str = f'Errore durante l\'update dei dati nel file config.json.\n{e}'
        await log.error(error_message, 'CONFIG - UPDATE DATA')
        await communication_channel.send(log.error_message(command='CONFIG - UPDATE DATA', message=error_message))


# ============================= Exception =============================
# >>==============<< Load >>==============<<
def load_exception(tag: str) -> list[int]:
    # Load config file
    config: dict = config_file()
    
    return config['exception'].get(tag, [])

# >>==============<< Add >>==============<<
def add_exception(tag: str, data: list[int]) -> None:
    # Load config file
    config: dict = config_file()
    
    # Update data
    config['exception'][tag] = data

    # Save config.json data
    write_file(config_file_path(), config)

# ============================= Rules =============================
# >>==============<< Load >>==============<<
def load_rules(tag: str = '') -> tuple[dict, str]:
    # Load config file
    config: dict = config_file()
    
    if tag == '':
        return config['rules']
    else:
        return config['rules'].get(tag, '')

# >>==============<< Add >>==============<<
def add_rules(data: dict | str, tag: str = '') -> None:
    # Load config file
    config: dict = config_file()
    
    # Update data
    if tag == '':
        config['rules'] = data
    else:
        config['rules'][tag] = data

    # Save config.json data
    write_file(config_file_path(), config)