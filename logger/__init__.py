
# ----------------------------- Standard libraries -----------------------------
from os import getenv, path, mkdir
# ----------------------------- Custom libraries -----------------------------
from utils.file_io import write_file, read_file
from utils.printing import format_datetime_now
from database import DB

# ============================= Logger class =============================
class Logger():
    """
    Logger class for handling all logging operations.
    
    Provides methods to log events, commands, messages, errors, and verification
    records to the database with proper timestamps.
    """
    
    def __init__(self) -> None:
        """
        Initialize the Logger with a database connection.
        
        Creates a new database instance for storing log records.
        """
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
        """
        Log a command execution to the database.
        
        Args:
            log_message (str): The log message describing the command execution
            record_type (str): The type/category of the command
            command (str): The actual command that was executed
        """
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
        """
        Log a Discord message to the database.
        
        Args:
            log_message (str): The content of the message
            channel_id (str): Discord channel ID where the message was sent
            channel_name (str): Name of the Discord channel
            user_id (str): Discord user ID who sent the message
            user_name (str): Username who sent the message
        """
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
        """
        Log an error to the database.
        
        Args:
            log_message (str): The error message or description
            record_type (str): The type/category of the error
        """
        # Load formatted datetime now
        now: str = format_datetime_now()

        # Insert new record to db
        self.db.insert_error(
            timestamp=now,
            record_type=record_type,
            message=log_message
        )

    # >>==============<< New Verification Record >>==============<< 
    async def verification(self, log_message: str, status: str, user_id: str) -> None:
        """
        Log a verification attempt to the database.
        
        Args:
            log_message (str): The verification message or description
            status (str): The status of the verification (success, failed, pending, etc.)
            user_id (str): Discord user ID being verified
        """
        # Load formatted datetime now
        now: str = format_datetime_now()

        # Insert new record to db
        self.db.insert_verification(timestamp=now, status=status, user_id=user_id, message=log_message)
        
    # >>==============<< Error Message >>==============<<
    def error_message(self, command: str, message: str) -> str:
        """
        Create a formatted error message string.
        
        Args:
            command (str): The command or operation that failed
            message (str): The error message or description
            
        Returns:
            str: Formatted error message in the format 'command -> message'
        """
        return f'{command} -> {message}'

    