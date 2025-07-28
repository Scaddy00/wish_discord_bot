import discord
from discord.ext import tasks, commands
import datetime
from logger import Logger
import pytz
from utils.printing import create_embed

ROME_TZ = pytz.timezone('Europe/Rome')

class WeeklyReport(commands.Cog):
    """
    Weekly report cog that generates and sends weekly Discord activity reports.
    
    Collects data from the database for the past week and creates an embed
    with statistics about member joins, leaves, boosts, and message activity.
    """
    
    def __init__(self, bot):
        """
        Initialize the WeeklyReport cog.
        
        Args:
            bot: Discord bot instance
        """
        self.bot = bot
        self.logger = Logger()
        self.weekly_report.start()

    def convert_italian_timestamp_to_datetime(self, italian_timestamp: str) -> datetime.datetime:
        """
        Convert Italian timestamp format (dd/mm/yyyy hh:mm:ss) to datetime object.
        
        Args:
            italian_timestamp (str): Timestamp in format 'dd/mm/yyyy hh:mm:ss'
            
        Returns:
            datetime.datetime: Datetime object in Rome timezone
        """
        try:
            # Parse Italian timestamp format
            dt = datetime.datetime.strptime(italian_timestamp, '%d/%m/%Y %H:%M:%S')
            # Assume it's in Rome timezone
            dt = dt.replace(tzinfo=ROME_TZ)
            return dt
        except ValueError:
            # Try without seconds if seconds are missing
            try:
                dt = datetime.datetime.strptime(italian_timestamp, '%d/%m/%Y %H:%M')
                dt = dt.replace(tzinfo=ROME_TZ)
                return dt
            except ValueError:
                # If all parsing fails, return None
                return None

    @tasks.loop(hours=168)  # 168 hours = 1 week
    async def weekly_report(self):
        """
        Generate and send weekly Discord activity report.
        
        Collects data from the past week (Monday 9:00 to Monday 8:59:59) and
        creates an embed with statistics about member activity and message counts.
        """
        # Calcola il periodo: da lunedì scorso 9:00 a oggi lunedì 8:59:59
        now_rome = datetime.datetime.now(ROME_TZ)
        today = now_rome.date()
        # Trova il lunedì corrente
        this_monday = today - datetime.timedelta(days=today.weekday())
        last_monday = this_monday - datetime.timedelta(days=7)
        start_dt = datetime.datetime.combine(last_monday, datetime.time(9, 0, 0), tzinfo=ROME_TZ)
        end_dt = datetime.datetime.combine(this_monday, datetime.time(8, 59, 59), tzinfo=ROME_TZ)

        # Get events from DB - convert to Italian timestamp format for comparison
        event_types = ['guild_join', 'remove', 'boost']
        start_time_italian = start_dt.strftime('%d/%m/%Y %H:%M:%S')
        end_time_italian = end_dt.strftime('%d/%m/%Y %H:%M:%S')
        
        events = self.logger.db.get_events(event_types, start_time_italian, end_time_italian)
        join_count = sum(1 for e in events if e[1] == 'guild_join')
        leave_count = sum(1 for e in events if e[1] == 'remove')
        boost_count = sum(1 for e in events if e[1] == 'boost')

        # Get messages from DB - convert to Italian timestamp format for comparison
        messages = self.logger.db.get_messages(start_time_italian, end_time_italian)
        msg_per_channel = {}
        for msg in messages:
            channel_name = msg[2] or 'Sconosciuto'
            msg_per_channel[channel_name] = msg_per_channel.get(channel_name, 0) + 1

        # Formatta le date per il report
        start_str = start_dt.strftime('%d/%m/%Y %H:%M')
        end_str = end_dt.strftime('%d/%m/%Y %H:%M')

        # Build the report in Italian
        embed_title = "Report Settimanale Eventi Discord"
        embed_description = (
            f"Periodo: dal {start_str} al {end_str}\n"
            f"Membri entrati: {join_count}\n"
            f"Membri usciti: {leave_count}\n"
            f"Nuovi server booster: {boost_count}\n"
            f"\nMessaggi per canale:\n"
        )
        fields = []
        if msg_per_channel:
            for ch, count in msg_per_channel.items():
                fields.append({
                    'name': ch,
                    'value': f'{count} messaggi',
                    'inline': False
                })
        else:
            fields.append({
                'name': 'Messaggi',
                'value': 'Nessun messaggio registrato.',
                'inline': False
            })
        # Use bot color if available, else fallback
        color = getattr(self.bot, 'color', '0xA6BBF0')
        # Create the embed
        embed = create_embed(
            title=embed_title,
            description=embed_description,
            color=color,
            fields=fields
        )
        # Get report channel from config
        report_channel_id = getattr(self.bot.config, 'report_channel', None)
        channel = self.bot.get_channel(report_channel_id) if report_channel_id else None
        if channel:
            await channel.send(embed=embed)

    @weekly_report.before_loop
    async def before_weekly_report(self):
        """
        Calculate time until next Monday 9:00 AM (Rome timezone) and wait.
        
        Ensures the weekly report runs at the correct time each week.
        """
        # Calcola quanto manca al prossimo lunedì alle 9:00 ora italiana
        now_rome = datetime.datetime.now(ROME_TZ)
        today = now_rome.date()
        this_monday = today - datetime.timedelta(days=today.weekday())
        next_monday = this_monday + datetime.timedelta(days=7)
        next_run = datetime.datetime.combine(next_monday, datetime.time(9, 0, 0), tzinfo=ROME_TZ)
        seconds_until_next = (next_run - now_rome).total_seconds()
        if seconds_until_next < 0:
            seconds_until_next += 7 * 24 * 3600  # fallback di sicurezza
        await discord.utils.sleep_until(next_run)

async def setup(bot):
    """
    Setup function for the WeeklyReport cog.
    
    Args:
        bot: Discord bot instance to add the cog to
    """
    await bot.add_cog(WeeklyReport(bot)) 