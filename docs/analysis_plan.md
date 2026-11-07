# Analysis plan
1. Generate synthetic data and run validation.
2. Profile row counts, nulls, key uniqueness, date ranges and category distributions.
3. Load CSVs into MySQL and run KPI queries.
4. Build the Power BI star schema and add DAX measures.
5. Compare departments and months; investigate outliers before recommendations.

Questions: Which departments have highest encounter volume? How do admissions and discharges change over time? Which departments have longer stays? Does discharge turnaround vary? State date ranges and KPI denominators. Distinguish correlation from causation. This demo is not clinical decision support. Use only synthetic or authorized de-identified data.
