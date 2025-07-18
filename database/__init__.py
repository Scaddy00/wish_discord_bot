
# ----------------------------- Standard libraries -----------------------------
import sqlite3
from sqlite3 import Connection, Cursor
from os import getenv, path, mkdir

# ============================= DB Manager class =============================
class DB():
    def __init__(self):
        self.tables: dict = ['events', 'commands', 'messages', 'errors', 'verification']
        self.db_path: str = ''
        self.conn: Connection = None
        self.cursor: Cursor = None
        self.configure_db()
    
    # >>==============<< Create Table >>==============<< 
    def create_table(self, table_name: str) -> str:
        if table_name == 'events':
            return 'CREATE TABLE IF NOT EXISTS events (timestamp TEXT, type TEXT, message TEXT);'
        elif table_name == 'commands':
            return 'CREATE TABLE IF NOT EXISTS commands (timestamp TEXT, type TEXT, command TEXT, message TEXT);'
        elif table_name == 'messages':
            return 'CREATE TABLE IF NOT EXISTS messages (timestamp TEXT, channel_id TEXT, channel_name TEXT, user_id TEXT, user_name TEXT, message TEXT);'
        elif table_name == 'errors':
            return 'CREATE TABLE IF NOT EXISTS errors (timestamp TEXT, type TEXT, message TEXT);'
        elif table_name == 'verification':
            return 'CREATE TABLE IF NOT EXISTS verification (timestamp TEXT, status TEXT, user_id TEXT, message TEXT);'
        else:
            raise ValueError(f"Tried to create unknown table: {table_name}")

    # >>==============<< Configure DB >>==============<< 
    def configure_db(self) -> None:
        # Get folder path and check if exist
        folder_path: str = getenv('DATA_PATH')
        if not path.exists(folder_path):
            mkdir(folder_path)
        # Get file path and check if exist
        self.db_path = f'{folder_path}/{getenv("DB_FILE_NAME")}'
        # if not path.exists(self.db_path):
        
        # Connect to db
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # Create tables
        for table in self.tables:
            self.cursor.execute(self.create_table(table))
            self.conn.commit()
    
    # >>==============<< Insert Event >>==============<< 
    def insert_event(self, timestamp: str, record_type: str, message: str) -> None:
        self.cursor.execute(
            'INSERT INTO events (timestamp, type, message) VALUES (?, ?, ?)',
            (timestamp, record_type, message)
        )
        self.conn.commit()
    
    # >>==============<< Insert Command >>==============<< 
    def insert_command(self, timestamp: str, record_type: str, command: str, message: str) -> None:
        self.cursor.execute(
            'INSERT INTO commands (timestamp, type, command, message) VALUES (?, ?, ?, ?)',
            (timestamp, record_type, command, message)
        )
        self.conn.commit()
        
    # >>==============<< Insert Message >>==============<< 
    def insert_message(self, timestamp: str, channel_id: str, channel_name: str, user_id: str, user_name: str, message: str) -> None:
        self.cursor.execute(
            'INSERT INTO messages (timestamp, channel_id, channel_name, user_id, user_name, message) VALUES (?, ?, ?, ?, ?, ?)',
            (timestamp, channel_id, channel_name, user_id, user_name, message)
        )
        self.conn.commit()

    # >>==============<< Insert Error >>==============<< 
    def insert_error(self, timestamp: str, record_type: str, message: str) -> None:
        self.cursor.execute(
            'INSERT INTO errors (timestamp, type, message) VALUES (?, ?, ?)',
            (timestamp, record_type, message)
        )
        self.conn.commit()
    
    # >>==============<< Insert Verification >>==============<< 
    def insert_verification(self, timestamp: str, status: str, user_id: str, message: str) -> None:
        self.cursor.execute(
            'INSERT INTO verification (timestamp, status, user_id, message) VALUES (?, ?, ?, ?)',
            (timestamp, status, user_id, message)
        )
        self.conn.commit()

    # >>==============<< Get Events by Type and Date Range >>==============<< 
    def get_events(self, event_types: list, start_time: str, end_time: str) -> list:
        """Get events of given types between start_time and end_time (ISO format)."""
        placeholders = ','.join('?' for _ in event_types)
        query = f"SELECT timestamp, type, message FROM events WHERE type IN ({placeholders}) AND timestamp BETWEEN ? AND ?"
        params = event_types + [start_time, end_time]
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    # >>==============<< Get Messages by Date Range >>==============<< 
    def get_messages(self, start_time: str, end_time: str) -> list:
        """Get messages between start_time and end_time (ISO format)."""
        query = "SELECT timestamp, channel_id, channel_name, user_id, user_name, message FROM messages WHERE timestamp BETWEEN ? AND ?"
        self.cursor.execute(query, (start_time, end_time))
        return self.cursor.fetchall()