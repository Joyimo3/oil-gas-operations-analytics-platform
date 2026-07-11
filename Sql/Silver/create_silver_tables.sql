-- ============================================================
-- SILVER LAYER - CLEANED DATA + SLA FLAGS
-- ============================================================

CREATE TABLE IF NOT EXISTS silver_incidents (
    incident_id TEXT,
    equipment_id TEXT,
    field TEXT,
    team TEXT,
    category TEXT,
    incident_date TEXT,
    incident_type TEXT,
    severity TEXT,
    status TEXT,
    resolution_hours REAL,
    sla_breach TEXT,
    downtime_hours REAL,
    reported_by TEXT,
    sla_status TEXT
);

CREATE TABLE IF NOT EXISTS silver_production (
    production_id TEXT,
    equipment_id TEXT,
    field TEXT,
    team TEXT,
    category TEXT,
    production_date TEXT,
    oil_volume_bbl REAL,
    gas_volume_mcf REAL,
    water_volume_bbl REAL,
    choke_size REAL,
    wellhead_pressure REAL,
    deferred_production_bbls REAL,
    operator TEXT
);

CREATE TABLE IF NOT EXISTS silver_maintenance (
    maintenance_id TEXT,
    equipment_id TEXT,
    field TEXT,
    team TEXT,
    category TEXT,
    issued_date TEXT,
    resolved_date TEXT,
    maintenance_type TEXT,
    maintenance_cost REAL,
    status TEXT,
    maintenance_duration_hours REAL,
    operator TEXT
);

CREATE TABLE IF NOT EXISTS silver_hse (
    hse_id TEXT,
    equipment_id TEXT,
    field TEXT,
    team TEXT,
    category TEXT,
    incident_date TEXT,
    incident_type TEXT,
    severity TEXT,
    near_miss TEXT,
    days_lost INTEGER,
    department TEXT,
    location TEXT,
    reported_by TEXT,
    investigator TEXT
);