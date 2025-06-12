# ----------------------------- Standard libraries -----------------------------
import logging
from os import getenv, path, mkdir
from datetime import datetime
# ----------------------------- Custom libraries -----------------------------
from utility.file_io import write_file, read_file
from utility.printing import format_datetime_now

# ============================= Logger class =============================
class Logger():
    def __init__(self, name: str) -> None:
        self.log: logging.Logger = logging.getLogger(f'{name}_logger')
        self.log_path: str = self.configure_logger()
    
    # >>==============<< Configure Logger >>==============<< 
    def configure_logger(self) -> str:
        log_file: dict = {
            'events': {
                'welcome': [],
                'remove': [],
                'twitch': [],
                'youtube': [],
                'instagram': [],
                'tiktok': [],
                'chat-clear': [],
                'role-assign-auto': []
            },
            'commands': {
                'test': [],
                'social': [],
                'admin': []
            },
            'messages': {},
            'errors': []
        }
        # Get path and file name from .env
        main_path: str = str(getenv('MAIN_PATH'))
        log_folder_path: str = str(getenv('LOG_FILE_PATH'))
        log_file_name: str = str(getenv('LOG_FILE_NAME'))
        
        complete_folder_path: str = path.join(main_path, log_folder_path)
        complete_file_path: str = path.join(complete_folder_path, log_file_name)
        
        # Check logs if folder exist, else create new folder
        if not path.exists(complete_folder_path):
            mkdir(complete_folder_path)
        
        # Check if log file exist
        if not path.exists(complete_file_path):
            write_file(complete_file_path, log_file)
        
        return complete_file_path
    
    # >>==============<< New Event Record >>==============<< 
    async def event(self, log_message: str, record_type: str) -> None:
        """Add event to the log

        Parameters:
            log_message (str): The message of the event
            record_type (str): The record type of the event. 
            Can be:
            - welcome
            - remove
            - twitch
            - youtube
            - instagram
            - tiktok
            - chat-clear
            - role-assign-auto
        """
        # Load log file
        log_file: dict = read_file(self.log_path)
        # Load formatted datetime now
        now = format_datetime_now()
        
        # Create json record
        record: dict = {'timestamp': now, 'message': log_message}
        
        # Add record
        log_file['events'][record_type].append(record)
        
        # Write changes in log file
        write_file(self.log_path, log_file)
        
    # >>==============<< New Command Record >>==============<< 
    async def command(self, log_message: str, record_type: str, command: str) -> None:
        # Load log file
        log_file: dict = read_file(self.log_path)
        # Load formatted datetime now
        now = format_datetime_now()
        
        # Create json record
        record: dict = {'timestamp': now, 'command': command, 'message': log_message}
        
        # Add record
        log_file['commands'][record_type].append(record)
        
        # Write changes in log file
        write_file(self.log_path, log_file)
    
    # >>==============<< New Message Record >>==============<< 
    async def message(self, log_message: str, channel_id: str, channel_name: str) -> None:
        # Load log file
        log_file: dict = read_file(self.log_path)
        # Load formatted datetime now
        now = format_datetime_now()
        
        # Create json record
        record: dict = {'timestamp': now, 'message': log_message}
        
        # Check if the corresponding channel_id key exists
        if channel_id in log_file['messages']:
            # Add record
            log_file['messages'][channel_id].append(record)
        else:
            # Create the missing key
            log_file['messages'][channel_id] = { 'name': channel_name, 'msg': []}
            # Add record
            log_file['messages'][channel_id]['msg'].append(record)
        
        # Write changes in log file
        write_file(self.log_path, log_file)
    
    # >>==============<< New Error Record >>==============<< 
    async def error(self, log_message: str, record_type: str) -> None:
        # Load log file
        log_file: dict = read_file(self.log_path)
        # Load formatted datetime now
        now = format_datetime_now()
        
        # Create json record
        record: dict = {'timestamp': now, 
                        'type': record_type, 
                        'message': log_message}
        
        # Add record
        log_file['errors'][record_type].append(record)
        
        # Write changes in log file
        write_file(self.log_path, log_file)

    # >>==============<< Error Message >>==============<<
    def error_message(self, command: str, message: str) -> str:
        return f'{command} -> {message}'

    