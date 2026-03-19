
import io, sys, os
from datetime import date, timedelta
sys.path.insert(0, os.path.dirname(__file__))

import matplotlib.pyplot as plt
import streamlit as st
from Attendence.admin           import close_attendance, get_today_summary, open_attendance, delete_record
from Attendence.analytics       import build_attendance_matrix, daily_counts
from Attendence.supabase_client import SupabaseClient
from Attendence.logger          import get_logger

log = get_logger(__name__)

st.set_page_config(page_title="Attendance Portal — Admin", page_icon="🛠", layout="wide")
st.title("🛠 Admin Panel — Smart Attendance Portal")
st.divider()

tab1, tab2, tab3 = st.tabs(["📋 Manage Classes", "📊 Analytics", "🗑 Delete Records"])

# ── TAB 1: Manage Classes ─────────────────────────────────────────
with tab1:
    st.subheader("Open / Close Attendance")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Open Attendance")
        cn  = st.text_input("Class Name", key="oc", placeholder="CS-A")
        cd  = st.text_input("Attendance Code", key="ocd")
        lim = st.number_input("Daily Limit", min_value=1, max_value=500, value=60, key="ol")
        if st.button("Open", use_container_width=True):
            r = open_attendance(cn, cd, lim)
            st.success(r["message"]) if r["success"] else st.error(r["message"])

    with col2:
        st.markdown("#### Close Attendance")
        cc = st.text_input("Class Name", key="cc", placeholder="CS-A")
        if st.button("Close", use_container_width=True):
            r = close_attendance(cc)
            st.success(r["message"]) if r["success"] else st.error(r["message"])

    st.divider()
    st.subheader("Today Summary")
    db = SupabaseClient()
    all_classes = db.get_all_classes()
    if all_classes:
        for cls in all_classes:
            name = cls["class_name"]
            s = get_today_summary(name)
            status = "🟢 Open" if s["is_open"] else "🔴 Closed"
            st.metric(
                label=f"{name} — {status}",
                value=f"{s['count']} / {s['limit']} students"
            )
    else:
        st.info("No classes found.")

# ── TAB 2: Analytics ──────────────────────────────────────────────
with tab2:
    st.subheader("Attendance Analytics")
    ca, cb, cc2 = st.columns(3)
    with ca: acls = st.text_input("Class", key="acls")
    with cb: s_dt = st.date_input("Start", value=date.today()-timedelta(days=7), key="sdt")
    with cc2: e_dt = st.date_input("End",  value=date.today(), key="edt")

    if st.button("Generate Report", use_container_width=True):
        s_str, e_str = s_dt.strftime("%Y-%m-%d"), e_dt.strftime("%Y-%m-%d")
        with st.spinner("Fetching..."):
            matrix = build_attendance_matrix(acls, s_str, e_str)
        if matrix.empty:
            st.warning("No records found.")
        else:
            st.dataframe(matrix, use_container_width=True)
            counts = daily_counts(acls, s_str, e_str)
            if not counts.empty:
                fig, ax = plt.subplots(figsize=(10, 4))
                ax.bar(counts.index, counts.values, color="steelblue")
                ax.set(xlabel="Date", ylabel="Present", title=f"Daily Attendance — {acls}")
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()
                st.pyplot(fig)
            buf = io.StringIO()
            matrix.to_csv(buf)
            st.download_button("⬇️ Download CSV", buf.getvalue(),
                               file_name=f"{acls}_{s_str}_to_{e_str}.csv",
                               mime="text/csv", use_container_width=True)

# ── TAB 3: Delete Records ─────────────────────────────────────────
with tab3:
    st.subheader("Delete Attendance Record")
    st.warning("This action is permanent.")
    rid = st.number_input("Record ID", min_value=1, step=1, key="rid")
    if st.button("Delete", use_container_width=True):
        r = delete_record(int(rid))
        st.success(r["message"]) if r["success"] else st.error(r["message"])
