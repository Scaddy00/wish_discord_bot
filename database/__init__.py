
# ----------------------------- Standard libraries -----------------------------
# Standard library imports
import sqlite3
from sqlite3 import Connection, Cursor
from os import getenv, path, mkdir

# ============================= DB Manager class =============================
class DB():
    """
    Database manager class for SQLite operations.
    
    Handles all database operations including insert, get, and delete operations
    for events, commands, messages, errors, and verification records.
    """
    
    def __init__(self) -> None:
        """
        Initialize the database manager.
        
        Sets up the database path, creates necessary tables if they don't exist,
        and initializes connection variables.
        """
        self.tables: list[str] = ['events', 'commands', 'messages', 'errors', 'verification', 'welcome']
        self.db_path: str = ''
        self.conn: Connection | None = None
        self.cursor: Cursor | None = None
        self.configure_db()
    
    # >>==============<< Create Table >>==============<< 
    def create_table(self, table_name: str) -> str:
        """
        Generate SQL CREATE TABLE statement for the specified table.
        
        Args:
            table_name (str): Name of the table to create ('events', 'commands', 
                            'messages', 'errors', 'verification', 'welcome')
        
        Returns:
            str: SQL CREATE TABLE statement
            
        Raises:
            ValueError: If table_name is not recognized
        """
        if table_name == 'events':
            return 'CREATE TABLE IF NOT EXISTS events (timestamp TEXT, type TEXT, message TEXT);'
        elif table_name == 'commands':
            return 'CREATE TABLE IF NOT EXISTS commands (timestamp TEXT, type TEXT, command TEXT, message TEXT);'
        elif table_name == 'messages':
            return 'CREATE TABLE IF NOT EXISTS messages (timestamp TEXT, channel_id TEXT, channel_name TEXT, user_id TEXT, user_name TEXT, message TEXT, to_maintain TEXT);'
        elif table_name == 'errors':
            return 'CREATE TABLE IF NOT EXISTS errors (timestamp TEXT, type TEXT, message TEXT);'
        elif table_name == 'verification':
            return 'CREATE TABLE IF NOT EXISTS verification (timestamp TEXT, status TEXT, user_id TEXT, message TEXT);'
        elif table_name == 'welcome':
            return 'CREATE TABLE IF NOT EXISTS welcome (timestamp TEXT, user_id TEXT, user_name TEXT);'
        else:
            raise ValueError(f"Tried to create unknown table: {table_name}")

    # >>==============<< Configure DB >>==============<< 
    def configure_db(self) -> None:
        """
        Configure the database by setting up the path and creating all necessary tables.
        
        Creates the data directory if it doesn't exist, sets the database file path,
        and creates all tables defined in self.tables.
        """
        # Get folder path and check if exist
        folder_path: str = getenv('DATA_PATH')
        if not path.exists(folder_path):
            mkdir(folder_path)
        # Get file path and check if exist
        self.db_path = f'{folder_path}/{getenv("DB_FILE_NAME")}'
        # if not path.exists(self.db_path):
        
        # Create tables on first run
        self.open_db()
        for table in self.tables:
            self.cursor.execute(self.create_table(table))
            self.conn.commit()
        self.close_db()
    
    # >>==============<< Open DB >>==============<< 
    def open_db(self) -> None:
        """
        Open a new database connection and create a cursor.
        
        Establishes a connection to the SQLite database file and creates
        a cursor for executing SQL operations.
        """
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
    
    # ============================= Insert Functions =============================
    # >>==============<< Insert Event >>==============<< 
    def insert_event(self, timestamp: str, record_type: str, message: str) -> None:
        """
        Insert an event record into the database.
        
        Args:
            timestamp (str): ISO format timestamp of the event
            record_type (str): Type/category of the event
            message (str): Event message or description
        """
        self.open_db()
        self.cursor.execute(
            'INSERT INTO events (timestamp, type, message) VALUES (?, ?, ?)',
            (timestamp, record_type, message)
        )
        self.conn.commit()
        self.close_db()
    
    # >>==============<< Insert Command >>==============<< 
    def insert_command(self, timestamp: str, record_type: str, command: str, message: str) -> None:
        """
        Insert a command record into the database.
        
        Args:
            timestamp (str): ISO format timestamp of the command execution
            record_type (str): Type/category of the command
            command (str): The command that was executed
            message (str): Additional message or context about the command
        """
        self.open_db()
        self.cursor.execute(
            'INSERT INTO commands (timestamp, type, command, message) VALUES (?, ?, ?, ?)',
            (timestamp, record_type, command, message)
        )
        self.conn.commit()
        self.close_db()
        
    # >>==============<< Insert Message >>==============<< 
    def insert_message(self, timestamp: str, channel_id: str, channel_name: str, user_id: str, user_name: str, message: str, to_maintain: str = 'False') -> None:
        """
        Insert a message record into the database.
        
        Args:
            timestamp (str): ISO format timestamp of the message
            channel_id (str): Discord channel ID where the message was sent
            channel_name (str): Name of the Discord channel
            user_id (str): Discord user ID who sent the message
            user_name (str): Username who sent the message
            message (str): Content of the message
            to_maintain (str, optional): Flag indicating if message should be maintained. Defaults to 'False'
        """
        self.open_db()
        self.cursor.execute(
            'INSERT INTO messages (timestamp, channel_id, channel_name, user_id, user_name, message, to_maintain) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (timestamp, channel_id, channel_name, user_id, user_name, message, to_maintain)
        )
        self.conn.commit()
        self.close_db()

    # >>==============<< Insert Error >>==============<< 
    def insert_error(self, timestamp: str, record_type: str, message: str) -> None:
        """
        Insert an error record into the database.
        
        Args:
            timestamp (str): ISO format timestamp of the error occurrence
            record_type (str): Type/category of the error
            message (str): Error message or description
        """
        self.open_db()
        self.cursor.execute(
            'INSERT INTO errors (timestamp, type, message) VALUES (?, ?, ?)',
            (timestamp, record_type, message)
        )
        self.conn.commit()
        self.close_db()
    
    # >>==============<< Insert Verification >>==============<< 
    def insert_verification(self, timestamp: str, status: str, user_id: str, message: str) -> None:
        """
        Insert a verification record into the database.
        
        Args:
            timestamp (str): ISO format timestamp of the verification attempt
            status (str): Status of the verification (success, failed, pending, etc.)
            user_id (str): Discord user ID being verified
            message (str): Additional message or context about the verification
        """
        self.open_db()
        self.cursor.execute(
            'INSERT INTO verification (timestamp, status, user_id, message) VALUES (?, ?, ?, ?)',
            (timestamp, status, user_id, message)
        )
        self.conn.commit()
        self.close_db()

    # >>==============<< Insert Welcome >>==============<< 
    def insert_welcome(self, timestamp: str, user_id: str, user_name: str) -> None:
        """
        Insert a welcome record into the database.
        
        Args:
            timestamp (str): ISO format timestamp of the welcome message
            user_id (str): Discord user ID who received the welcome message
            user_name (str): Username who received the welcome message
        """
        self.open_db()
        self.cursor.execute(
            'INSERT INTO welcome (timestamp, user_id, user_name) VALUES (?, ?, ?)',
            (timestamp, user_id, user_name)
        )
        self.conn.commit()
        self.close_db()
    
    # ============================= Get Functions =============================
    # >>==============<< Get Events by Type and Date Range >>==============<< 
    def get_events(self, event_types: list, start_time: str, end_time: str) -> list:
        """
        Get events of given types between start_time and end_time.
        
        Args:
            event_types (list): List of event types to filter by
            start_time (str): ISO format start timestamp
            end_time (str): ISO format end timestamp
            
        Returns:
            list: List of tuples containing (timestamp, type, message) for matching events
        """
        self.open_db()
        placeholders = ','.join('?' for _ in event_types)
        query = f"SELECT timestamp, type, message FROM events WHERE type IN ({placeholders}) AND timestamp BETWEEN ? AND ?"
        params = event_types + [start_time, end_time]
        self.cursor.execute(query, params)
        result = self.cursor.fetchall()
        self.close_db()
        return result

    # >>==============<< Get Messages by Date Range >>==============<< 
    def get_messages(self, start_time: str, end_time: str) -> list:
        """
        Get messages between start_time and end_time.
        
        Args:
            start_time (str): ISO format start timestamp
            end_time (str): ISO format end timestamp
            
        Returns:
            list: List of tuples containing (timestamp, channel_id, channel_name, user_id, user_name, message) for matching messages
        """
        self.open_db()
        query = "SELECT timestamp, channel_id, channel_name, user_id, user_name, message FROM messages WHERE timestamp BETWEEN ? AND ?"
        self.cursor.execute(query, (start_time, end_time))
        result = self.cursor.fetchall()
        self.close_db()
        return result
    
    # >>==============<< Get Welcome by User ID >>==============<< 
    def get_welcome(self, user_id: str = None) -> dict | list:
        """
        Get welcome message for a given user ID or all welcome messages.
        
        Args:
            user_id (str): Discord user ID to search for
            
        Returns:
            dict | list: Dictionary containing (timestamp, user_id, user_name) for matching welcome message or empty dictionary if no welcome message found or list of dictionaries for all welcome messages
        """
        self.open_db()
        if user_id:
            query = "SELECT timestamp, user_id, user_name FROM welcome WHERE user_id = ?"   
            self.cursor.execute(query, (user_id,))
        else:
            query = "SELECT timestamp, user_id, user_name FROM welcome"
            self.cursor.execute(query)
        result = self.cursor.fetchall()
        self.close_db()
        
        if user_id:
            output: dict = {}
            if result:
                output = { 
                'timestamp': result[0][0],
                'user_id': int(result[0][1]),
                'user_name': result[0][2]
            }
        else:
            output: list = []
            if result:
                for row in result:
                    output.append({
                        'timestamp': row[0],
                        'user_id': int(row[1]),
                        'user_name': row[2]
                    })
        return output
    
    # ============================= Delete Functions =============================
    # >>==============<< Delete Messages by Date Range >>==============<< 
    def delete_messages_by_range(self, start_time: str, end_time: str) -> int:
        """
        Delete messages between start_time and end_time.
        
        Only deletes messages where to_maintain is set to 'False'.
        Messages with to_maintain = 'True' will be preserved.
        
        Args:
            start_time (str): ISO format start timestamp
            end_time (str): ISO format end timestamp
            
        Returns:
            int: Number of deleted rows
        """
        
        self.open_db()
        query = "DELETE FROM messages WHERE timestamp BETWEEN ? AND ? AND to_maintain = 'False'"
        self.cursor.execute(query, (start_time, end_time))
        deleted_count = self.cursor.rowcount
        self.conn.commit()
        self.close_db()
        return deleted_count
    
    # >>==============<< Delete Events by Date Range >>==============<< 
    def delete_events_by_range(self, start_time: str, end_time: str, event_types: list = None) -> int:
        """
        Delete events between start_time and end_time.
        
        Args:
            start_time (str): ISO format start timestamp
            end_time (str): ISO format end timestamp
            event_types (list, optional): List of event types to filter deletion. 
                                       If None, deletes all events in the range
            
        Returns:
            int: Number of deleted rows
        """
        
        self.open_db()
        if event_types:
            placeholders = ','.join('?' for _ in event_types)
            query = f"DELETE FROM events WHERE type IN ({placeholders}) AND timestamp BETWEEN ? AND ?"
            params = event_types + [start_time, end_time]
        else:
            query = "DELETE FROM events WHERE timestamp BETWEEN ? AND ?"
            params = [start_time, end_time]
        
        self.cursor.execute(query, params)
        deleted_count = self.cursor.rowcount
        self.conn.commit()
        self.close_db()
        return deleted_count
    
    # >>==============<< Delete Commands by Date Range >>==============<< 
    def delete_commands_by_range(self, start_time: str, end_time: str, command_types: list = None) -> int:
        """
        Delete commands between start_time and end_time.
        
        Args:
            start_time (str): ISO format start timestamp
            end_time (str): ISO format end timestamp
            command_types (list, optional): List of command types to filter deletion.
                                         If None, deletes all commands in the range
            
        Returns:
            int: Number of deleted rows
        """
        
        self.open_db()
        if command_types:
            placeholders = ','.join('?' for _ in command_types)
            query = f"DELETE FROM commands WHERE type IN ({placeholders}) AND timestamp BETWEEN ? AND ?"
            params = command_types + [start_time, end_time]
        else:
            query = "DELETE FROM commands WHERE timestamp BETWEEN ? AND ?"
            params = [start_time, end_time]
        
        self.cursor.execute(query, params)
        deleted_count = self.cursor.rowcount
        self.conn.commit()
        self.close_db()
        return deleted_count
    
    # ============================= Close Functions =============================
    # >>==============<< Close DB >>==============<< 
    def close_db(self) -> None:
        """
        Close the database connection.
        
        Safely closes the current database connection and cursor.
        """
        self.conn.close()