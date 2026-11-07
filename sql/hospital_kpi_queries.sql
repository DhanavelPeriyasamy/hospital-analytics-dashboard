-- Hospital Analytics: MySQL 8+ analytical queries
-- Load departments.csv, patients.csv, encounters.csv into matching tables first.

-- 1. Executive KPI snapshot
SELECT COUNT(DISTINCT encounter_id) AS encounters,
       SUM(admission_type = 'Emergency') AS emergency_admissions,
       ROUND(AVG(TIMESTAMPDIFF(HOUR, admission_datetime, discharge_datetime))/24, 2) AS avg_length_of_stay_days,
       ROUND(AVG(readmission_flag_30d) * 100, 2) AS readmission_flag_rate_pct
FROM encounters;

-- 2. Monthly patient flow
SELECT DATE_FORMAT(admission_datetime, '%Y-%m') AS admission_month,
       COUNT(*) AS admissions,
       SUM(discharge_datetime IS NOT NULL) AS discharges
FROM encounters
GROUP BY DATE_FORMAT(admission_datetime, '%Y-%m')
ORDER BY admission_month;

-- 3. Department scorecard
SELECT d.department_name, COUNT(*) AS encounters,
       ROUND(AVG(TIMESTAMPDIFF(HOUR,e.admission_datetime,e.discharge_datetime))/24,2) AS avg_los_days,
       ROUND(AVG(e.readmission_flag_30d)*100,2) AS readmission_flag_pct
FROM encounters e JOIN departments d USING (department_id)
GROUP BY d.department_id, d.department_name
ORDER BY encounters DESC;

-- 4. Discharge turnaround in hours
SELECT d.department_name,
       ROUND(AVG(TIMESTAMPDIFF(MINUTE,e.discharge_order_datetime,e.discharge_datetime))/60,2) AS avg_turnaround_hours
FROM encounters e JOIN departments d USING (department_id)
GROUP BY d.department_name ORDER BY avg_turnaround_hours DESC;

-- 5. Patient-level encounter sequence using a window function
WITH ordered AS (
  SELECT patient_id, encounter_id, admission_datetime,
         LAG(discharge_datetime) OVER (PARTITION BY patient_id ORDER BY admission_datetime) AS prior_discharge
  FROM encounters
)
SELECT *, TIMESTAMPDIFF(DAY, prior_discharge, admission_datetime) AS days_since_prior_discharge
FROM ordered WHERE prior_discharge IS NOT NULL
ORDER BY patient_id, admission_datetime;

-- 6. Monthly department trend
SELECT d.department_name, DATE_FORMAT(e.admission_datetime,'%Y-%m') AS month,
       COUNT(*) AS encounter_count
FROM encounters e JOIN departments d USING(department_id)
GROUP BY d.department_name, month
ORDER BY month, encounter_count DESC;
