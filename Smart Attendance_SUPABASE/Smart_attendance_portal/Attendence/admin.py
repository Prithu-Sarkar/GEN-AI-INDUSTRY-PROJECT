
from .logger          import get_logger
from .supabase_client import SupabaseClient
from .utils           import get_today_date, sanitize_input

log = get_logger(__name__)

def open_attendance(class_name, code, daily_limit) -> dict:
    """Open attendance for a class — sets code, limit, and open=True."""
    db   = SupabaseClient()
    code = sanitize_input(code)
    if not code:
        return {"success": False, "message": "Code cannot be empty."}
    if daily_limit < 1:
        return {"success": False, "message": "Limit must be >= 1."}
    ok = db.upsert_class_settings({"class_name": class_name, "attendance_code": code,
                                    "daily_limit": daily_limit, "attendance_open": True})
    if ok:
        log.info(f"OPENED {class_name} code={code} limit={daily_limit}")
        return {"success": True, "message": f"Attendance opened for {class_name}."}
    return {"success": False, "message": "Failed to open attendance."}

def close_attendance(class_name) -> dict:
    """Close attendance — students can no longer submit."""
    db       = SupabaseClient()
    settings = db.get_class_settings(class_name)
    if not settings:
        return {"success": False, "message": f"Class not found."}
    settings["attendance_open"] = False
    ok = db.upsert_class_settings(settings)
    if ok:
        log.info(f"CLOSED {class_name}")
        return {"success": True, "message": f"Attendance closed for {class_name}."}
    return {"success": False, "message": "Failed to close attendance."}

def get_today_summary(class_name) -> dict:
    """Return dict with today count, limit, and open status."""
    db       = SupabaseClient()
    today    = get_today_date()
    settings = db.get_class_settings(class_name) or {}
    return {"class_name": class_name, "date": today,
            "count": db.count_today_attendance(class_name, today),
            "limit": settings.get("daily_limit", 0),
            "is_open": settings.get("attendance_open", False)}

def delete_record(record_id) -> dict:
    """Delete a specific attendance record by primary key."""
    db = SupabaseClient()
    if db.delete_attendance_record(record_id):
        log.info(f"Deleted record id={record_id}")
        return {"success": True, "message": f"Record {record_id} deleted."}
    return {"success": False, "message": "Delete failed."}
