"""Hospital operations dashboard for exploring fictional encounter data.

Run locally with: streamlit run app.py
The sample data is generated from the project's documented data generator.
"""
from pathlib import Path
import subprocess
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"

st.set_page_config(page_title="Hospital Operations | Analytics", page_icon="🏥", layout="wide")

@st.cache_data
def load_data():
    required = [DATA_DIR / "departments.csv", DATA_DIR / "patients.csv", DATA_DIR / "encounters.csv"]
    if not all(path.exists() for path in required):
        subprocess.run([sys.executable, str(ROOT / "src" / "generate_data.py")], check=True)
    departments = pd.read_csv(required[0])
    patients = pd.read_csv(required[1])
    encounters = pd.read_csv(required[2], parse_dates=["admission_datetime", "discharge_datetime", "discharge_order_datetime"])
    return departments, patients, encounters

departments, patients, encounters = load_data()
data = encounters.merge(departments, on="department_id").merge(patients[["patient_id", "age", "gender", "payer_category"]], on="patient_id")
data["length_of_stay_days"] = (data["discharge_datetime"] - data["admission_datetime"]).dt.total_seconds() / 86400
data["month"] = data["admission_datetime"].dt.to_period("M").astype(str)
data["discharge_delay_hours"] = (data["discharge_datetime"] - data["discharge_order_datetime"]).dt.total_seconds() / 3600

st.title("Hospital Operations Dashboard")
st.caption("A practical view of patient flow, department activity and discharge performance · Fictional portfolio dataset")

with st.sidebar:
    st.header("Report filters")
    min_date, max_date = data["admission_datetime"].min().date(), data["admission_datetime"].max().date()
    date_range = st.date_input("Admission date", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    department_options = sorted(data["department_name"].unique())
    selected_departments = st.multiselect("Department", department_options, default=department_options)
    admission_options = sorted(data["admission_type"].dropna().unique())
    selected_types = st.multiselect("Admission type", admission_options, default=admission_options)
    payer_options = sorted(data["payer_category"].dropna().unique())
    selected_payers = st.multiselect("Payer category", payer_options, default=payer_options)

filtered = data.copy()
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1]) + pd.Timedelta(days=1)
    filtered = filtered[filtered["admission_datetime"].between(start_date, end_date, inclusive="left")]
filtered = filtered[
    filtered["department_name"].isin(selected_departments)
    & filtered["admission_type"].isin(selected_types)
    & filtered["payer_category"].isin(selected_payers)
]

if filtered.empty:
    st.warning("No encounters match these filters. Try widening the date range or selecting more categories.")
    st.stop()

encounter_count = len(filtered)
unique_patients = filtered["patient_id"].nunique()
average_stay = filtered["length_of_stay_days"].mean()
readmission_rate = filtered["readmission_flag_30d"].mean() * 100
discharge_delay = filtered["discharge_delay_hours"].mean()

kpis = st.columns(5)
kpis[0].metric("Encounters", f"{encounter_count:,}")
kpis[1].metric("Unique patients", f"{unique_patients:,}")
kpis[2].metric("Average stay", f"{average_stay:.1f} days")
kpis[3].metric("30-day readmission flag", f"{readmission_rate:.1f}%")
kpis[4].metric("Order-to-discharge", f"{discharge_delay:.1f} hrs")

left, right = st.columns(2)
with left:
    department_summary = filtered.groupby("department_name", as_index=False).agg(encounters=("encounter_id", "count"), average_stay=("length_of_stay_days", "mean")).sort_values("encounters", ascending=True)
    fig = px.bar(department_summary, x="encounters", y="department_name", orientation="h", color="average_stay", color_continuous_scale="Blues", title="Encounter volume by department", labels={"encounters": "Encounters", "department_name": "", "average_stay": "Avg. stay (days)"})
    st.plotly_chart(fig, use_container_width=True)
with right:
    monthly = filtered.groupby("month", as_index=False).agg(encounters=("encounter_id", "count")).sort_values("month")
    fig = px.line(monthly, x="month", y="encounters", markers=True, title="Monthly admission trend", labels={"month": "Admission month", "encounters": "Encounters"})
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    disposition = filtered["discharge_disposition"].value_counts().rename_axis("disposition").reset_index(name="encounters")
    fig = px.pie(disposition, names="disposition", values="encounters", hole=0.55, title="Discharge disposition mix")
    st.plotly_chart(fig, use_container_width=True)
with right:
    stay_by_department = filtered.groupby("department_name", as_index=False)["length_of_stay_days"].median().sort_values("length_of_stay_days", ascending=False)
    fig = px.bar(stay_by_department, x="department_name", y="length_of_stay_days", title="Median length of stay", labels={"department_name": "Department", "length_of_stay_days": "Median days"})
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Encounter detail")
display_columns = ["encounter_id", "patient_id", "department_name", "admission_datetime", "admission_type", "length_of_stay_days", "discharge_disposition", "readmission_flag_30d"]
st.dataframe(filtered[display_columns].sort_values("admission_datetime", ascending=False), use_container_width=True, hide_index=True)
st.download_button("Download filtered encounters", filtered[display_columns].to_csv(index=False).encode("utf-8"), "hospital_encounters_filtered.csv", "text/csv")

with st.expander("Data notes and interpretation"):
    st.write("All records are fictional and generated for portfolio demonstration. The 30-day readmission field is randomly simulated; it is not a clinically validated outcome or a measure of care quality. The dashboard is an operational analytics example, not a clinical decision tool.")
