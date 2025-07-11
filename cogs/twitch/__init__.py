
# ----------------------------- Imported Libraries -----------------------------
import discord
from discord.ext import tasks
from discord.ext import commands
from os import getenv, path
from twitchAPI.twitch import Twitch
from twitchAPI.object.api import Stream
import asyncio
# ----------------------------- Custom Libraries -----------------------------
from logger import Logger
from utils.config import read_file, write_file
from utils.printing import create_embed, format_datetime_now_extended, format_datetime_extended
from .stream_button_view import StreamButtonView

class TwitchApp():
    def __init__(self, bot: commands.Bot, log: Logger):
        # Twitch data
        app_id = getenv('TWITCH_CLIENT_ID')
        app_secret = getenv('TWITCH_CLIENT_SECRET')
        # Variables
        self.log = log
        self.bot = bot
        
        self.file_path: str = path.join(getenv('MAIN_PATH'), getenv('DATA_PATH'), getenv('TWITCH_FILE_NAME'))
        self.stream_info: dict = {}
        self.streamer_name: str = ''
        self.url: str = getenv('TWITCH_URL')
        self.channel_id: int = int(getenv('LIVE_CHANNEL_ID'))
        self.color: discord.Color = f'0x{getenv('TWITCH_COLOR')}'
        
        # Create Twitch app
        self.app: Twitch = Twitch(app_id, app_secret)
        # Setup the App
        self.setup()
    
    # ============================= Authenticate App =============================
    async def _authenticate(self) -> None:
        await self.app.authenticate_app([])
    
    # ============================= Load Data =============================
    def load_data(self) -> dict:
        if path.exists(self.file_path):
            return read_file(self.file_path)
        else:
            return {}
    
    # ============================= Reload Data =============================
    def reload_data(self, data) -> None:
        self.streamer_name = data['config'].get('streamer_name', '')
        self.url = f'{self.url}{self.streamer_name}' if self.streamer_name != '' else self.url
        self.stream_info = data.get('stream', {})
    
    # ============================= Save Status =============================
    def save_status(self) -> None:
        data: dict = self.load_data()
        data['stream'] = self.stream_info
        write_file(self.file_path, data)
    
    # ============================= Add Image =============================
    def add_image(self, new_image: dict) -> None:
        data: dict = self.load_data()
        data['embeds']['images'][new_image['tag']] = new_image['url']
        write_file(self.file_path, data)
    
    # ============================= Change Title =============================
    def change_title(self, new_title: dict) -> None:
        data: dict = self.load_data()
        data['embeds']['titles'][new_title['tag']] = new_title['title']
        write_file(self.file_path, data)

    # ============================= Change Streamer Name =============================
    def change_streamer_name(self, new_name: str) -> None:
        data: dict = self.load_data()
        data['config']['streamer_name'] = new_name
        self.streamer_name = new_name
        write_file(self.file_path, data)

    # ============================= Set Default Stream Info =============================
    def set_default_stream_info(self) -> None:
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
    
    # ============================= Setup =============================
    def setup(self) -> None:
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
    
    # ============================= Update Stream Info =============================
    def update_stream_info(self, data: dict) -> None:
        for tag, item in data.items():
            self.stream_info[tag] = item
        
        self.save_status()
    
    # ============================= Get Embed Data =============================
    def get_embed_data(self, image_tag: str) -> tuple[str, str]:
        data: dict = self.load_data()
        # Return status and image_url
        return (
            data['embeds']['titles'].get(self.stream_info['status'].lower(), ''), 
            data['embeds']['images'].get(image_tag, '')
        )
    
    # ============================= Get Image Tag =============================
    @staticmethod
    def get_image_tag(title: str) -> str:
        # Get image_tag
        split_title: list = title.split('/')
        return split_title[1].strip() if len(split_title) > 1 else 'default'
    
    # ============================= Create Embed Message =============================
    def create_embed_message(self, embed_title: str, image_url: str) -> discord.Embed:
        # Create the description
        description: str = (
            "**Titolo**\n{title}"
            "\n\n**Gioco**\n{game}"
            "\n\n**Iniziata il**\n{started_at}"
        ).format(
            title=self.stream_info['title'], 
            game=self.stream_info['game'], 
            started_at=self.stream_info['started_at']
        )
        # Add the end of stream to description if stream is ended
        if self.stream_info['status'] == 'OFF' and self.stream_info['ended_at'] != '':
            description.join('\n**Finita il**\n{ended_at}'.format(self.stream_info['ended_at']))
        # Return the created embed
        return create_embed(
            title=embed_title,
            description=description,
            color=self.color,
            image=image_url
            )

    # ============================= Check Changes =============================
    def check_changes(self, data: Stream) -> dict:
        updated_data: dict = {}
        if data.title != self.stream_info['title']:
            updated_data['title'] = data.title
            updated_data['image_tag'] = self.get_image_tag(data.title)
        if data.game_name != self.stream_info['game']:
            updated_data['game'] = data.game_name

        return updated_data

    # ============================= Check Live Status =============================
    async def check_live_status(self) -> None:
        async def get_stream(app: Twitch, streamer_name: str) -> Stream:
            async for stream in app.get_streams(user_login=[streamer_name]):
                return stream
            return {}
        
        # Load communication channel
        communication_channel = self.bot.get_channel(int(getenv('BOT_COMMUNICATION_CHANNEL_ID')))
        
        try:
            # Get the channel where the message will be sent
            channel = self.bot.get_channel(self.channel_id)
            
            # Get stream
            stream: Stream = await get_stream(self.app, self.streamer_name)
            if stream != {}:
                if self.stream_info['status'] == 'OFF':
                    try:
                        # Initially update stream_info data
                        self.update_stream_info(
                            {
                                'status': 'ON',
                                'id': stream.id,
                                'title': stream.title,
                                'game': stream.game_name,
                                'started_at': format_datetime_extended(stream.started_at.isoformat())
                            }
                        )
                        # Get image_tag
                        image_tag: str = self.get_image_tag(self.stream_info['title'])
                        # Get embed data
                        embed_title, embed_image_url = self.get_embed_data(image_tag)
                        # Send the message
                        message: discord.Message = await channel.send(
                            embed=self.create_embed_message(embed_title, embed_image_url),
                            view=StreamButtonView(self.url)
                            )
                        
                        # Update stream_info data
                        self.update_stream_info(
                            {
                                'message_id': str(message.id),
                                'image_tag': image_tag
                            }
                        )
                    except Exception as e:
                        # EXCEPTION
                        error_message: str = f'Errore durante la fase di invio del messaggio di inizio di una nuova live.\n{e}'
                        await self.log.error(error_message, 'TWITCH - CHECK STATUS - START')
                        await communication_channel.send(self.log.error_message(command = 'TWITCH - CHECK STATUS - START', message = error_message))
                    
                elif self.stream_info['status'] == 'ON':
                    try:
                        # Check if something changed in the stream info
                        changes: dict = self.check_changes(stream)
                        if changes != {}:
                            # Update stream_info data
                            self.update_stream_info(changes)
                            # Get image_tag
                            image_tag: str = self.get_image_tag(self.stream_info['title'])
                            # Get embed data
                            embed_title, embed_image_url = self.get_embed_data(image_tag)
                            # Get the message
                            message: discord.Message = channel.get_partial_message(int(self.stream_info['message_id']))
                            # Update message
                            await message.edit(
                                embed=self.create_embed_message(embed_title, embed_image_url),
                                view=StreamButtonView(self.url)
                            )
                    except Exception as e:
                        # EXCEPTION
                        error_message: str = f'Errore durante la fase di aggiornamento del messaggio.\n{e}'
                        await self.log.error(error_message, 'TWITCH - CHECK STATUS - UPDATE')
                        await communication_channel.send(self.log.error_message(command = 'TWITCH - CHECK STATUS - UPDATE', message = error_message))
            else:
                if self.stream_info['status'] == 'ON':
                    try:
                        # Change status in OFF and set ended_at
                        self.stream_info['status'] == 'OFF'
                        self.stream_info['ended_at'] == format_datetime_now_extended()
                        # Get image_tag
                        image_tag: str = self.get_image_tag(self.stream_info['title'])
                        # Get embed data
                        embed_title, embed_image_url = self.get_embed_data(image_tag)
                        # Get the message
                        message: discord.Message = channel.get_partial_message(int(self.stream_info['message_id']))
                        # Update message
                        await message.edit(
                            embed=self.create_embed_message(embed_title, embed_image_url),
                            view=StreamButtonView(self.url, 'Seguimi sul mio canale')
                        )
                        # Set stream_info to default
                        self.set_default_stream_info()
                    except Exception as e:
                        # EXCEPTION
                        error_message: str = f'Errore durante il reset dei dati a fine live.\n{e}'
                        await self.log.error(error_message, 'TWITCH - CHECK STATUS - RESET')
                        await communication_channel.send(self.log.error_message(command = 'TWITCH - CHECK STATUS - RESET', message = error_message))
        except Exception as e:
            # EXCEPTION
            error_message: str = f'Errore durante il controllo dell\'inizio di una nuova live.\n{e}'
            await self.log.error(error_message, 'TWITCH - CHECK STATUS')
            await communication_channel.send(self.log.error_message(command = 'TWITCH - CHECK STATUS', message = error_message))