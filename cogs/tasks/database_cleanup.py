import discord
from discord.ext import tasks, commands
import datetime
from logger import Logger
import pytz
from config_manager import ConfigManager

ROME_TZ = pytz.timezone('Europe/Rome')

class DatabaseCleanup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = Logger()
        self.config = ConfigManager()
        self.database_cleanup.start()

    @tasks.loop(hours=168)  # 168 ore = 1 settimana
    async def database_cleanup(self):
        """
        Weekly database cleanup task that runs every Monday at 9:00 (Europe/Rome).
        Deletes records older than the retention period from all database tables.
        Messages with to_maintain = 'True' are preserved.
        """
        try:
            # Load retention days from config
            retention_days = self.config.load_retention_days()
            # Calculate cutoff date
            now_rome = datetime.datetime.now(ROME_TZ)
            cutoff_date = now_rome - datetime.timedelta(days=retention_days)
            cutoff_utc = cutoff_date.astimezone(datetime.timezone.utc)
            cutoff_time = cutoff_utc.isoformat(sep=' ', timespec='seconds')
            current_utc = now_rome.astimezone(datetime.timezone.utc)
            current_time = current_utc.isoformat(sep=' ', timespec='seconds')
            # Delete records older than the retention period
            deleted_messages = self.logger.db.delete_messages_by_range(cutoff_time, current_time)
            deleted_events = self.logger.db.delete_events_by_range(cutoff_time, current_time)
            deleted_commands = self.logger.db.delete_commands_by_range(cutoff_time, current_time)
            # Create cleanup message
            cleanup_message = (
                f"Pulizia database completata - {now_rome.strftime('%d/%m/%Y %H:%M')}\n"
                f"Messaggi eliminati: {deleted_messages}\n"
                f"Eventi eliminati: {deleted_events}\n"
                f"Comandi eliminati: {deleted_commands}\n"
                f"Data di cutoff: {cutoff_date.strftime('%d/%m/%Y')} (Retention: {retention_days} giorni)"
            )
            # Insert cleanup message into database
            self.logger.db.insert_event(
                timestamp=current_time,
                record_type="database_cleanup",
                message=cleanup_message
            )
            # Get report channel from config
            report_channel_id = getattr(self.bot.config, 'report_channel', None)
            if report_channel_id:
                channel = self.bot.get_channel(report_channel_id)
                if channel:
                    # Create embed
                    embed = discord.Embed(
                        title="🗑️ Pulizia Database Completata",
                        description=cleanup_message,
                        color=0x00FF00,
                        timestamp=now_rome
                    )
                    # Send embed to report channel
                    await channel.send(embed=embed)
        except Exception as e:
            communication_channel = self.bot.get_channel(self.config.communication_channel)
            error_message = f"Errore durante la pulizia del database: {str(e)}"
            await communication_channel.send(self.logger.error_message(command='DATABASE-CLEANUP', message=error_message))
            await self.logger.error(self.logger.error_message(command='DATABASE-CLEANUP', message=error_message), 'TASK')

    @database_cleanup.before_loop
    async def before_database_cleanup(self):
        """
        Calcola quanto manca al prossimo lunedì alle 9:00 (Europe/Rome) e attende.
        """
        now_rome = datetime.datetime.now(ROME_TZ)
        today = now_rome.date()
        this_monday = today - datetime.timedelta(days=now_rome.weekday())
        next_monday = this_monday + datetime.timedelta(days=7)
        next_run = datetime.datetime.combine(next_monday, datetime.time(9, 0, 0), tzinfo=ROME_TZ)
        seconds_until_next = (next_run - now_rome).total_seconds()
        if seconds_until_next < 0:
            seconds_until_next += 7 * 24 * 3600  # fallback di sicurezza
        await discord.utils.sleep_until(next_run)

async def setup(bot):
    await bot.add_cog(DatabaseCleanup(bot)) 