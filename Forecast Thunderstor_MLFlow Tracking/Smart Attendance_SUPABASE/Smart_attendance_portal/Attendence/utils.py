
from datetime import datetime
import pytz
from .config import DEFAULT_TIMEZONE
from .logger import get_logger

log = get_logger(__name__)

def get_today_date() -> str:
    """Return today in YYYY-MM-DD using the configured timezone."""
    tz    = pytz.timezone(DEFAULT_TIMEZONE)
    today = datetime.now(tz).strftime("%Y-%m-%d")
    log.debug(f"Today: {today}")
    return today

def get_now_timestamp() -> str:
    """Return current datetime as ISO-8601 string with timezone."""
    return datetime.now(pytz.timezone(DEFAULT_TIMEZONE)).isoformat()

def sanitize_input(value: str) -> str:
    """Strip whitespace and uppercase — normalises codes and roll numbers."""
    return value.strip().upper()

def validate_roll_number(roll: str) -> bool:
    """True if roll is non-empty and alphanumeric (dashes/underscores allowed)."""
    roll = roll.strip()
    return bool(roll) and roll.replace("-","").replace("_","").isalnum()

def validate_name(name: str) -> bool:
    """True if name is non-empty and contains only letters and spaces."""
    name = name.strip()
    return bool(name) and all(c.isalpha() or c.isspace() for c in name)
