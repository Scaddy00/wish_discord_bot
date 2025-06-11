# ----------------------------- Standard library -----------------------------
from datetime import datetime
from os import getenv

# ============================= Datetime format =============================
def format_datetime_now() -> str:
    str_format: str = str(getenv('DATETIME_FORMAT'))
    return datetime.now().strftime(str_format)