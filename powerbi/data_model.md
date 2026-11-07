# Power BI data model

## Tables and relationships
- **FactEncounters**: one row per encounter; keys: patient_id, department_id; dates: admission, discharge, discharge order.
- **DimPatient**: one row per synthetic patient.
- **DimDepartment**: one row per department, including licensed bed capacity.
- **DimDate**: continuous calendar table. Mark it as the Date table.

Create one-to-many, single-direction relationships from dimensions to FactEncounters. Use an active relationship from DimDate to admission date; create inactive relationships for discharge date and activate them in measures with USERELATIONSHIP.

## Suggested report pages
- Executive overview: cards and monthly trend.
- Department performance: matrix with encounter volume, ALOS and flag rate.
- Flow analysis: admissions by month and admission type.
- Operations: discharge turnaround and occupancy trend.

## Important caveat
The synthetic generator assigns an illustrative encounter-level readmission flag. It is not a validated patient-level 30-day readmission calculation. For production analysis, derive readmission by sequencing actual encounters and applying a documented eligibility rule.
