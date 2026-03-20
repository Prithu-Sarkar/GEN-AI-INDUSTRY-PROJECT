
from .clients import get_supabase_client
from .config  import TABLE_ATTENDANCE, TABLE_ROLL_MAP, TABLE_CLASSROOM_SETTINGS
from .logger  import get_logger

log = get_logger(__name__)

class SupabaseClient:
    def __init__(self):
        self.db = get_supabase_client()

    # ── Classroom settings ────────────────────────────────────
    def get_all_classes(self):
        try:
            return self.db.table(TABLE_CLASSROOM_SETTINGS).select("*").execute().data
        except Exception as e:
            log.exception(e); return []

    def get_class_settings(self, class_name):
        try:
            return self.db.table(TABLE_CLASSROOM_SETTINGS).select("*").eq("class_name", class_name).single().execute().data
        except Exception:
            return None

    def upsert_class_settings(self, payload):
        try:
            self.db.table(TABLE_CLASSROOM_SETTINGS).upsert(payload).execute()
            return True
        except Exception as e:
            log.exception(e); return False

    # ── Roll-number map ───────────────────────────────────────
    def get_roll_entry(self, class_name, roll_number):
        try:
            return self.db.table(TABLE_ROLL_MAP).select("*").eq("class_name", class_name).eq("roll_number", roll_number).single().execute().data
        except Exception:
            return None

    def lock_roll_number(self, class_name, roll_number, name):
        try:
            self.db.table(TABLE_ROLL_MAP).insert({"class_name": class_name, "roll_number": roll_number, "name": name}).execute()
            return True
        except Exception as e:
            log.exception(e); return False

    # ── Attendance records ────────────────────────────────────
    def check_already_marked(self, class_name, roll_number, date_str):
        try:
            res = self.db.table(TABLE_ATTENDANCE).select("id").eq("class_name", class_name).eq("roll_number", roll_number).eq("date", date_str).execute()
            return len(res.data) > 0
        except Exception as e:
            log.exception(e); return False

    def count_today_attendance(self, class_name, date_str):
        try:
            res = self.db.table(TABLE_ATTENDANCE).select("id", count="exact").eq("class_name", class_name).eq("date", date_str).execute()
            return res.count or 0
        except Exception as e:
            log.exception(e); return 0

    def insert_attendance(self, payload):
        try:
            self.db.table(TABLE_ATTENDANCE).insert(payload).execute()
            log.info(f"Inserted: {payload}"); return True
        except Exception as e:
            log.exception(e); return False

    def fetch_attendance_range(self, class_name, start_date, end_date):
        try:
            return self.db.table(TABLE_ATTENDANCE).select("*").eq("class_name", class_name).gte("date", start_date).lte("date", end_date).execute().data
        except Exception as e:
            log.exception(e); return []

    def delete_attendance_record(self, record_id):
        try:
            self.db.table(TABLE_ATTENDANCE).delete().eq("id", record_id).execute()
            return True
        except Exception as e:
            log.exception(e); return False
