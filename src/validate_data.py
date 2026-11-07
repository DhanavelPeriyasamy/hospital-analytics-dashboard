"""Run basic data-quality checks on generated hospital CSVs."""
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data"
patients = pd.read_csv(DATA / "patients.csv")
departments = pd.read_csv(DATA / "departments.csv")
encounters = pd.read_csv(DATA / "encounters.csv", parse_dates=["admission_datetime","discharge_datetime","discharge_order_datetime"])

checks = {
    "patient_id unique": patients.patient_id.is_unique,
    "department_id unique": departments.department_id.is_unique,
    "encounter_id unique": encounters.encounter_id.is_unique,
    "patient foreign keys valid": encounters.patient_id.isin(patients.patient_id).all(),
    "department foreign keys valid": encounters.department_id.isin(departments.department_id).all(),
    "admission before discharge": (encounters.admission_datetime <= encounters.discharge_datetime).all(),
    "discharge order not after discharge": (encounters.discharge_order_datetime <= encounters.discharge_datetime).all(),
    "no missing encounter fields": not encounters.isna().any().any(),
}
for label, passed in checks.items():
    print(f"{'PASS' if passed else 'FAIL'} | {label}")
if not all(checks.values()):
    raise SystemExit("Data-quality checks failed.")
print("All checks passed.")
