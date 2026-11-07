"""Hospital operations intelligence dashboard.

A clinical-operations inspired interface for exploring fictional encounter data.
Run with: streamlit run app.py
"""
from pathlib import Path
import subprocess
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"

st.set_page_config(page_title="CareFlow | Hospital Intelligence", page_icon="✚", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');
html, body, [class*="css"] {font-family:'DM Sans',sans-serif;}
.stApp {background:#F3F7F8;color:#18313A;}
[data-testid="stSidebar"] {background:#102D38;}
[data-testid="stSidebar"] * {color:#EAF4F5 !important;}
[data-testid="stMetric"] {background:white;border:1px solid #DCE8E9;padding:18px 20px;border-radius:12px;box-shadow:0 3px 12px rgba(16,45,56,.04);}
[data-testid="stMetricLabel"] {color:#607B82;}
[data-testid="stMetricValue"] {color:#123C48;font-family:'Manrope',sans-serif;}
h1,h2,h3 {font-family:'Manrope',sans-serif;color:#123C48;}
.block-container {padding-top:2rem;padding-bottom:3rem;max-width:1450px;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    paths = [DATA_DIR / name for name in ["departments.csv", "patients.csv", "encounters.csv"]]
    if not all(path.exists() for path in paths):
        subprocess.run([sys.executable, str(ROOT / "src" / "generate_data.py")], check=True)
    departments = pd.read_csv(paths[0])
    patients = pd.read_csv(paths[1])
    encounters = pd.read_csv(paths[2], parse_dates=["admission_datetime", "discharge_datetime", "discharge_order_datetime"])
    data = encounters.merge(departments, on="department_id", how="left")
    data = data.merge(patients[["patient_id", "age", "gender", "payer_category"]], on="patient_id", how="left")
    data["stay_days"] = (data["discharge_datetime"] - data["admission_datetime"]).dt.total_seconds() / 86400
    data["discharge_delay_hours"] = (data["discharge_datetime"] - data["discharge_order_datetime"]).dt.total_seconds() / 3600
    data["month"] = data["admission_datetime"].dt.to_period("M").astype(str)
    return departments, data

departments, data = load_data()
st.markdown("<div style='background:#123C48;padding:24px 28px;border-radius:16px;color:white;margin-bottom:20px'><div style='font-size:12px;letter-spacing:2px;color:#83CFC5;font-weight:700'>CARE OPERATIONS • ANALYTICS SUITE</div><div style='font-family:Manrope;font-size:32px;font-weight:800;color:white'>Hospital Performance Centre</div><div style='color:#C6DADC;margin-top:5px'>Patient flow, department activity and discharge operations</div></div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## CAREFLOW")
    st.caption("HOSPITAL INTELLIGENCE")
    st.markdown("---")
    date_min, date_max = data.admission_datetime.min().date(), data.admission_datetime.max().date()
    date_range = st.date_input("Admission period", (date_min, date_max), min_value=date_min, max_value=date_max)
    dept_list = sorted(data.department_name.dropna().unique())
    depts = st.multiselect("Clinical department", dept_list, default=dept_list)
    admission_types = sorted(data.admission_type.dropna().unique())
    types = st.multiselect("Admission pathway", admission_types, default=admission_types)
    payers = sorted(data.payer_category.dropna().unique())
    payer_filter = st.multiselect("Payer group", payers, default=payers)

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1]) + pd.Timedelta(days=1)
else:
    start, end = pd.Timestamp(date_min), pd.Timestamp(date_max) + pd.Timedelta(days=1)
view = data[data.admission_datetime.between(start, end, inclusive="left") & data.department_name.isin(depts) & data.admission_type.isin(types) & data.payer_category.isin(payer_filter)].copy()

if view.empty:
    st.warning("No encounters match the selected filters.")
    st.stop()

encounters = view.encounter_id.nunique()
patients = view.patient_id.nunique()
avg_stay = view.stay_days.mean()
delay = view.discharge_delay_hours.mean()
readmit_flag = view.readmission_flag_30d.mean() * 100

kpi = st.columns(4)
for col, label, value, help_text in [
    (kpi[0], "Total encounters", f"{encounters:,}", "Distinct encounter records"),
    (kpi[1], "Patients served", f"{patients:,}", "Distinct patients in selected period"),
    (kpi[2], "Average length of stay", f"{avg_stay:.1f} days", "Mean admission-to-discharge duration"),
    (kpi[3], "Readmission flag", f"{readmit_flag:.1f}%", "Simulated flag; not a clinical readmission calculation"),
]:
    col.metric(label, value, help=help_text)

st.markdown("### Patient flow overview")
left, right = st.columns([1.55, 1])
with left:
    monthly = view.groupby("month", as_index=False).agg(Admissions=("encounter_id", "nunique"))
    fig = px.area(monthly, x="month", y="Admissions", markers=True, color_discrete_sequence=["#159A91"])
    fig.update_traces(line=dict(width=3), fillcolor="rgba(21,154,145,.16)")
    fig.update_layout(title="Admission volume across the year", paper_bgcolor="white", plot_bgcolor="white", font_color="#23434B", margin=dict(l=10,r=10,t=55,b=10), xaxis_title="", yaxis_title="Encounters")
    st.plotly_chart(fig, use_container_width=True)
with right:
    pathway = view.admission_type.value_counts().rename_axis("Pathway").reset_index(name="Patients")
    fig = px.funnel(pathway, x="Patients", y="Pathway", color_discrete_sequence=["#159A91"])
    fig.update_layout(title="Admission pathway mix", paper_bgcolor="white", plot_bgcolor="white", font_color="#23434B", margin=dict(l=10,r=10,t=55,b=10))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("### Department operations")
left, right = st.columns([1.15, 1])
with left:
    dept_perf = view.groupby("department_name", as_index=False).agg(Encounters=("encounter_id","nunique"), Median_stay=("stay_days","median"), Average_stay=("stay_days","mean"))
    fig = px.bar(dept_perf.sort_values("Encounters"), x="Encounters", y="department_name", orientation="h", color="Median_stay", color_continuous_scale=["#CDEBE6","#087F78"], labels={"department_name":"Department","Median_stay":"Median stay (days)"})
    fig.update_layout(title="Workload by department", paper_bgcolor="white", plot_bgcolor="white", font_color="#23434B", margin=dict(l=10,r=10,t=55,b=10), coloraxis_colorbar_title="Days")
    st.plotly_chart(fig, use_container_width=True)
with right:
    disposition = view.discharge_disposition.value_counts().rename_axis("Disposition").reset_index(name="Encounters")
    fig = px.sunburst(disposition, path=["Disposition"], values="Encounters", color="Encounters", color_continuous_scale=["#D7EFEC","#087F78"])
    fig.update_layout(title="Discharge disposition profile", paper_bgcolor="white", font_color="#23434B", margin=dict(l=10,r=10,t=55,b=10))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("### Discharge efficiency")
left, right = st.columns([1, 1.2])
with left:
    fig = px.box(view, x="admission_type", y="discharge_delay_hours", color="admission_type", color_discrete_sequence=["#087F78","#159A91","#8BCBC2"], points="outliers", labels={"admission_type":"Admission type","discharge_delay_hours":"Hours"})
    fig.update_layout(title="Order-to-discharge time distribution", showlegend=False, paper_bgcolor="white", plot_bgcolor="white", font_color="#23434B", margin=dict(l=10,r=10,t=55,b=10))
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.markdown("#### Department performance snapshot")
    summary = dept_perf.sort_values("Encounters", ascending=False).rename(columns={"department_name":"Department","Encounters":"Encounters","Median_stay":"Median stay (days)","Average_stay":"Average stay (days)"})
    st.dataframe(summary, use_container_width=True, hide_index=True)

with st.expander("Explore encounter records"):
    columns = ["encounter_id","patient_id","department_name","admission_datetime","admission_type","stay_days","discharge_disposition","discharge_delay_hours"]
    st.dataframe(view[columns].sort_values("admission_datetime", ascending=False), use_container_width=True, hide_index=True)
    st.download_button("Export filtered encounters", view[columns].to_csv(index=False).encode("utf-8"), "hospital_encounters.csv", "text/csv")

with st.expander("Metric definitions and data limitations"):
    st.write("The dataset is synthetic. The 30-day readmission flag is randomly assigned, not derived from subsequent encounters. Bed occupancy cannot be calculated reliably because daily census and staffed-bed snapshots are not included. This is an operations portfolio demonstration, not a clinical decision system.")
st.caption("CAREFLOW • Synthetic portfolio data • Built with Python, Streamlit and Plotly")
