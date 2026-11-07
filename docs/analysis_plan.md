# Analysis plan and interpretation guide

## Workflow
1. Generate synthetic data and run the validation script.
2. Profile row counts, missing values, key uniqueness, date ranges, and category distributions.
3. Load the three CSVs into MySQL and execute the KPI queries.
4. Build the Power BI model and measures.
5. Compare departments and months; investigate outliers before making recommendations.

## Questions to answer
- Which departments contribute the largest encounter volume?
- Are admission and discharge patterns changing month over month?
- Which departments have longer average stays?
- Does discharge turnaround vary by department?
- What capacity questions can be explored with licensed beds and encounter dates?

## Reporting discipline
State the date range and denominator beside each KPI. Distinguish correlation from causation. Avoid interpreting the synthetic readmission flag as a clinical quality measure. This project is an analytics demonstration, not a clinical decision-support system.
