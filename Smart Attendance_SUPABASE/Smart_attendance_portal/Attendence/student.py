
from .logger          import get_logger
from .supabase_client import SupabaseClient
from .utils           import get_today_date, get_now_timestamp, sanitize_input, validate_name, validate_roll_number

log = get_logger(__name__)

def mark_attendance(class_name, roll_number, name, entered_code) -> dict:
    db    = SupabaseClient()
    today = get_today_date()

    # 1. Sanitise & validate
    roll_number  = sanitize_input(roll_number)
    name         = name.strip().title()
    entered_code = sanitize_input(entered_code)
    if not validate_roll_number(roll_number):
        return {"success": False, "message": "Invalid roll number format."}
    if not validate_name(name):
        return {"success": False, "message": "Invalid name — letters only."}

    # 2. Class settings & open check
    settings = db.get_class_settings(class_name)
    if not settings:
        return {"success": False, "message": f"Class not found."}
    if not settings.get("attendance_open", False):
        return {"success": False, "message": "Attendance is closed for this class."}

    # 3. Daily limit check
    limit = settings.get("daily_limit", 60)
    count = db.count_today_attendance(class_name, today)
    if count >= limit:
        return {"success": False, "message": "Daily attendance limit reached."}

    # 4. Code verification
    if entered_code != sanitize_input(settings.get("attendance_code", "")):
        return {"success": False, "message": "Incorrect attendance code."}

    # 5. Roll-number/name locking
    existing = db.get_roll_entry(class_name, roll_number)
    if existing:
        if name.lower() != existing["name"].lower():
            return {"success": False, "message": f"Roll {roll_number} belongs to '{existing[chr(34)+chr(110)+chr(97)+chr(109)+chr(101)+chr(34)]}.' Name mismatch."}
    else:
        db.lock_roll_number(class_name, roll_number, name)

    # 6. Duplicate check
    if db.check_already_marked(class_name, roll_number, today):
        return {"success": False, "message": "Attendance already marked today."}

    # 7. Insert
    ok = db.insert_attendance({"class_name": class_name, "roll_number": roll_number,
                               "name": name, "date": today, "submitted_at": get_now_timestamp()})
    if ok:
        log.info(f"Marked: {roll_number}|{name}|{class_name}|{today}")
        return {"success": True, "message": "Attendance marked successfully!"}
    return {"success": False, "message": "Database error. Try again."}
