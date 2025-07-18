import discord
from discord.ext import tasks, commands
import datetime
from logger import Logger
import pytz

ROME_TZ = pytz.timezone('Europe/Rome')

class DatabaseCleanup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = Logger()
        self.database_cleanup.start()

    @tasks.loop(hours=24)  # 24 hours = 1 day
    async def database_cleanup(self):
        """
        Daily database cleanup task that runs at midnight.
        
        Deletes records older than 3 months from all database tables.
        Messages with to_maintain = 'True' are preserved.
        """
        try:
            # Calculate the cutoff date (3 months ago)
            now_rome = datetime.datetime.now(ROME_TZ)
            cutoff_date = now_rome - datetime.timedelta(days=90)  # 3 months = ~90 days
            cutoff_utc = cutoff_date.astimezone(datetime.timezone.utc)
            cutoff_time = cutoff_utc.isoformat(sep=' ', timespec='seconds')
            
            # Current time for end of range
            current_utc = now_rome.astimezone(datetime.timezone.utc)
            current_time = current_utc.isoformat(sep=' ', timespec='seconds')
            
            # Delete old records from all tables
            deleted_messages = self.logger.db.delete_messages_by_range(cutoff_time, current_time)
            deleted_events = self.logger.db.delete_events_by_range(cutoff_time, current_time)
            deleted_commands = self.logger.db.delete_commands_by_range(cutoff_time, current_time)
            
            # Log the cleanup results
            cleanup_message = (
                f"Pulizia database completata - {now_rome.strftime('%d/%m/%Y %H:%M')}\n"
                f"Messaggi eliminati: {deleted_messages}\n"
                f"Eventi eliminati: {deleted_events}\n"
                f"Comandi eliminati: {deleted_commands}\n"
                f"Data di cutoff: {cutoff_date.strftime('%d/%m/%Y')}"
            )
            
            # Log the cleanup operation
            self.logger.db.insert_event(
                timestamp=current_time,
                record_type="database_cleanup",
                message=cleanup_message
            )
            
            # Send notification to communication channel if available
            comm_channel_id = getattr(self.bot.config, 'communication_channel', None)
            if comm_channel_id:
                channel = self.bot.get_channel(comm_channel_id)
                if channel:
                    embed = discord.Embed(
                        title="🗑️ Pulizia Database Completata",
                        description=cleanup_message,
                        color=0x00FF00,  # Green color
                        timestamp=now_rome
                    )
                    await channel.send(embed=embed)
                    
        except Exception as e:
            # Log any errors during cleanup
            error_message = f"Errore durante la pulizia del database: {str(e)}"
            self.logger.db.insert_error(
                timestamp=datetime.datetime.now(ROME_TZ).astimezone(datetime.timezone.utc).isoformat(sep=' ', timespec='seconds'),
                record_type="database_cleanup_error",
                message=error_message
            )

    @database_cleanup.before_loop
    async def before_database_cleanup(self):
        """
        Calculate time until next midnight (Rome timezone) and wait.
        """
        now_rome = datetime.datetime.now(ROME_TZ)
        tomorrow = now_rome.date() + datetime.timedelta(days=1)
        next_midnight = datetime.datetime.combine(tomorrow, datetime.time(0, 0, 0), tzinfo=ROME_TZ)
        
        # Calculate seconds until next midnight
        seconds_until_midnight = (next_midnight - now_rome).total_seconds()
        
        # Wait until next midnight
        await discord.utils.sleep_until(next_midnight)

async def setup(bot):
    await bot.add_cog(DatabaseCleanup(bot)) 