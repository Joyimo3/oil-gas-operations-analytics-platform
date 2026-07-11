# ============================================================
# OIL & GAS OPERATIONS - PIPELINE TESTS
# tests/test_pipeline.py
# ============================================================

import pytest
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Scripts.generate_daily_data import (
    generate_incidents,
    generate_production,
    generate_maintenance,
    generate_hse
)

# ============================================================
# FILE CREATION TESTS
# ============================================================

def test_generate_incidents_creates_csv():
    generate_incidents()
    assert os.path.exists("data/raw/incidents.csv")

def test_generate_production_creates_csv():
    generate_production()
    assert os.path.exists("data/raw/production.csv")

def test_generate_maintenance_creates_csv():
    generate_maintenance()
    assert os.path.exists("data/raw/maintenance.csv")

def test_generate_hse_creates_csv():
    generate_hse()
    assert os.path.exists("data/raw/hse.csv")

# ============================================================
# RECORD COUNT TESTS
# ============================================================

def test_incidents_csv_has_1000_records():
    generate_incidents()
    df = pd.read_csv("data/raw/incidents.csv")
    assert len(df) == 1000

def test_production_csv_has_1000_records():
    generate_production()
    df = pd.read_csv("data/raw/production.csv")
    assert len(df) == 1000

def test_maintenance_csv_has_1000_records():
    generate_maintenance()
    df = pd.read_csv("data/raw/maintenance.csv")
    assert len(df) == 1000

def test_hse_csv_has_1000_records():
    generate_hse()
    df = pd.read_csv("data/raw/hse.csv")
    assert len(df) == 1000

# alerts file exists
def test_validation_creates_alerts_file():
    assert os.path.exists("data/alerts/incidents_alerts.csv")

# all clean files less than 1000
def test_production_clean_less_than_total():
    df = pd.read_csv("data/clean/production_clean.csv")
    assert len(df) < 1000

def test_maintenance_clean_less_than_total():
    df = pd.read_csv("data/clean/maintenance_clean.csv")
    assert len(df) < 1000

def test_hse_clean_less_than_total():
    df = pd.read_csv("data/clean/hse_clean.csv")
    assert len(df) < 1000

# error files have records
def test_incidents_errors_has_records():
    df = pd.read_csv("data/errors/incidents_errors.csv")
    assert len(df) > 0

def test_production_errors_has_records():
    df = pd.read_csv("data/errors/production_errors.csv")
    assert len(df) > 0

def test_maintenance_errors_has_records():
    df = pd.read_csv("data/errors/maintenance_errors.csv")
    assert len(df) > 0

def test_hse_errors_has_records():
    df = pd.read_csv("data/errors/hse_errors.csv")
    assert len(df) > 0

# alerts file has records
def test_alerts_has_records():
    df = pd.read_csv("data/alerts/incidents_alerts.csv")
    assert len(df) > 0

# content check
def test_incidents_has_correct_columns():
    df = pd.read_csv("data/raw/incidents.csv")
    expected_columns = ["incident_id", "equipment_id", "field", "team", 
                       "category", "incident_date", "incident_type", 
                       "severity", "status", "resolution_hours", 
                       "sla_breach", "downtime_hours", "reported_by"]
    for col in expected_columns:
        assert col in df.columns

def test_clean_incidents_has_sla_status_column():
    df = pd.read_csv("data/clean/incidents_clean.csv")
    assert "sla_status" in df.columns

def test_validation_creates_clean_files():
    assert os.path.exists("data/clean/incidents_clean.csv")
    assert os.path.exists("data/clean/production_clean.csv")
    assert os.path.exists("data/clean/maintenance_clean.csv")
    assert os.path.exists("data/clean/hse_clean.csv")

def test_validation_creates_error_files():
    assert os.path.exists("data/errors/incidents_errors.csv")
    assert os.path.exists("data/errors/production_errors.csv")
    assert os.path.exists("data/errors/maintenance_errors.csv")
    assert os.path.exists("data/errors/hse_errors.csv")



def test_clean_records_less_than_total():
    df_clean = pd.read_csv("data/clean/incidents_clean.csv")
    assert len(df_clean) < 1000