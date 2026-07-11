# ============================================================
# OIL & GAS OPERATIONS - VALIDATION PIPELINE
# validation_pipeline.py
# ============================================================
import pandas as pd
import os
from datetime import datetime
from pydantic import BaseModel, ValidationError, field_validator
from typing import Optional
from Scripts.generate_daily_data import EQUIPMENT_REGISTRY
from config.logger import logger


# ============================================================
# LOAD CONFIG
# ============================================================
from config.settings import PATHS, SLA_RULES

RAW_PATHS = PATHS["raw"]
CLEAN_PATH = PATHS["clean"]
ERRORS_PATH = PATHS["errors"]
ALERTS_PATH = PATHS["alerts"]

# Create folders if they don't exist
os.makedirs(CLEAN_PATH, exist_ok=True)
os.makedirs(ERRORS_PATH, exist_ok=True)
os.makedirs(ALERTS_PATH, exist_ok=True)

# ============================================================
# PYDANTIC MODELS - STRICT TYPE ENFORCEMENT
# These run after Pandas validation as a final check
# before anything touches the database
# ============================================================

class IncidentModel(BaseModel):
    incident_id: str
    equipment_id: str
    field: str
    team: str
    category: str
    incident_date: datetime
    incident_type: str
    severity: str
    status: str
    resolution_hours: float
    sla_breach: str
    downtime_hours: float
    reported_by: str


class ProductionModel(BaseModel):
    production_id: str
    equipment_id: str
    field: str
    team: str
    category: str
    production_date: datetime
    oil_volume_bbl: float
    gas_volume_mcf: float
    water_volume_bbl: float
    choke_size: float
    wellhead_pressure: float
    deferred_production_bbls: float
    operator: str

class MaintenanceModel(BaseModel):
    maintenance_id: str
    equipment_id: str
    field: str
    team: str
    category: str
    issued_date: datetime
    resolved_date: datetime
    maintenance_type: str
    maintenance_cost: float
    status: str
    maintenance_duration_hours: float
    operator: str

class HSEModel(BaseModel):
    hse_id: str
    equipment_id: str
    field: str
    team: str
    category: str
    incident_date: datetime
    incident_type: str
    severity: str
    near_miss: str
    days_lost: int
    department: str
    location: str
    reported_by: str
    investigator: str


# ============================================================
# VALIDATE INCIDENTS
# ============================================================
def validate_incidents():
    try:
        logger.info("Starting incident validation...")
        # read raw incidents file
        df=pd.read_csv(f"{RAW_PATHS}incidents.csv")

        clean_records = []
        error_records = []
        alert_records = []

        for _, row in df.iterrows():
            errors = []
            #check for missing incident_date and future dates
            if pd.isnull(row['incident_date']):
                errors.append("Missing incident_date")

            elif pd.to_datetime(row['incident_date']) > datetime.now():
                errors.append("Incident date cannot be in the future")
        
            #check for null sla_breach
            if pd.isnull(row['sla_breach']):
                errors.append("Missing sla_breach ")

            #check for null resolution_hours and negative values
            if pd.isnull(row['resolution_hours']):
                errors.append("Missing resolution_hours")

            elif row['resolution_hours'] < 0:
                errors.append("Resolution hours cannot be negative")

            #check for null downtime_hours and negative values
            if pd.isnull(row['downtime_hours']):
                errors.append("Missing downtime_hours")

            elif row['downtime_hours'] < 0:
                errors.append("Downtime hours cannot be negative")

            #check for missing status and invalid status values
            if pd.isnull(row['status']):
                errors.append("Missing status")

            elif row['status'] not in ['Open', 'Resolved', 'In Progress']:
                errors.append(f"Invalid status: {row['status']}")

            #check for missing severity and invalid severity values
            if pd.isnull(row['severity']):
                errors.append("Missing severity")

            elif row['severity'] not in ['Low', 'Medium', 'High', 'Critical']:
                errors.append(f"Invalid severity: {row['severity']}")

            #check for equipment_id in registry and missing equipment_id
            if pd.isnull(row['equipment_id']):
                errors.append("Missing equipment_id") 
            elif row['equipment_id'] not in [e['equipment_id'] for e in EQUIPMENT_REGISTRY]:
                errors.append(f"Unknown equipment_id: {row['equipment_id']}") 

            # checkks for incident_type and invalid values
            if pd.isnull(row['incident_type']):
                errors.append("Missing incident_type")    
            elif row['incident_type'] not in ['Equipment Failure', 'Pressure Drop', 'Leak', 'Power Outage', 'Corrosion', 'Valve Malfunction']:
                errors.append(f"Invalid incident_type: {row['incident_type']}") 

            # sla breach consistency check
            if not pd.isnull(row["resolution_hours"]) and not pd.isnull(row["severity"]):
                sla_limit = SLA_RULES.get(row["severity"])
                if sla_limit:
                    if row["resolution_hours"] > sla_limit and row["sla_breach"] == "No":
                        errors.append(f"SLA inconsistency: {row['severity']} resolved in {row['resolution_hours']}hrs but sla_breach marked No")
                    if row["resolution_hours"] <= sla_limit and row["sla_breach"] == "Yes":
                        errors.append(f"SLA inconsistency: {row['severity']} resolved in {row['resolution_hours']}hrs but sla_breach marked Yes")

            if errors:
                row["error_reason"] = " | ".join(errors)
                error_records.append(row)
            else:
                sla_limit = SLA_RULES.get(row["severity"])
                if sla_limit and row["resolution_hours"] > sla_limit:
                    row["sla_status"] = "BREACHED"
                    alert_records.append(row)
                else:
                    row["sla_status"] = "COMPLIANT"
                clean_records.append(row)

        # save clean records
        clean_df = pd.DataFrame(clean_records)
        clean_df.to_csv(f"{CLEAN_PATH}incidents_clean.csv", index=False)

        # save error records
        error_df = pd.DataFrame(error_records)
        error_df.to_csv(f"{ERRORS_PATH}incidents_errors.csv", index=False)

        # save alert records
        alert_df = pd.DataFrame(alert_records)
        alert_df.to_csv(f"{ALERTS_PATH}incidents_alerts.csv", index=False)

        logger.info(f"Incidents validated: {len(clean_records)} clean | {len(error_records)} errors | {len(alert_records)} alerts")
        return {
            "incidents_clean": len(clean_records),
            "incidents_errors": len(error_records),
            "incidents_alerts": len(alert_records)
        }
    except Exception:
        logger.exception("❌ Incident validation failed.")
        raise

    # ============================================================
    # VALIDATE PRODUCTION
    # ============================================================
def validate_production():
    try:
        logger.info("Starting production validation...")    
        # read raw production file
        df=pd.read_csv(f"{RAW_PATHS}production.csv")
        
        clean_records = []
        error_records = []
        alert_records = []

        for _, row in df.iterrows():
            errors = []
            #check for missing production_date and future dates (pd to date time converts it to datetime)
            if pd.isnull(row['production_date']):
                errors.append("Missing production_date")

            elif pd.to_datetime(row['production_date']) > datetime.now():
                errors.append("Production date cannot be in the future")
            
            # check for null operator and invalid operator values
            if pd.isnull(row['operator']):
                errors.append("Missing operator")

            elif row['operator'] == 'Unknown':
                errors.append("Operator cannot be Unknown") 
        
            #check for null oil_volume_bbls and negative values
            if pd.isnull(row['oil_volume_bbl']):
                errors.append("Missing oil_volume_bbls")

            elif row['oil_volume_bbl'] < 0:
                errors.append("Oil volume cannot be negative")

            #check for null gas_volume_mcf and negative values
            if pd.isnull(row['gas_volume_mcf']):
                errors.append("Missing gas_volume_mcf")

            elif row['gas_volume_mcf'] < 0:
                errors.append("Gas volume cannot be negative")

            #check for null water_volume_bbls and negative values
            if pd.isnull(row['water_volume_bbl']):
                errors.append("Missing water_volume_bbl")

            elif row['water_volume_bbl'] < 0:
                errors.append("Water volume cannot be negative")

            #check for null choke_size and negative values
            if pd.isnull(row['choke_size']):
                errors.append("Missing choke_size")

            elif row['choke_size'] < 0:
                errors.append("Choke size cannot be negative")

            #check for null wellhead_pressure and negative values
            if pd.isnull(row['wellhead_pressure']):
                errors.append("Missing wellhead_pressure")

            elif row['wellhead_pressure'] < 0:
                errors.append("Wellhead pressure cannot be negative")

            #check for null deferred_production_bbls and negative values
            if pd.isnull(row['deferred_production_bbls']):
                errors.append("Missing deferred_production_bbls")

            elif row['deferred_production_bbls'] < 0:
                errors.append("Deferred production cannot be negative")

            #check for equipment_id in registry and missing equipment_id
            if pd.isnull(row['equipment_id']):
                errors.append("Missing equipment_id") 
            elif row['equipment_id'] not in [e['equipment_id'] for e in EQUIPMENT_REGISTRY]:
                errors.append(f"Unknown equipment_id: {row['equipment_id']}") 

            # decide where the record goes
            if errors:
                row["error_reason"] = " | ".join(errors)
                error_records.append(row)
            else:
                clean_records.append(row)

        #save clean records
        clean_df = pd.DataFrame(clean_records)
        clean_df.to_csv(f"{CLEAN_PATH}production_clean.csv", index=False)

        # save error records
        error_df = pd.DataFrame(error_records)
        error_df.to_csv(f"{ERRORS_PATH}production_errors.csv", index=False)

        # save alert records
        alert_df = pd.DataFrame(alert_records)
        alert_df.to_csv(f"{ALERTS_PATH}production_alerts.csv", index=False)

        logger.info(f"Production validated: {len(clean_records)} clean | {len(error_records)} errors | {len(alert_records)} alerts")     
        return {
            "production_clean": len(clean_records),
            "production_errors": len(error_records)
        }
    except Exception:
        logger.exception("❌ Production validation failed.")    
        raise

# ============================================================
# VALIDATE MAINTENANCE
# ============================================================
def validate_maintenance():
    try:
        logger.info("Starting maintenance validation...")
    # read raw maintenance file
        df=pd.read_csv(f"{RAW_PATHS}maintenance.csv")
        
        clean_records = []
        error_records = []
        alert_records = []

        for _, row in df.iterrows():
            errors = []

            # check for missing issued_date and future dates
            if pd.isnull(row['issued_date']):
                errors.append("Missing issued_date")
            elif pd.to_datetime(row['issued_date']) > pd.to_datetime('today'):
                errors.append("Issued date cannot be in the future")
            
            # check for missing resolved_date and future dates
            if pd.isnull(row['resolved_date']):
                errors.append("Missing resolved_date")  
            elif pd.to_datetime(row['resolved_date']) > pd.to_datetime('today'):
                errors.append("Resolved date cannot be in the future")

            # check that resolved_date is after issued_date
            if not pd.isnull(row['issued_date']) and not pd.isnull(row['resolved_date']):
                if pd.to_datetime(row['resolved_date']) < pd.to_datetime(row['issued_date']):
                    errors.append("Resolved date cannot be before issued date")
            
            # check for null operator and invalid operator values
            if pd.isnull(row['operator']):
                errors.append("Missing operator")
            elif row['operator'] == 'Unknown':
                errors.append("Invalid operator value")
            
            #checkk for nuull maintenace type and invalid values
            if pd.isnull(row['maintenance_type']):
                errors.append("Missing maintenance_type")
            elif row['maintenance_type'] not in ['Corrective', 'Preventive', 'Predictive']:
                errors.append(f"Invalid maintenance_type: {row['maintenance_type']}") 

            #check for null maintenance_cost and negative values
            if pd.isnull(row['maintenance_cost']):
                errors.append("Missing maintenance_cost")
            elif row['maintenance_cost'] < 0:
                errors.append("Maintenance cost cannot be negative")
            
            #check for null maintenance_duration_hours and negative values
            if pd.isnull(row['maintenance_duration_hours']):
                errors.append("Missing maintenance_duration_hours")
            elif row['maintenance_duration_hours'] < 0:
                errors.append("Maintenance duration cannot be negative")

            #check for null status and invalid status values
            if pd.isnull(row['status']):
                errors.append("Missing status")
            elif row['status'] not in ['Open', 'Resolved', 'In Progress']:
                errors.append(f"Invalid status: {row['status']}") 

            #check for equipment_id in registry and missing equipment_id
            if pd.isnull(row['equipment_id']):
                errors.append("Missing equipment_id")
            elif row['equipment_id'] not in [e['equipment_id'] for e in EQUIPMENT_REGISTRY]:
                errors.append(f"Unknown equipment_id: {row['equipment_id']}")

            # decide where the record goes
            if errors:
                row["error_reason"] = " | ".join(errors)
                error_records.append(row)
            else:
                clean_records.append(row)

        # save clean records
        clean_df = pd.DataFrame(clean_records)
        clean_df.to_csv(f"{CLEAN_PATH}maintenance_clean.csv", index=False)

        # save error records
        error_df = pd.DataFrame(error_records)
        error_df.to_csv(f"{ERRORS_PATH}maintenance_errors.csv", index=False)

        # save alert records
        alert_df = pd.DataFrame(alert_records)
        alert_df.to_csv(f"{ALERTS_PATH}maintenance_alerts.csv", index=False)

        logger.info(f"Maintenance validated: {len(clean_records)} clean | {len(error_records)} errors | {len(alert_records)} alerts")
        return {
            "maintenance_clean": len(clean_records),
            "maintenance_errors": len(error_records)
        }
    except Exception:
        logger.exception("❌ Maintenance validation failed.")
        raise
# ============================================================
# VALIDATE HSE
# ============================================================
def validate_hse():
    try:
        logger.info("Starting HSE validation...")
        df = pd.read_csv(f"{RAW_PATHS}hse.csv")

        clean_records = []
        error_records = []
        alert_records = []

        for _, row in df.iterrows():
            errors = []

            # check for missing incident_date and future dates
            if pd.isnull(row["incident_date"]):
                errors.append("Missing incident_date")
            elif pd.to_datetime(row["incident_date"]) > datetime.now():
                errors.append("Incident date cannot be in the future")

            # check for missing investigator
            if pd.isnull(row["investigator"]):
                errors.append("Missing investigator")

            # check for null and negative days_lost
            if pd.isnull(row["days_lost"]):
                errors.append("Missing days_lost")
            elif row["days_lost"] < 0:
                errors.append("Days lost cannot be negative")

            # check for null and invalid severity
            if pd.isnull(row["severity"]):
                errors.append("Missing severity")
            elif row["severity"] not in ["Critical", "High", "Medium", "Low"]:
                errors.append(f"Invalid severity: {row['severity']}")

            # check for null and invalid incident_type
            if pd.isnull(row["incident_type"]):
                errors.append("Missing incident_type")
            elif row["incident_type"] not in ["Fire", "Chemical Spill", "Fall", "Gas Leak", "Explosion", "Equipment Strike"]:
                errors.append(f"Invalid incident_type: {row['incident_type']}")

            # check for null and invalid department
            if pd.isnull(row["department"]):
                errors.append("Missing department")
            elif row["department"] not in ["Operations", "Maintenance", "Logistics", "HSE", "Engineering"]:
                errors.append(f"Invalid department: {row['department']}")

            # check for null near_miss
            if pd.isnull(row["near_miss"]):
                errors.append("Missing near_miss")
            elif row["near_miss"] not in ["Yes", "No"]:
                errors.append(f"Invalid near_miss: {row['near_miss']}")

            # check for null location
            if pd.isnull(row["location"]):
                errors.append("Missing location")

            # check for null reported_by
            if pd.isnull(row["reported_by"]):
                errors.append("Missing reported_by")
            
            # check for equipment_id in registry
            if pd.isnull(row["equipment_id"]):
                errors.append("Missing equipment_id")
            elif row["equipment_id"] not in [e["equipment_id"] for e in EQUIPMENT_REGISTRY]:
                errors.append(f"Unknown equipment_id: {row['equipment_id']}")

            # decide where the record goes
            if errors:
                row["error_reason"] = " | ".join(errors)
                error_records.append(row)
            else:
                clean_records.append(row)

        # save clean records
        clean_df = pd.DataFrame(clean_records)
        clean_df.to_csv(f"{CLEAN_PATH}hse_clean.csv", index=False)

        # save error records
        error_df = pd.DataFrame(error_records)
        error_df.to_csv(f"{ERRORS_PATH}hse_errors.csv", index=False)

        # save alert records
        alert_df = pd.DataFrame(alert_records)
        alert_df.to_csv(f"{ALERTS_PATH}hse_alerts.csv", index=False)

        logger.info(f"HSE validated: {len(clean_records)} clean | {len(error_records)} errors | {len(alert_records)} alerts")
        return {
            "hse_clean": len(clean_records),
            "hse_errors": len(error_records)
        }
    except Exception:
        logger.exception("❌ HSE validation failed.")
        raise

if __name__ == "__main__":
    validate_incidents()
    validate_production()
    validate_maintenance()
    validate_hse()