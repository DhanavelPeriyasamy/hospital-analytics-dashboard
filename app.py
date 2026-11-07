"""Hospital operations dashboard | Power BI companion web view."""
from pathlib import Path
import subprocess
import sys
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
st.set_page_config(page_title="Hospital Analytics | Dhanavel Periyasamy", page_icon="✚", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {font-family:Inter,sans-serif;}
.stApp {background:#F5F7F8;color:#182B36;}
.block-container {max-width:1500px;padding-top:2rem;padding-bottom:3rem;}
[data-testid="stMetric"] {background:#FFFFFF;border:1px solid #E3E9EC;border-radius:12px;padding:17px 18px;box-shadow:0 2px 8px rgba(19,45,58,.035);}
[data-testid="stMetricLabel"] {color:#647681;font-size:13px;}
[data-testid="stMetricValue"] {color:#173B4A;font-weight:750;}
h1,h2,h3 {color:#173B4A;letter-spacing:-.025em;}
div[data-testid="stMultiSelect"] label, div[data-testid="stDateInput"] label {font-weight:650;color:#526671;}
div[data-testid="stPlotlyChart"] {background:#FFFFFF;border:1px solid #E7ECEF;border-radius:12px;padding:8px;}
hr {border-color:#E4EAED;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    files = [DATA / "departments.csv", DATA / "patients.csv", DATA / "encounters.csv"]
    if not all(p.exists() for p in files):
        subprocess.run([sys.executable, str(ROOT / "src" / "generate_data.py")], check=True)
    departments = pd.read_csv(files[0])
    patients = pd.read_csv(files[1])
    encounters = pd.read_csv(files[2], parse_dates=["admission_datetime","discharge_datetime","discharge_order_datetime"])
    df = encounters.merge(departments, on="department_id", how="left")
    df = df.merge(patients[["patient_id","age","gender","payer_category"]], on="patient_id", how="left")
    df["stay_days"] = (df.discharge_datetime-df.admission_datetime).dt.total_seconds()/86400
    df["discharge_delay_hours"] = (df.discharge_datetime-df.discharge_order_datetime).dt.total_seconds()/3600
    df["month"] = df.admission_datetime.dt.to_period("M").astype(str)
    return df

df = load_data()
st.markdown("""
<div style="background:#123847;border-radius:16px;padding:27px 30px;color:white;margin-bottom:20px">
<div style="font-size:11px;letter-spacing:2px;font-weight:700;color:#8ED3C8">HEALTHCARE OPERATIONS • ANALYTICS</div>
<div style="font-size:31px;font-weight:800;letter-spacing:-1px;color:#FFFFFF;margin-top:5px">Hospital Performance Dashboard</div>
<div style="font-size:14px;color:#D5E5E8;margin-top:7px">A management view of patient demand, department workload and discharge efficiency</div>
</div>
""", unsafe_allow_html=True)

st.markdown("**REPORT FILTERS**")
date_min, date_max = df.admission_datetime.min().date(), df.admission_datetime.max().date()
f1,f2,f3,f4 = st.columns([1.35,1.2,1.2,1.2])
date_range = f1.date_input("Admission date", (date_min,date_max), min_value=date_min, max_value=date_max)
departments = sorted(df.department_name.dropna().unique())
dept_filter = f2.multiselect("Department", departments, default=departments, placeholder="All departments")
pathways = sorted(df.admission_type.dropna().unique())
path_filter = f3.multiselect("Admission type", pathways, default=pathways, placeholder="All types")
payers = sorted(df.payer_category.dropna().unique())
payer_filter = f4.multiselect("Payer category", payers, default=payers, placeholder="All payers")
if isinstance(date_range,(tuple,list)) and len(date_range)==2:
    start,end = pd.Timestamp(date_range[0]),pd.Timestamp(date_range[1])+pd.Timedelta(days=1)
else:
    start,end = pd.Timestamp(date_min),pd.Timestamp(date_max)+pd.Timedelta(days=1)
view = df[df.admission_datetime.between(start,end,inclusive="left") & df.department_name.isin(dept_filter) & df.admission_type.isin(path_filter) & df.payer_category.isin(payer_filter)].copy()
st.divider()
if view.empty:
    st.info("No records match the current filters. Widen the date range or select more categories.")
    st.stop()

encounters = view.encounter_id.nunique()
patients = view.patient_id.nunique()
avg_los = view.stay_days.mean()
avg_delay = view.discharge_delay_hours.mean()
flag_rate = view.readmission_flag_30d.mean()*100
st.markdown("### Executive overview")
k = st.columns(5)
k[0].metric("Total encounters",f"{encounters:,}")
k[1].metric("Patients served",f"{patients:,}")
k[2].metric("Average stay",f"{avg_los:.1f} days")
k[3].metric("Discharge delay",f"{avg_delay:.1f} hrs")
k[4].metric("Readmission flag",f"{flag_rate:.1f}%")
st.caption("The readmission flag is randomly simulated in this dataset; it is not calculated from subsequent encounters.")
st.markdown("### Demand and patient flow")
left,right = st.columns([1.55,1])
with left:
    trend = view.groupby("month",as_index=False).agg(Encounters=("encounter_id","nunique"))
    fig = px.line(trend,x="month",y="Encounters",markers=True,title="Monthly encounter volume")
    fig.update_traces(line_color="#168779",line_width=3,marker_size=6,fill="tozeroy",fillcolor="rgba(22,135,121,.10)")
    fig.update_layout(template="plotly_white",height=330,margin=dict(l=18,r=18,t=55,b=15),xaxis_title="",yaxis_title="Encounters",font_color="#344B56")
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
with right:
    pathway = view.admission_type.value_counts().rename_axis("Admission type").reset_index(name="Encounters")
    fig = px.bar(pathway,x="Admission type",y="Encounters",title="Admission mix",text_auto=True,color_discrete_sequence=["#315B6A"])
    fig.update_layout(template="plotly_white",height=330,margin=dict(l=18,r=18,t=55,b=15),xaxis_title="",yaxis_title="Encounters",font_color="#344B56")
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
st.markdown("### Department performance")
left,right = st.columns([1.2,1])
with left:
    perf = view.groupby("department_name",as_index=False).agg(Encounters=("encounter_id","nunique"),Median_stay=("stay_days","median"),Average_stay=("stay_days","mean")).sort_values("Encounters")
    fig = px.bar(perf,x="Encounters",y="department_name",orientation="h",title="Workload by department",text="Encounters",color_discrete_sequence=["#168779"])
    fig.update_layout(template="plotly_white",height=350,margin=dict(l=18,r=18,t=55,b=15),xaxis_title="Encounters",yaxis_title="",font_color="#344B56")
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
with right:
    disp = view.discharge_disposition.value_counts().rename_axis("Discharge disposition").reset_index(name="Encounters")
    fig = px.pie(disp,names="Discharge disposition",values="Encounters",hole=.58,title="Discharge outcomes",color_discrete_sequence=["#168779","#315B6A","#9CB9C1","#D9A85B"])
    fig.update_layout(template="plotly_white",height=350,margin=dict(l=18,r=18,t=55,b=15),font_color="#344B56",legend_title="")
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
st.markdown("### Operational detail")
detail = perf.rename(columns={"department_name":"Department","Encounters":"Encounters","Median_stay":"Median stay (days)","Average_stay":"Average stay (days)"})
st.dataframe(detail,use_container_width=True,hide_index=True)
with st.expander("View filtered encounter records"):
    cols=["encounter_id","patient_id","department_name","admission_datetime","admission_type","stay_days","discharge_disposition","discharge_delay_hours"]
    st.dataframe(view[cols].sort_values("admission_datetime",ascending=False),use_container_width=True,hide_index=True)
    st.download_button("Download filtered records",view[cols].to_csv(index=False).encode("utf-8"),"hospital_filtered_encounters.csv","text/csv")
with st.expander("Metric definitions and data limitations"):
    st.write("All records are synthetic. Average stay is the time between admission and discharge. Discharge delay is discharge timestamp minus discharge-order timestamp. The 30-day readmission flag is randomly assigned and must not be presented as a validated readmission rate. No daily census or staffed-bed snapshots are provided, so bed occupancy cannot be calculated.")
st.caption("Hospital Analytics Dashboard • Power BI portfolio project with an interactive Streamlit companion • Synthetic demonstration data")
