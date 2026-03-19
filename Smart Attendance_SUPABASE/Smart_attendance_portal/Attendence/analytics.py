
import os
import pandas as pd
from .config          import CSV_EXPORT_DIR
from .logger          import get_logger
from .supabase_client import SupabaseClient

log = get_logger(__name__)

def build_attendance_matrix(class_name, start_date, end_date) -> pd.DataFrame:
    """
    Pivot table: rows=students, columns=dates, values=1(present)/0(absent).
    Adds a Total column at the end.
    """
    db      = SupabaseClient()
    records = db.fetch_attendance_range(class_name, start_date, end_date)
    if not records:
        log.warning(f"No records for {class_name} [{start_date} to {end_date}]")
        return pd.DataFrame()
    df = pd.DataFrame(records)
    df["present"] = 1
    matrix = df.pivot_table(index="name", columns="date", values="present",
                             aggfunc="max", fill_value=0)
    matrix["Total"] = matrix.sum(axis=1)
    log.info(f"Matrix: {matrix.shape[0]} students x {matrix.shape[1]-1} days")
    return matrix

def export_matrix_to_csv(matrix, class_name, start_date, end_date) -> str:
    """Save matrix to CSV and return the file path."""
    os.makedirs(CSV_EXPORT_DIR, exist_ok=True)
    path = os.path.join(CSV_EXPORT_DIR, f"{class_name}_{start_date}_to_{end_date}.csv")
    matrix.to_csv(path)
    log.info(f"Exported: {path}")
    return path

def daily_counts(class_name, start_date, end_date) -> pd.Series:
    """Count of students present per day — used for bar/line charts."""
    db      = SupabaseClient()
    records = db.fetch_attendance_range(class_name, start_date, end_date)
    if not records:
        return pd.Series(dtype=int)
    df = pd.DataFrame(records)
    return df.groupby("date")["roll_number"].count().sort_index()
