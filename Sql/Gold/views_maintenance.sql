CREATE VIEW vw_maintenance_costs AS
SELECT 
    field,
    team,
    total_work_orders,
    total_maintenance_cost,
    avg_maintenance_cost,
    avg_duration_hours,
    total_preventive,
    total_corrective,
    total_predictive,
    ROUND(total_preventive * 100.0 / total_work_orders, 2) as preventive_rate_pct,
    ROUND(total_corrective * 100.0 / total_work_orders, 2) as corrective_rate_pct
FROM gold_maintenance_kpis
ORDER BY total_maintenance_cost DESC;

CREATE VIEW vw_maintenance_backlog AS
SELECT 
    field,
    team,
    total_work_orders,
    total_open,
    total_in_progress,
    total_resolved,
    ROUND(total_open * 100.0 / total_work_orders, 2) as backlog_rate_pct
FROM gold_maintenance_kpis
ORDER BY total_open DESC;