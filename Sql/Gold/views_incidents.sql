CREATE VIEW vw_equipment_failures AS
SELECT 
    equipment_id,
    field,
    team,
    category,
    COUNT(*) as total_failures,
    ROUND(AVG(resolution_hours), 2) as avg_resolution_hours,
    ROUND(AVG(downtime_hours), 2) as avg_downtime_hours,
    SUM(CASE WHEN sla_status = 'BREACHED' THEN 1 ELSE 0 END) as total_breaches
FROM silver_incidents
GROUP BY equipment_id, field, team, category
ORDER BY total_failures DESC;

CREATE VIEW vw_downtime_by_field AS
SELECT 
    field,
    team,
    COUNT(*) as total_incidents,
    ROUND(AVG(downtime_hours), 2) as avg_downtime_hours,
    ROUND(SUM(downtime_hours), 2) as total_downtime_hours,
    ROUND(AVG(resolution_hours), 2) as avg_resolution_hours
FROM silver_incidents
GROUP BY field, team
ORDER BY total_downtime_hours DESC;


CREATE VIEW vw_incident_type_analysis AS
SELECT 
    incident_type,
    COUNT(*) as total_incidents,
    ROUND(AVG(resolution_hours), 2) as avg_resolution_hours,
    ROUND(AVG(downtime_hours), 2) as avg_downtime_hours,
    SUM(CASE WHEN sla_status = 'BREACHED' THEN 1 ELSE 0 END) as total_breaches
FROM silver_incidents
GROUP BY incident_type
ORDER BY total_incidents DESC;

CREATE VIEW vw_team_resolution_time AS
SELECT 
    team,
    COUNT(*) as total_incidents,
    ROUND(AVG(resolution_hours), 2) as avg_resolution_hours,
    ROUND(AVG(downtime_hours), 2) as avg_downtime_hours,
    SUM(CASE WHEN sla_status = 'BREACHED' THEN 1 ELSE 0 END) as total_breaches
FROM silver_incidents
GROUP BY team
ORDER BY avg_resolution_hours DESC;