
# ----------------------------- Imported Libraries -----------------------------
import discord
from os import getenv, path
# ----------------------------- Custom Libraries -----------------------------
from utility.file_io import read_file, write_file
from logger.logger import Logger

def start() -> None:
    config_path: str = path.join(str(getenv('MAIN_PATH')), str(getenv('CONFIG_FILE_NAME')))
    
    if path.exists(config_path):
        return
    else:
        config: dict = {
            'twitch': {
                'streamer': '',
                'stream_started': ''
                },
            'roles': {}
        }
        
        write_file(config_path, config)

async def load_data(log: Logger, guild: discord.Guild, event: str, first_sec: str, second_sec: str = '', third_sec: str = '') -> tuple[str, dict, None]:
    # Load communication channel
    communication_channel = guild.get_channel(int(getenv('BOT_COMMUNICATION_CHANNEL_ID')))
    
    # Load config file
    config_path: str = path.join(str(getenv('MAIN_PATH')), str(getenv('CONFIG_FILE_NAME')))
    config: dict = read_file(config_path)

    if first_sec not in config: # Check if the first section is part of the json file. If is not part of the file, log an error and return None
        error_message: str = f'Errore durante il caricamento dei seguenti dati dal file config.json\n[{first_sec}][{second_sec}][{third_sec}]\nIl campo \'{first_sec}\' non è stato trovato all\'interno della prima ricerca nel json.'
        log.error(error_message, f'{event} - LOAD DATA')
        await communication_channel.send(log.error_message(event, error_message))
        return
    else:
        if second_sec not in config[first_sec]: # Check if the second section is part of the json file. If is not part of the file, log an error and return None
            error_message: str = f'Errore durante il caricamento dei seguenti dati dal file config.json\n[{first_sec}][{second_sec}][{third_sec}]\nIl campo \'{second_sec}\' non è stato trovato all\'interno della seconda ricerca nel json.'
            log.error(error_message, f'{event} - LOAD DATA')
            await communication_channel.send(log.error_message(event, error_message))
            return 
        elif second_sec == '': # Check if the second section is the default value. If is true, return the entire first section of the file json
            return config[first_sec]
        else:
            if third_sec not in config[first_sec][second_sec]:
                error_message: str = f'Errore durante il caricamento dei seguenti dati dal file config.json\n[{first_sec}][{second_sec}][{third_sec}]\nIl campo \'{third_sec}\' non è stato trovato all\'interno della terza ricerca nel json.'
                log.error(error_message, f'{event} - LOAD DATA')
                await communication_channel.send(log.error_message(event, error_message))
                return None
            elif third_sec == '':
                return config[first_sec][second_sec]
            else:
                return config[first_sec][second_sec][third_sec]
    
async def update_data(log: Logger, guild: discord.Guild, new_data: str | dict, section: list) -> None:
    # Load communication channel
    communication_channel = guild.get_channel(int(getenv('BOT_COMMUNICATION_CHANNEL_ID')))
    
    # Load config file
    config_path: str = path.join(str(getenv('MAIN_PATH')), str(getenv('CONFIG_FILE_NAME')))
    config: dict = read_file(config_path)
    
    try:
        if len(section) == 1:
            config[section[0]] = new_data
        elif len(section) > 1:
            config[section[0]][section[1]] = new_data
        
        # Save updated config file
        write_file(config_path, config)
        
    except Exception as e:
        # EXCEPTION
        error_message: str = f'Errore durante l\'update dei dati nel file config.json.\n{e}'
        await log.error(error_message, 'EVENT - ROLE ASSIGN AUTO')
        await communication_channel.send(log.error_message(command='EVENT - ROLE ASSIGN AUTO', message=error_message))
