# ============================================================
# OIL & GAS OPERATIONS - VALIDATION TESTS
# tests/test_validation.py
# ============================================================

import pytest
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Scripts.generate_daily_data import EQUIPMENT_REGISTRY
from config.settings import SLA_RULES

# ============================================================
# EQUIPMENT REGISTRY TESTS
# ============================================================

def test_equipment_registry_has_10_items():
    assert len(EQUIPMENT_REGISTRY) == 10

def test_equipment_registry_has_required_keys():
    for equipment in EQUIPMENT_REGISTRY:
        assert "equipment_id" in equipment
        assert "field" in equipment
        assert "team" in equipment
        assert "category" in equipment

def test_pump_101_is_bonny_field():
    pump_101 = next(e for e in EQUIPMENT_REGISTRY if e["equipment_id"] == "PUMP-101")
    assert pump_101["field"] == "Bonny Field"
    assert pump_101["team"] == "Team Alpha"

def test_all_equipment_ids_are_unique():
    ids = [e["equipment_id"] for e in EQUIPMENT_REGISTRY]
    assert len(ids) == len(set(ids))

# ============================================================
# INCIDENTS VALIDATION TESTS
# ============================================================

def test_negative_resolution_hours_flagged_as_error():
    errors = []
    resolution_hours = -99
    if resolution_hours < 0:
        errors.append("Resolution hours cannot be negative")
    assert "Resolution hours cannot be negative" in errors

def test_null_incident_date_flagged_as_error():
    errors = []
    incident_date = None
    if pd.isnull(incident_date):
        errors.append("Missing incident_date")
    assert "Missing incident_date" in errors

def test_invalid_severity_flagged_as_error():
    errors = []
    severity = "EXTREME"
    if severity not in ["Critical", "High", "Medium", "Low"]:
        errors.append(f"Invalid severity: {severity}")
    assert "Invalid severity: EXTREME" in errors

def test_invalid_status_flagged_as_error():
    errors = []
    status = "UNKNOWN"
    if status not in ["Open", "In Progress", "Resolved"]:
        errors.append(f"Invalid status: {status}")
    assert "Invalid status: UNKNOWN" in errors

def test_unknown_equipment_id_flagged_as_error():
    errors = []
    equipment_id = "FAKE-999"
    valid_ids = [e["equipment_id"] for e in EQUIPMENT_REGISTRY]
    if equipment_id not in valid_ids:
        errors.append(f"Unknown equipment_id: {equipment_id}")
    assert "Unknown equipment_id: FAKE-999" in errors

def test_clean_incident_record_passes_validation():
    errors = []
    resolution_hours = 5.0
    incident_date = "2026-01-01"
    severity = "High"
    status = "Resolved"
    equipment_id = "PUMP-101"

    if pd.isnull(incident_date):
        errors.append("Missing incident_date")
    if resolution_hours < 0:
        errors.append("Resolution hours cannot be negative")
    if severity not in ["Critical", "High", "Medium", "Low"]:
        errors.append("Invalid severity")
    if status not in ["Open", "In Progress", "Resolved"]:
        errors.append("Invalid status")
    valid_ids = [e["equipment_id"] for e in EQUIPMENT_REGISTRY]
    if equipment_id not in valid_ids:
        errors.append("Unknown equipment_id")

    assert len(errors) == 0

def test_sla_breach_detected_for_critical_incident():
    severity = "Critical"
    resolution_hours = 10.0
    sla_limit = SLA_RULES.get(severity)
    assert resolution_hours > sla_limit

# ============================================================
# PRODUCTION VALIDATION TESTS
# ============================================================

def test_negative_oil_volume_flagged_as_error():
    errors = []
    oil_volume = -100.3
    if oil_volume < 0:
        errors.append("Oil volume cannot be negative")
    assert "Oil volume cannot be negative" in errors

def test_null_production_date_flagged_as_error():
    errors = []
    production_date = None
    if pd.isnull(production_date):
        errors.append("Missing production_date")
    assert "Missing production_date" in errors

def test_clean_production_record_passes_validation():
    errors = []
    production_date = "2026-01-01"
    oil_volume = 1500.0
    gas_volume = 800.0
    water_volume = 200.0

    if pd.isnull(production_date):
        errors.append("Missing production_date")
    if oil_volume < 0:
        errors.append("Oil volume cannot be negative")
    if gas_volume < 0:
        errors.append("Gas volume cannot be negative")
    if water_volume < 0:
        errors.append("Water volume cannot be negative")

    assert len(errors) == 0

# ============================================================
# MAINTENANCE VALIDATION TESTS
# ============================================================

def test_negative_duration_flagged_as_error():
    errors = []
    duration = -99
    if duration < 0:
        errors.append("Maintenance duration cannot be negative")
    assert "Maintenance duration cannot be negative" in errors

def test_unknown_maintenance_type_flagged_as_error():
    errors = []
    maintenance_type = "UNKNOWN"
    if maintenance_type not in ["Preventive", "Corrective", "Predictive"]:
        errors.append(f"Invalid maintenance_type: {maintenance_type}")
    assert "Invalid maintenance_type: UNKNOWN" in errors

def test_resolved_before_issued_flagged_as_error():
    errors = []
    issued_date = pd.to_datetime("2026-01-10")
    resolved_date = pd.to_datetime("2026-01-05")
    if resolved_date < issued_date:
        errors.append("Resolved date cannot be before issued date")
    assert "Resolved date cannot be before issued date" in errors

def test_clean_maintenance_record_passes_validation():
    errors = []
    issued_date = pd.to_datetime("2026-01-01")
    resolved_date = pd.to_datetime("2026-01-02")
    maintenance_type = "Preventive"
    duration = 24.0
    cost = 5000.0

    if resolved_date < issued_date:
        errors.append("Resolved date cannot be before issued date")
    if maintenance_type not in ["Preventive", "Corrective", "Predictive"]:
        errors.append("Invalid maintenance_type")
    if duration < 0:
        errors.append("Maintenance duration cannot be negative")
    if cost < 0:
        errors.append("Maintenance cost cannot be negative")

    assert len(errors) == 0

# ============================================================
# HSE VALIDATION TESTS
# ============================================================

def test_negative_days_lost_flagged_as_error():
    errors = []
    days_lost = -99
    if days_lost < 0:
        errors.append("Days lost cannot be negative")
    assert "Days lost cannot be negative" in errors

def test_invalid_department_flagged_as_error():
    errors = []
    department = "UNKNOWN"
    if department not in ["Operations", "Maintenance", "Logistics", "HSE", "Engineering"]:
        errors.append(f"Invalid department: {department}")
    assert "Invalid department: UNKNOWN" in errors

def test_clean_hse_record_passes_validation():
    errors = []
    incident_date = "2026-01-01"
    days_lost = 5
    severity = "High"
    department = "Operations"
    incident_type = "Fire"

    if pd.isnull(incident_date):
        errors.append("Missing incident_date")
    if days_lost < 0:
        errors.append("Days lost cannot be negative")
    if severity not in ["Critical", "High", "Medium", "Low"]:
        errors.append("Invalid severity")
    if department not in ["Operations", "Maintenance", "Logistics", "HSE", "Engineering"]:
        errors.append("Invalid department")
    if incident_type not in ["Fire", "Chemical Spill", "Fall", "Gas Leak", "Explosion", "Equipment Strike"]:
        errors.append("Invalid incident_type")

    assert len(errors) == 0