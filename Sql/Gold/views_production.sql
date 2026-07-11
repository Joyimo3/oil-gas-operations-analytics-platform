CREATE VIEW vw_production_by_field AS
SELECT 
    field,
    team,
    total_readings,
    total_oil_volume_bbls,
    total_gas_volume_mcf,
    total_water_volume_bbls,
    total_deferred_bbls,
    ROUND(total_deferred_bbls * 100.0 / total_oil_volume_bbls, 2) as production_loss_pct,
    avg_wellhead_pressure,
    avg_choke_size
FROM gold_production_kpis
ORDER BY total_oil_volume_bbls DESC;


CREATE VIEW vw_production_efficiency AS
SELECT 
    field,
    team,
    total_oil_volume_bbls,
    total_deferred_bbls,
    ROUND((total_oil_volume_bbls - total_deferred_bbls), 2) as net_production,
    ROUND(total_deferred_bbls * 100.0 / total_oil_volume_bbls, 2) as loss_rate_pct
FROM gold_production_kpis
ORDER BY loss_rate_pct DESC;