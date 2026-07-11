-- ============================================================
-- DIM EQUIPMENT - Central Dimension Table
-- This connects all 4 domains together
-- ============================================================

CREATE TABLE IF NOT EXISTS dim_equipment (
    equipment_id TEXT PRIMARY KEY,
    field TEXT,
    team TEXT,
    category TEXT
);

INSERT INTO dim_equipment VALUES
    ('PUMP-101', 'Bonny Field', 'Team Alpha', 'Pumping Unit'),
    ('PUMP-102', 'Bonny Field', 'Team Alpha', 'Pumping Unit'),
    ('COMP-201', 'Forcados Field', 'Team Bravo', 'Compressor'),
    ('COMP-202', 'Forcados Field', 'Team Bravo', 'Compressor'),
    ('VALVE-301', 'Escravos Field', 'Team Charlie', 'Pressure Valve'),
    ('VALVE-302', 'Escravos Field', 'Team Charlie', 'Pressure Valve'),
    ('PIPE-401', 'Brass Terminal', 'Team Delta', 'Pipeline Segment'),
    ('PIPE-402', 'Brass Terminal', 'Team Delta', 'Pipeline Segment'),
    ('TANK-501', 'Qua Iboe Field', 'Team Alpha', 'Storage Tank'),
    ('TANK-502', 'Qua Iboe Field', 'Team Bravo', 'Storage Tank');

    -- dim_field from existing data
CREATE TABLE IF NOT EXISTS dim_field (
    field TEXT PRIMARY KEY,
    region TEXT DEFAULT 'Niger Delta'
);

INSERT OR IGNORE INTO dim_field (field)
SELECT DISTINCT field 
FROM silver_incidents;

-- dim_team from existing data
CREATE TABLE IF NOT EXISTS dim_team (
    team TEXT PRIMARY KEY
);

INSERT OR IGNORE INTO dim_team (team)
SELECT DISTINCT team 
FROM silver_incidents;