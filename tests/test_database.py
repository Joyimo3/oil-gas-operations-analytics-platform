# ============================================================
# OIL & GAS OPERATIONS - DATABASE TESTS
# tests/test_database.py
# ============================================================

import pytest
import sqlite3
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import PATHS

DATABASE_PATH = PATHS["database"]

def get_connection():
    return sqlite3.connect(DATABASE_PATH)

# ============================================================
# TABLE EXISTS TESTS
# ============================================================

def test_bronze_incidents_table_exists():
    conn = get_connection()
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bronze_incidents'")
    assert cursor.fetchone() is not None
    conn.close()

def test_bronze_production_table_exists():
    conn = get_connection()
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bronze_production'")
    assert cursor.fetchone() is not None
    conn.close()

def test_bronze_maintenance_table_exists():
    conn = get_connection()
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bronze_maintenance'")
    assert cursor.fetchone() is not None
    conn.close()

def test_bronze_hse_table_exists():
    conn = get_connection()
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bronze_hse'")
    assert cursor.fetchone() is not None
    conn.close()

def test_silver_incidents_table_exists():
    conn = get_connection()
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='silver_incidents'")
    assert cursor.fetchone() is not None
    conn.close()

def test_silver_production_table_exists():
    conn = get_connection()
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='silver_production'")
    assert cursor.fetchone() is not None
    conn.close()

def test_silver_maintenance_table_exists():
    conn = get_connection()
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='silver_maintenance'")
    assert cursor.fetchone() is not None
    conn.close()

def test_silver_hse_table_exists():
    conn = get_connection()
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='silver_hse'")
    assert cursor.fetchone() is not None
    conn.close()

def test_gold_sla_compliance_table_exists():
    conn = get_connection()
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='gold_sla_compliance'")
    assert cursor.fetchone() is not None
    conn.close()

# ============================================================
# RECORD COUNT TESTS
# ============================================================

def test_bronze_incidents_has_1000_records():
    conn = get_connection()
    cursor = conn.execute("SELECT COUNT(*) FROM bronze_incidents")
    count = cursor.fetchone()[0]
    assert count == 1000
    conn.close()

def test_bronze_production_has_1000_records():
    conn = get_connection()
    cursor = conn.execute("SELECT COUNT(*) FROM bronze_production")
    count = cursor.fetchone()[0]
    assert count == 1000
    conn.close()

def test_bronze_maintenance_has_1000_records():
    conn = get_connection()
    cursor = conn.execute("SELECT COUNT(*) FROM bronze_maintenance")
    count = cursor.fetchone()[0]
    assert count == 1000
    conn.close()

def test_bronze_hse_has_1000_records():
    conn = get_connection()
    cursor = conn.execute("SELECT COUNT(*) FROM bronze_hse")
    count = cursor.fetchone()[0]
    assert count == 1000
    conn.close()

def test_silver_incidents_has_less_than_bronze():
    conn = get_connection()
    bronze = conn.execute("SELECT COUNT(*) FROM bronze_incidents").fetchone()[0]
    silver = conn.execute("SELECT COUNT(*) FROM silver_incidents").fetchone()[0]
    assert silver < bronze
    conn.close()

def test_silver_production_has_less_than_bronze():
    conn = get_connection()
    bronze = conn.execute("SELECT COUNT(*) FROM bronze_production").fetchone()[0]
    silver = conn.execute("SELECT COUNT(*) FROM silver_production").fetchone()[0]
    assert silver < bronze
    conn.close()

def test_silver_maintenance_has_less_than_bronze():
    conn = get_connection()
    bronze = conn.execute("SELECT COUNT(*) FROM bronze_maintenance").fetchone()[0]
    silver = conn.execute("SELECT COUNT(*) FROM silver_maintenance").fetchone()[0]
    assert silver < bronze
    conn.close()

def test_silver_hse_has_less_than_bronze():
    conn = get_connection()
    bronze = conn.execute("SELECT COUNT(*) FROM bronze_hse").fetchone()[0]
    silver = conn.execute("SELECT COUNT(*) FROM silver_hse").fetchone()[0]
    assert silver < bronze
    conn.close()

def test_gold_sla_has_24_rows():
    conn = get_connection()
    cursor = conn.execute("SELECT COUNT(*) FROM gold_sla_compliance")
    count = cursor.fetchone()[0]
    assert count == 24
    conn.close()

def test_dim_field_has_5_rows():
    conn = get_connection()
    cursor = conn.execute("SELECT COUNT(*) FROM dim_field")
    count = cursor.fetchone()[0]
    assert count == 5
    conn.close()

def test_dim_team_has_4_rows():
    conn = get_connection()
    cursor = conn.execute("SELECT COUNT(*) FROM dim_team")
    count = cursor.fetchone()[0]
    assert count == 4
    conn.close()

# ============================================================
# CONTENT TESTS
# ============================================================

def test_silver_incidents_has_sla_status_column():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM silver_incidents LIMIT 1", conn)
    assert "sla_status" in df.columns
    conn.close()

def test_gold_sla_has_correct_columns():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM gold_sla_compliance LIMIT 1", conn)
    assert "compliance_rate_pct" in df.columns
    assert "breach_rate_pct" in df.columns
    assert "total_incidents" in df.columns
    conn.close()

def test_dim_field_contains_bonny_field():
    conn = get_connection()
    cursor = conn.execute("SELECT * FROM dim_field WHERE field = 'Bonny Field'")
    assert cursor.fetchone() is not None
    conn.close()

def test_dim_team_contains_all_teams():
    conn = get_connection()
    df = pd.read_sql("SELECT team FROM dim_team", conn)
    teams = df["team"].tolist()
    assert "Team Alpha" in teams
    assert "Team Bravo" in teams
    assert "Team Charlie" in teams
    assert "Team Delta" in teams
    conn.close()