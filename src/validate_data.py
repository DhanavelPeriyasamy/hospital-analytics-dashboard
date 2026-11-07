"""Validate generated hospital CSV files."""
from pathlib import Path
import pandas as pd
D=Path(__file__).resolve().parents[1]/"data"
p=pd.read_csv(D/"patients.csv"); d=pd.read_csv(D/"departments.csv")
e=pd.read_csv(D/"encounters.csv",parse_dates=["admission_datetime","discharge_datetime","discharge_order_datetime"])
checks={"patient IDs unique":p.patient_id.is_unique,"department IDs unique":d.department_id.is_unique,"encounter IDs unique":e.encounter_id.is_unique,"patient foreign keys valid":e.patient_id.isin(p.patient_id).all(),"department foreign keys valid":e.department_id.isin(d.department_id).all(),"admission <= discharge":(e.admission_datetime<=e.discharge_datetime).all(),"order <= discharge":(e.discharge_order_datetime<=e.discharge_datetime).all(),"no missing encounter values":not e.isna().any().any()}
for k,v in checks.items(): print(("PASS" if v else "FAIL")+" | "+k)
if not all(checks.values()): raise SystemExit("Validation failed")
