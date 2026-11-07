# Power BI model
Tables: FactEncounters (one row per encounter), DimPatient, DimDepartment, and a continuous DimDate marked as the Date table. Create one-to-many, single-direction dimension-to-fact relationships. Relate DimDate actively to admission date; use inactive relationships for alternate date roles.

Pages: (1) Executive overview: encounters, admissions, discharges, ALOS. (2) Patient flow: monthly admission/discharge trend and admission type. (3) Department performance: volume, ALOS, readmission flag rate. (4) Operations: discharge turnaround and capacity trend.

Occupancy requires daily census or bed-day allocation; do not divide encounter count by licensed beds. The generated readmission flag is illustrative, not a validated patient-level 30-day outcome.
