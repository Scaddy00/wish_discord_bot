
# ----------------------------- Standard libraries -----------------------------
from os import getenv, path, mkdir
# ----------------------------- Custom libraries -----------------------------
from utils.file_io import write_file, read_file
from utils.printing import format_datetime_now
from database import DB

# ============================= Logger class =============================
class Logger():
    def __init__(self) -> None:
        self.db: DB = DB()
    
    # >>==============<< New Event Record >>==============<< 
    async def event(self, log_message: str, record_type: str) -> None:
        """Add event to the log

        Parameters:
            log_message (str): The message of the event
            record_type (str): The record type of the event. 
            Can be:
            - guild_join
            - welcome
            - remove
            - twitch
            - youtube
            - instagram
            - tiktok
            - chat-clear
            - role-assign-auto
        """
        # Load formatted datetime now
        now: str = format_datetime_now()
        
        # Insert new record to db
        self.db.insert_event(
            timestamp=now, 
            record_type=record_type, 
            message=log_message
        )
        
    # >>==============<< New Command Record >>==============<< 
    async def command(self, log_message: str, record_type: str, command: str) -> None:
        # Load formatted datetime now
        now: str = format_datetime_now()
        
        # Insert new record to db
        self.db.insert_command(
            timestamp=now, 
            record_type=record_type, 
            command=command, 
            message=log_message
        )
    
    # >>==============<< New Message Record >>==============<< 
    async def message(self, log_message: str, channel_id: str, channel_name: str, user_id: str, user_name: str) -> None:
        # Load formatted datetime now
        now: str = format_datetime_now()

        # Insert new record to db
        self.db.insert_message(
            timestamp=now,
            channel_id=channel_id,
            channel_name=channel_name,
            user_id=user_id,
            user_name=user_name,
            message=log_message
        )
    
    # >>==============<< New Error Record >>==============<< 
    async def error(self, log_message: str, record_type: str) -> None:
        # Load formatted datetime now
        now: str = format_datetime_now()

        # Insert new record to db
        self.db.insert_error(
            timestamp=now,
            record_type=record_type,
            message=log_message
        )

    # >>==============<< Error Message >>==============<<
    def error_message(self, command: str, message: str) -> str:
        return f'{command} -> {message}'

    