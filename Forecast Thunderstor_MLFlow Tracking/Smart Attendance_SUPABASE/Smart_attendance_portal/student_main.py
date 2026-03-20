
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from Attendence.student         import mark_attendance
from Attendence.supabase_client import SupabaseClient
from Attendence.logger          import get_logger

log = get_logger(__name__)

st.set_page_config(page_title="Attendance Portal — Student", page_icon="🎓", layout="centered")
st.title("🎓 Smart Attendance Portal")
st.subheader("Mark Your Attendance")
st.divider()

@st.cache_data(ttl=60)
def load_open_classes():
    """Load classes that are currently open — refresh every 60 s."""
    db = SupabaseClient()
    return [c["class_name"] for c in db.get_all_classes() if c.get("attendance_open")]

open_classes = load_open_classes()
if not open_classes:
    st.warning("No classes are currently open for attendance.")
    st.stop()

with st.form("attendance_form", clear_on_submit=True):
    class_name   = st.selectbox("Select Class", open_classes)
    roll_number  = st.text_input("Roll Number", placeholder="e.g. CS2101")
    name         = st.text_input("Full Name",   placeholder="e.g. John Doe")
    entered_code = st.text_input("Attendance Code", type="password")
    submitted    = st.form_submit_button("Mark Attendance", use_container_width=True)

if submitted:
    with st.spinner("Submitting..."):
        result = mark_attendance(class_name, roll_number, name, entered_code)
    if result["success"]:
        st.success(result["message"])
        st.balloons()
    else:
        st.error(result["message"])
