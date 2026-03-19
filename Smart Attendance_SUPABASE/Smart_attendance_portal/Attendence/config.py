
import os

# Supabase credentials (from env vars set in Step 1)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

# Supabase table names
TABLE_ATTENDANCE         = "attendance"
TABLE_ROLL_MAP           = "roll_map"
TABLE_CLASSROOM_SETTINGS = "classroom_settings"

# Application constants
DEFAULT_TIMEZONE     = "Asia/Kolkata"   # IST
MAX_ATTENDANCE_PER_DAY = 60
LOG_DIR              = "logs"
LOG_FILE             = "attendance.log"
CSV_EXPORT_DIR       = "exports"
