
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import commands
from os import getenv, path
from twitchAPI.twitch import Twitch
from twitchAPI.object.api import Stream
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from config_manager import ConfigManager
from utils.printing import create_embed, format_datetime_now_extended, format_datetime_extended
from .views_modals.stream_button_view import StreamButtonView
from utils.file_io import read_file, write_file

class TwitchApp():
    def __init__(self, bot: commands.Bot, log: Logger, config: ConfigManager):
        """
        Initializes the Twitch app with Discord bot, logger, and config manager.
        """
        # Twitch API credentials
        app_id = getenv('TWITCH_CLIENT_ID')
        app_secret = getenv('TWITCH_CLIENT_SECRET')
        # Core references
        self.log = log
        self.bot = bot
        self.config = config
        # Data file path for Twitch stream info
        self.file_path: str = path.join(getenv('DATA_PATH'), getenv('TWITCH_FILE_NAME'))
        self.stream_info: dict = {}
        self.streamer_name: str = ''
        self.url: str = getenv('TWITCH_URL')
        # Discord channel for live notifications
        live_channel = self.config.load_admin('channels', 'live')
        self.channel_id: int = int(live_channel) if live_channel and str(live_channel).isdigit() else None
        # Embed color as hex string
        self.color: str = f"0x{getenv('TWITCH_COLOR')}"
        # Twitch API client
        self.app: Twitch = Twitch(app_id, app_secret)
        # Initialize data and state
        self.setup()
    
    # ============================= Authentication =============================
    async def _authenticate(self) -> None:
        await self.app.authenticate_app([])
    
    # ============================= Data Loading =============================
    def load_data(self) -> dict:
        """
        Load Twitch data from file if it exists, otherwise return an empty dict.
        """
        if path.exists(self.file_path):
            return read_file(self.file_path)
        else:
            return {}
    
    # ============================= Data Reloading =============================
    def reload_data(self, data) -> None:
        """
        Reloads stream and config data from the provided dictionary.
        """
        self.streamer_name = data['config'].get('streamer_name', '')
        self.url = f'{self.url}{self.streamer_name}' if self.streamer_name != '' else self.url
        self.stream_info = data.get('stream', {})
    
    # ============================= Save Stream Status =============================
    def save_status(self) -> None:
        """
        Save the current stream_info to the data file.
        """
        data: dict = self.load_data()
        data['stream'] = self.stream_info
        write_file(self.file_path, data)
    
    # ============================= Embed Image Management =============================
    def add_image(self, new_image: dict) -> None:
        """
        Add or update an image URL for a given tag in the embed images section.
        After adding, sort the tags alphabetically.
        """
        data: dict = self.load_data()
        images = data.setdefault('embeds', {}).setdefault('images', {})
        images[new_image['tag']] = new_image['url']
        # Sort tags alphabetically
        data['embeds']['images'] = dict(sorted(images.items()))
        write_file(self.file_path, data)
    
    # ============================= Embed Title Management =============================
    def change_title(self, new_title: dict) -> None:
        """
        Add or update a title for a given tag in the embed titles section.
        """
        data: dict = self.load_data()
        data.setdefault('embeds', {}).setdefault('titles', {})[new_title['tag']] = new_title['title']
        write_file(self.file_path, data)

    # ============================= Streamer Name Management =============================
    def change_streamer_name(self, new_name: str) -> None:
        """
        Update the streamer name in the config and in memory.
        """
        data: dict = self.load_data()
        data['config']['streamer_name'] = new_name
        self.streamer_name = new_name
        write_file(self.file_path, data)

    # ============================= Default Stream Info =============================
    def set_default_stream_info(self) -> None:
        """
        Reset stream_info to default (offline) values and save to file.
        """
        self.stream_info = {
            'status': 'OFF',
            'message_id': '',
            'id': '',
            'title': '',
            'game': '',
            'started_at': '',
            'ended_at': '',
            'image_tag': ''
        }
        self.save_status()
    
    # ============================= Initial Setup =============================
    def setup(self) -> None:
        """
        Initialize the data file with default values if it does not exist, otherwise load existing data.
        """
        default: dict = {}
        if not path.exists(self.file_path):
            default = {
                'config': {
                    'streamer_name': ''
                },
                'stream': {
                    'status': 'OFF',
                    'message_id': '',
                    'id': '',
                    'title': '',
                    'game': '',
                    'started_at': '',
                    'ended_at': '',
                    'image_tag': ''
                },
                'embeds': {
                    'titles': {
                        'on': '',
                        'off': ''
                    },
                    'images': {}
                }
            }
            write_file(self.file_path, default)
            self.reload_data(default)
        else:
            default = self.load_data()
            self.reload_data(default)
    
    # ============================= Stream Info Update =============================
    def update_stream_info(self, data: dict) -> None:
        """
        Update the stream_info dictionary with new data and save to file.
        """
        for tag, item in data.items():
            self.stream_info[tag] = item
        self.save_status()
    
    # ============================= Embed Data Retrieval =============================
    def get_embed_data(self, image_tag: str) -> tuple[str, str]:
        """
        Retrieve the embed title and image URL for the current stream status and image tag.
        """
        data: dict = self.load_data()
        return (
            data['embeds']['titles'].get(self.stream_info['status'].lower(), ''), 
            data['embeds']['images'].get(image_tag, '')
        )
    
    # ============================= Image Tag Extraction =============================
    @staticmethod
    def get_image_tag(title: str) -> str:
        """
        Extract the image tag from the stream title, or return 'default' if not found.
        """
        split_title: list = title.split('|')
        return split_title[1].strip() if len(split_title) > 1 else 'default'
    
    # ============================= Embed Message Creation =============================
    def create_embed_message(self, embed_title: str, image_url: str) -> discord.Embed:
        """
        Create a Discord embed message with the current stream information.
        """
        description: str = (
            "**Titolo**\n{title}"
            "\n\n**Gioco**\n{game}"
            "\n\n**Iniziata il**\n{started_at}"
        ).format(
            title=self.stream_info['title'], 
            game=self.stream_info['game'], 
            started_at=self.stream_info['started_at']
        )
        # If the stream is offline, add the end time to the description
        if self.stream_info['status'] == 'OFF' and self.stream_info['ended_at'] != '':
            description += '\n**Finita il**\n{ended_at}'.format(ended_at=self.stream_info['ended_at'])
        return create_embed(
            title=embed_title,
            description=description,
            color=self.color,
            image=image_url
        )

    # ============================= Embed Message Update/Send Helper =============================
    async def _update_or_edit_message(self, channel, embed_title, embed_image_url, view, message_id=None):
        """
        Send a new embed message or edit an existing one in the specified Discord channel.
        If message_id is provided, the message is edited; otherwise, a new message is sent.
        """
        if channel is None:
            await self._log_and_notify_error('Canale non trovato', 'TWITCH - CHECK STATUS')
            return None
        if message_id:
            message = channel.get_partial_message(int(message_id))
            await message.edit(
                embed=self.create_embed_message(embed_title, embed_image_url),
                view=view
            )
            return message
        else:
            message = await channel.send(
                embed=self.create_embed_message(embed_title, embed_image_url),
                view=view
            )
            return message

    # ============================= Error Logging and Notification =============================
    async def _log_and_notify_error(self, error_message: str, context: str):
        """
        Log an error and notify the communication channel if available.
        """
        await self.log.error(error_message, context)
        communication_channel = self.bot.get_channel(self.config.communication_channel)
        if communication_channel:
            await communication_channel.send(self.log.error_message(command=context, message=error_message))

    # ============================= Stream Change Detection =============================
    def check_changes(self, data: Stream) -> dict:
        """
        Check for changes in the stream's title or game and return a dict of updates.
        """
        updated_data: dict = {}
        if data.title != self.stream_info['title']:
            updated_data['title'] = data.title
            updated_data['image_tag'] = self.get_image_tag(data.title)
        if data.game_name != self.stream_info['game']:
            updated_data['game'] = data.game_name
        return updated_data

    # ============================= Live Status Check and Discord Update =============================
    async def check_live_status(self) -> None:
        """
        Check the Twitch live status and update the Discord message accordingly.
        Handles going live, updating stream info, and going offline.
        """
        async def get_stream(app: Twitch, streamer_name: str) -> Stream:
            async for stream in app.get_streams(user_login=[streamer_name]):
                return stream
            return {}
        # Get the communication channel for error notifications
        communication_channel = self.bot.get_channel(self.config.communication_channel)
        try:
            # Get the channel where the live message is sent
            channel = self.bot.get_channel(self.channel_id)
            if channel is None:
                await self._log_and_notify_error('Canale non trovato', 'TWITCH - CHECK STATUS')
                return
            # Fetch current stream info from Twitch
            stream: Stream = await get_stream(self.app, self.streamer_name)
            if stream != {}:
                if self.stream_info['status'] == 'OFF':
                    try:
                        # Stream just went live: update info and send message
                        self.update_stream_info(
                            {
                                'status': 'ON',
                                'id': stream.id,
                                'title': stream.title,
                                'game': stream.game_name,
                                'started_at': format_datetime_extended(stream.started_at.isoformat())
                            }
                        )
                        image_tag: str = self.get_image_tag(self.stream_info['title'])
                        embed_title, embed_image_url = self.get_embed_data(image_tag)
                        message = await self._update_or_edit_message(
                            channel, embed_title, embed_image_url, StreamButtonView(self.url)
                        )
                        self.update_stream_info(
                            {
                                'message_id': str(message.id),
                                'image_tag': image_tag
                            }
                        )
                        await self.log.event('Nuovo messaggio live iniziata e dati aggiornati in stream_info', 'twitch')
                    except Exception as e:
                        error_message: str = f'Errore durante la fase di invio del messaggio di inizio di una nuova live.\n{e}'
                        await self._log_and_notify_error(error_message, 'TWITCH - CHECK STATUS - START')
                elif self.stream_info['status'] == 'ON':
                    try:
                        # Stream is live and info may have changed: update if needed
                        changes: dict = self.check_changes(stream)
                        if changes != {}:
                            self.update_stream_info(changes)
                            image_tag: str = self.get_image_tag(self.stream_info['title'])
                            embed_title, embed_image_url = self.get_embed_data(image_tag)
                            await self._update_or_edit_message(
                                channel, embed_title, embed_image_url, StreamButtonView(self.url), self.stream_info['message_id']
                            )
                        await self.log.event('Messaggio live aggiornato con le nuove informazioni e dati aggiornati in stream_info', 'twitch')
                    except Exception as e:
                        error_message: str = f'Errore durante la fase di aggiornamento del messaggio.\n{e}'
                        await self._log_and_notify_error(error_message, 'TWITCH - CHECK STATUS - UPDATE')
            else:
                if self.stream_info['status'] == 'ON':
                    try:
                        # Stream just ended: update info and edit message
                        self.stream_info['status'] = 'OFF'
                        self.stream_info['ended_at'] = format_datetime_now_extended()
                        image_tag: str = self.get_image_tag(self.stream_info['title'])
                        embed_title, embed_image_url = self.get_embed_data(image_tag)
                        await self._update_or_edit_message(
                            channel, embed_title, embed_image_url, StreamButtonView(self.url, 'Seguimi sul mio canale'), self.stream_info['message_id']
                        )
                        self.set_default_stream_info()
                        await self.log.event('Messaggio aggiornato con live terminata e dati riportati a default in stream_info', 'twitch')
                    except Exception as e:
                        error_message: str = f'Errore durante il reset dei dati a fine live.\n{e}'
                        await self._log_and_notify_error(error_message, 'TWITCH - CHECK STATUS - RESET')
        except Exception as e:
            error_message: str = f'Errore durante il controllo dell\'inizio di una nuova live.\n{e}'
            await self._log_and_notify_error(error_message, 'TWITCH - CHECK STATUS')