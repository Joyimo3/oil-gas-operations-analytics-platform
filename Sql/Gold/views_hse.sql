CREATE VIEW vw_hse_risk_by_field AS
SELECT 
    field,
    team,
    total_incidents,
    total_critical,
    total_high,
    total_near_misses,
    total_days_lost,
    avg_days_lost,
    ROUND(total_critical * 100.0 / total_incidents, 2) as critical_rate_pct,
    ROUND(total_near_misses * 100.0 / total_incidents, 2) as near_miss_rate_pct
FROM gold_hse_kpis
ORDER BY total_critical DESC;


CREATE VIEW vw_hse_incident_types AS
SELECT 
    incident_type,
    COUNT(*) as total_incidents,
    SUM(CASE WHEN severity = 'Critical' THEN 1 ELSE 0 END) as total_critical,
    SUM(days_lost) as total_days_lost,
    ROUND(AVG(days_lost), 2) as avg_days_lost,
    SUM(CASE WHEN near_miss = 'Yes' THEN 1 ELSE 0 END) as total_near_misses
FROM silver_hse
GROUP BY incident_type
ORDER BY total_incidents DESC;

CREATE VIEW vw_hse_department_risk AS
SELECT 
    department,
    COUNT(*) as total_incidents,
    SUM(CASE WHEN severity = 'Critical' THEN 1 ELSE 0 END) as total_critical,
    SUM(days_lost) as total_days_lost,
    ROUND(AVG(days_lost), 2) as avg_days_lost
FROM silver_hse
GROUP BY department
ORDER BY total_incidents DESC;