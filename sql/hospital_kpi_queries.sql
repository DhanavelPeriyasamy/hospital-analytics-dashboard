-- MySQL 8+ | Load departments, patients and encounters CSVs first.
SELECT COUNT(DISTINCT encounter_id) encounters,SUM(admission_type='Emergency') emergency_admissions,
ROUND(AVG(TIMESTAMPDIFF(HOUR,admission_datetime,discharge_datetime))/24,2) avg_los_days,
ROUND(AVG(readmission_flag_30d)*100,2) readmission_flag_rate_pct FROM encounters;
SELECT DATE_FORMAT(admission_datetime,'%Y-%m') month,COUNT(*) admissions,
SUM(discharge_datetime IS NOT NULL) discharges FROM encounters GROUP BY month ORDER BY month;
SELECT d.department_name,COUNT(*) encounters,
ROUND(AVG(TIMESTAMPDIFF(HOUR,e.admission_datetime,e.discharge_datetime))/24,2) avg_los_days,
ROUND(AVG(e.readmission_flag_30d)*100,2) readmission_flag_pct
FROM encounters e JOIN departments d USING(department_id)
GROUP BY d.department_id,d.department_name ORDER BY encounters DESC;
SELECT d.department_name,ROUND(AVG(TIMESTAMPDIFF(MINUTE,e.discharge_order_datetime,e.discharge_datetime))/60,2) avg_turnaround_hours
FROM encounters e JOIN departments d USING(department_id) GROUP BY d.department_name;
WITH x AS (SELECT patient_id,encounter_id,admission_datetime,
LAG(discharge_datetime) OVER(PARTITION BY patient_id ORDER BY admission_datetime) prior_discharge FROM encounters)
SELECT *,TIMESTAMPDIFF(DAY,prior_discharge,admission_datetime) days_since_prior_discharge
FROM x WHERE prior_discharge IS NOT NULL;
