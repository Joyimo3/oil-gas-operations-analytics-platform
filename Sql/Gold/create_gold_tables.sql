-- ============================================================
-- GOLD LAYER - SLA COMPLIANCE BY FIELD AND TEAM
-- Answers: Which field has worst SLA compliance?
-- Which team breaches SLA the most?
-- ============================================================

CREATE TABLE IF NOT EXISTS gold_sla_compliance AS
SELECT 
    field,
    team,
    severity,
    COUNT(*) as total_incidents,
    SUM(CASE WHEN sla_status = 'BREACHED' THEN 1 ELSE 0 END) as total_breaches,
    SUM(CASE WHEN sla_status = 'COMPLIANT' THEN 1 ELSE 0 END) as total_compliant,
    ROUND(SUM(CASE WHEN sla_status = 'COMPLIANT' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as compliance_rate_pct,
    ROUND(SUM(CASE WHEN sla_status = 'BREACHED' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as breach_rate_pct,
    ROUND(AVG(resolution_hours), 2) as avg_resolution_hours
FROM silver_incidents
GROUP BY field, team, severity;

-- ============================================================
-- GOLD LAYER - PRODUCTION KPIs BY FIELD AND TEAM
-- Answers: Which field produces the most oil and gas?  
-- Which team has the highest average wellhead pressure?
-- ============================================================

CREATE TABLE IF NOT EXISTS gold_production_kpis AS
SELECT 
    field,
    team,
    COUNT(*) as total_readings,
    ROUND(SUM(oil_volume_bbl), 2) as total_oil_volume_bbl,
    ROUND(SUM(gas_volume_mcf), 2) as total_gas_volume_mcf,
    ROUND(SUM(water_volume_bbl), 2) AS total_water_volume_bbl,
    ROUND(SUM(deferred_production_bbls), 2) AS total_deferred_production_bbls,
    ROUND(AVG(wellhead_pressure), 2) as avg_wellhead_pressure
FROM silver_production
GROUP BY field, team;

-- ============================================================
-- GOLD LAYER - EQUIPMENT MAINTENANCE BY FIELD AND TEAM 
-- Answers: Which field has the most maintenance activities?
-- Which team performs the most maintenance activities? 
-- ============================================================
CREATE TABLE IF NOT EXISTS gold_maintenance_kpis AS
SELECT 
    field,
    team,
    maintenance_type,
    COUNT(*) as total_work_orders,
    ROUND(SUM(maintenance_cost), 2) as total_maintenance_cost,
    ROUND(AVG(maintenance_cost), 2) as avg_maintenance_cost,
    ROUND(AVG(maintenance_duration_hours), 2) as avg_duration_hours
FROM silver_maintenance
GROUP BY field, team;

-- ============================================================
-- GOLD LAYER - SAFETY INCIDENTS BY FIELD AND TEAM
-- Answers: Which field has the most safety incidents?
-- Which team has the most safety incidents?
-- ============================================================
CREATE TABLE gold_hse_kpis (
    field TEXT,
    team TEXT,
    total_incidents INTEGER,
    total_days_lost INTEGER,
    avg_days_lost REAL,
    total_critical INTEGER,
    total_near_misses INTEGER,
    near_miss_rate_pct REAL
);

INSERT INTO gold_hse_kpis (field, team, total_incidents, total_days_lost, avg_days_lost, total_critical, total_near_misses, near_miss_rate_pct)
SELECT 
    field,
    team,
    COUNT(*),
    SUM(days_lost),
    ROUND(AVG(days_lost), 2),
    SUM(CASE WHEN severity = 'Critical' THEN 1 ELSE 0 END),
    SUM(CASE WHEN near_miss = 'Yes' THEN 1 ELSE 0 END),
    ROUND(SUM(CASE WHEN near_miss = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2)
FROM silver_hse
GROUP BY field, team;

CREATE TABLE IF NOT EXISTS gold_hse_by_severity (
    field TEXT,
    team TEXT,
    severity TEXT,
    total_incidents INTEGER
);

INSERT INTO gold_hse_by_severity (field, team, severity, total_incidents)
SELECT 
    field,
    team,
    severity,
    COUNT(*)
FROM silver_hse
GROUP BY field, team, severity;

CREATE TABLE IF NOT EXISTS gold_hse_by_type (
    field TEXT,
    team TEXT,
    incident_type TEXT,
    total_incidents INTEGER,
    total_days_lost INTEGER
);
INSERT INTO gold_hse_by_type (field, team, incident_type, total_incidents, total_days_lost)
SELECT 
    field,
    team,
    incident_type,
    COUNT(*),
    SUM(days_lost)
FROM silver_hse
GROUP BY field, team, incident_type;

CREATE TABLE IF NOT EXISTS gold_hse_by_department (
    field TEXT,
    team TEXT,
    department TEXT,
    total_incidents INTEGER,
    total_days_lost INTEGER
);

INSERT INTO gold_hse_by_department (field, team, department, total_incidents, total_days_lost)
SELECT 
    field,
    team,
    department,
    COUNT(*),
    SUM(days_lost)
FROM silver_hse
GROUP BY field, team, department;

-- ============================================================
-- GOLD LAYER - DATA QUALITY METRICS
-- Answers: What is the overall data quality for each domain?       
-- ============================================================

CREATE TABLE IF NOT EXISTS gold_data_quality (
    domain TEXT,
    total_records INTEGER,
    total_clean INTEGER,
    total_errors INTEGER,
    total_alerts INTEGER,
    error_rate_pct REAL,
    alert_rate_pct REAL
);

INSERT INTO gold_data_quality VALUES
    ('Incidents', 1000, 846, 154, 512, 15.4, 51.2),
    ('Production', 1000, 847, 153, 0, 15.3, 0.0),
    ('Maintenance', 1000, 868, 132, 0, 13.2, 0.0),
    ('HSE', 1000, 848, 152, 0, 15.2, 0.0);
