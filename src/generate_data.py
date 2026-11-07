"""Generate reproducible synthetic hospital operations data.

All records are fictional. No real patient information is used.
Run: python src/generate_data.py
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
RNG = np.random.default_rng(42)

departments = pd.DataFrame([
    (1, "Emergency", 35), (2, "Cardiology", 48), (3, "Orthopedics", 42),
    (4, "General Medicine", 60), (5, "Neurology", 30), (6, "Pediatrics", 28)
], columns=["department_id", "department_name", "licensed_beds"])
departments.to_csv(DATA / "departments.csv", index=False)

n_patients, n_encounters = 1800, 6500
patients = pd.DataFrame({
    "patient_id": np.arange(1, n_patients + 1),
    "age": RNG.integers(1, 91, n_patients),
    "gender": RNG.choice(["Female", "Male", "Other/Unknown"], n_patients, p=[.49,.49,.02]),
    "payer_category": RNG.choice(["Government", "Private", "Self-pay"], n_patients, p=[.42,.43,.15])
})
patients.to_csv(DATA / "patients.csv", index=False)

patient_ids = RNG.integers(1, n_patients + 1, n_encounters)
dept_ids = RNG.choice(departments.department_id, n_encounters)
start = pd.Timestamp("2024-01-01")
admit = start + pd.to_timedelta(RNG.integers(0, 730, n_encounters), unit="D")
stay = np.clip(RNG.gamma(shape=2.2, scale=2.0, size=n_encounters), .15, 24)
discharge = admit + pd.to_timedelta(stay, unit="D")
order_delay = RNG.uniform(.1, 5.0, n_encounters)
order_time = discharge - pd.to_timedelta(order_delay, unit="h")
encounters = pd.DataFrame({
    "encounter_id": np.arange(100001, 100001 + n_encounters),
    "patient_id": patient_ids,
    "department_id": dept_ids,
    "admission_datetime": admit,
    "discharge_datetime": discharge,
    "discharge_order_datetime": order_time,
    "admission_type": RNG.choice(["Emergency", "Elective", "Transfer"], n_encounters, p=[.58,.32,.10]),
    "discharge_disposition": RNG.choice(["Home", "Transfer", "Rehab", "Other"], n_encounters, p=[.78,.09,.08,.05]),
    "readmission_flag_30d": RNG.choice([0,1], n_encounters, p=[.91,.09])
})
encounters.to_csv(DATA / "encounters.csv", index=False)
print(f"Generated {len(patients):,} patients and {len(encounters):,} encounters in {DATA}")
