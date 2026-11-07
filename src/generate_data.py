"""Generate fictional hospital operations data."""
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"data"; OUT.mkdir(exist_ok=True)
rng=np.random.default_rng(42)
departments=pd.DataFrame([(1,"Emergency",35),(2,"Cardiology",48),(3,"Orthopedics",42),(4,"General Medicine",60),(5,"Neurology",30),(6,"Pediatrics",28)],columns=["department_id","department_name","licensed_beds"])
patients=pd.DataFrame({"patient_id":range(1,1801),"age":rng.integers(1,91,1800),"gender":rng.choice(["Female","Male","Other/Unknown"],1800),"payer_category":rng.choice(["Government","Private","Self-pay"],1800)})
n=6500; admit=pd.Timestamp("2024-01-01")+pd.to_timedelta(rng.integers(0,730,n),unit="D")
stay=np.clip(rng.gamma(2.2,2,n),.15,24); discharge=admit+pd.to_timedelta(stay,unit="D")
encounters=pd.DataFrame({"encounter_id":range(100001,100001+n),"patient_id":rng.integers(1,1801,n),"department_id":rng.choice(departments.department_id,n),"admission_datetime":admit,"discharge_datetime":discharge,"discharge_order_datetime":discharge-pd.to_timedelta(rng.uniform(.1,5,n),unit="h"),"admission_type":rng.choice(["Emergency","Elective","Transfer"],n,p=[.58,.32,.10]),"discharge_disposition":rng.choice(["Home","Transfer","Rehab","Other"],n,p=[.78,.09,.08,.05]),"readmission_flag_30d":rng.choice([0,1],n,p=[.91,.09])})
for name,df in [("departments",departments),("patients",patients),("encounters",encounters)]: df.to_csv(OUT/f"{name}.csv",index=False)
print(f"Wrote {len(patients)} patients and {len(encounters)} encounters")
