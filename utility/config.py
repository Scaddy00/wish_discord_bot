
# ----------------------------- Imported Libraries -----------------------------
import discord
from os import getenv, path
# ----------------------------- Custom Libraries -----------------------------
from utility.file_io import read_file, write_file
from logger.logger import Logger

# ============================= Load Config File =============================
def config_file_path() -> str:
    return path.join(str(getenv('MAIN_PATH')), str(getenv('CONFIG_FILE_NAME')))

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
            'twitch': {
                'streamer': '',
                'stream_started': ''
                },
            'roles': {},
            'rules': {},
            'channels': {},
            'exception': {}
        }
        
        write_file(config_path, config)

# ============================= Load Data =============================
async def load_data(log: Logger, guild: discord.Guild, event: str, first_sec: str, second_sec: str = '', third_sec: str = '') -> tuple[str, dict, None]:
    # Load communication channel
    communication_channel = guild.get_channel(int(getenv('BOT_COMMUNICATION_CHANNEL_ID')))
    
    # Load config file
    config: dict = config_file()

    if first_sec not in config: # Check if the first section is part of the json file. If is not part of the file, log an error and return None
        error_message: str = f'Errore durante il caricamento dei seguenti dati dal file config.json\n[{first_sec}][{second_sec}][{third_sec}]\nIl campo \'{first_sec}\' non è stato trovato all\'interno della prima ricerca nel json.'
        log.error(error_message, f'{event} - CONFIG - LOAD DATA')
        await communication_channel.send(log.error_message(f'{event} - CONFIG - LOAD DATA', error_message))
        return
    else:
        if second_sec not in config[first_sec]: # Check if the second section is part of the json file. If is not part of the file, log an error and return None
            error_message: str = f'Errore durante il caricamento dei seguenti dati dal file config.json\n[{first_sec}][{second_sec}][{third_sec}]\nIl campo \'{second_sec}\' non è stato trovato all\'interno della seconda ricerca nel json.'
            log.error(error_message, f'{event} - CONFIG - LOAD DATA')
            await communication_channel.send(log.error_message(f'{event} - CONFIG - LOAD DATA', error_message))
            return 
        elif second_sec == '': # Check if the second section is the default value. If is true, return the entire first section of the file json
            return config[first_sec]
        else:
            if third_sec not in config[first_sec][second_sec]:
                error_message: str = f'Errore durante il caricamento dei seguenti dati dal file config.json\n[{first_sec}][{second_sec}][{third_sec}]\nIl campo \'{third_sec}\' non è stato trovato all\'interno della terza ricerca nel json.'
                log.error(error_message, f'{event} - CONFIG - LOAD DATA')
                await communication_channel.send(log.error_message(f'{event} - CONFIG - LOAD DATA', error_message))
                return None
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

# ============================= Load Channels ID =============================
async def load_channel_id(channel_name: str) -> str:
    # Load config file
    config: dict = config_file()
    
    return config['channels'].get(channel_name, '')

# ============================= Add Data Channels ID =============================
async def add_data_channel_id(channel_name: str, channel_id: str) -> None:
    # Load config file
    config: dict = config_file()
    
    # Update data
    config['channels'][channel_name] = channel_id

    # Save config.json data
    write_file(config_file_path(), config)

# ============================= Load Channels ID =============================
async def load_exception(tag: str) -> list[int]:
    # Load config file
    config: dict = config_file()
    
    return config['exception'].get(tag, [])

# ============================= Add Channels ID =============================
async def add_exception(tag: str, data: list[int]) -> None:
    # Load config file
    config: dict = config_file()
    
    # Update data
    config['exception'][tag] = data

    # Save config.json data
    write_file(config_file_path(), config)