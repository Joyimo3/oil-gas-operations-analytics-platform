# ============================================================
# OIL & GAS OPERATIONS - DATA GENERATOR
# generate_daily_data.py
# ============================================================
from faker import Faker
import random
import pandas as pd
import os
from datetime import datetime, timedelta
from config.logger import logger

# Initialize Faker
fake = Faker()

# ============================================================
# FIXED EQUIPMENT REGISTRY
# This never changes. Every domain uses this same registry.
# PUMP-101 is ALWAYS Bonny Field, Team Alpha. No exceptions.
# ============================================================
EQUIPMENT_REGISTRY = [
    {"equipment_id": "PUMP-101", "field": "Bonny Field",     "team": "Team Alpha",   "category": "Pumping Unit"},
    {"equipment_id": "PUMP-102", "field": "Bonny Field",     "team": "Team Alpha",   "category": "Pumping Unit"},
    {"equipment_id": "COMP-201", "field": "Forcados Field",  "team": "Team Bravo",   "category": "Compressor"},
    {"equipment_id": "COMP-202", "field": "Forcados Field",  "team": "Team Bravo",   "category": "Compressor"},
    {"equipment_id": "VALVE-301","field": "Escravos Field",  "team": "Team Charlie", "category": "Pressure Valve"},
    {"equipment_id": "VALVE-302","field": "Escravos Field",  "team": "Team Charlie", "category": "Pressure Valve"},
    {"equipment_id": "PIPE-401", "field": "Brass Terminal",  "team": "Team Delta",   "category": "Pipeline Segment"},
    {"equipment_id": "PIPE-402", "field": "Brass Terminal",  "team": "Team Delta",   "category": "Pipeline Segment"},
    {"equipment_id": "TANK-501", "field": "Qua Iboe Field",  "team": "Team Alpha",   "category": "Storage Tank"},
    {"equipment_id": "TANK-502", "field": "Qua Iboe Field",  "team": "Team Bravo",   "category": "Storage Tank"},
]

# ============================================================
# LOAD CONFIG
# No hardcoded values. Everything comes from config.yaml
# ============================================================
from config.settings import PATHS, GENERATION

RAW_PATH = PATHS["raw"]
NUM_RECORDS = GENERATION["num_records"]
DIRTY_PERCENTAGE = GENERATION["dirty_percentage"]

os.makedirs(RAW_PATH, exist_ok=True)

# ============================================================
# INCIDENTS GENERATOR
# ============================================================
def generate_incidents(num_records=NUM_RECORDS):
    try:
        logger.info(f"Starting incident generation ({num_records} records)...")    

        records = []

        # _ is a convention developers use when they don't need the loop counter
        for _ in range(num_records):
            equipment = random.choice(EQUIPMENT_REGISTRY)
            is_dirty = random.random() < DIRTY_PERCENTAGE
            incident_date = fake.date_time_between(start_date="-6m", end_date="now")
            severity = random.choice(["Critical", "High", "Medium", "Low"])

            # incident types common in oil and gas operations
            incident_type = random.choice([
                "Equipment Failure", "Pressure Drop", "Leak",
                "Power Outage", "Corrosion", "Valve Malfunction"
            ])

            # status of the incident
            status = random.choice(["Open", "In Progress", "Resolved"])

            # resolution hours depends on severity
            if severity == "Critical":
                resolution_hours = round(random.uniform(1, 12), 2)
            elif severity == "High":
                resolution_hours = round(random.uniform(1, 24), 2)
            elif severity == "Medium":
                resolution_hours = round(random.uniform(1, 48), 2)
            else:
                resolution_hours = round(random.uniform(1, 72), 2)

            # sla breach check based on severity thresholds
            if severity == "Critical" and resolution_hours > 4:
                sla_breach = "Yes"
            elif severity == "High" and resolution_hours > 8:
                sla_breach = "Yes"
            elif severity == "Medium" and resolution_hours > 24:
                sla_breach = "Yes"
            elif severity == "Low" and resolution_hours > 48:
                sla_breach = "Yes"
            else:
                sla_breach = "No"

            # downtime hours always less than resolution hours
            downtime_hours = round(random.uniform(0.5, resolution_hours), 2)

            # inject dirty data into 15% of records
            if is_dirty:
                incident_date = None
                resolution_hours = -99
                status = "UNKNOWN"
                sla_breach = None

            # build the record using fixed equipment registry
            record = {
                "incident_id": fake.uuid4(),
                "equipment_id": equipment["equipment_id"],
                "field": equipment["field"],
                "team": equipment["team"],
                "category": equipment["category"],
                "incident_date": incident_date,
                "incident_type": incident_type,
                "severity": severity,
                "status": status,
                "resolution_hours": resolution_hours,
                "sla_breach": sla_breach,
                "downtime_hours": downtime_hours,
                "reported_by": fake.name(),
            }

            records.append(record)

        # convert to dataframe and save to data/raw/
        df = pd.DataFrame(records)
        df.to_csv(f"{RAW_PATH}incidents.csv", index=False)
        logger.info(f"Incidents generated: {len(df)} records saved to {RAW_PATH}incidents.csv")
    except Exception:
        logger.exception("❌ Incident generation failed.")
        raise



# ============================================================
# PRODUCTION GENERATOR
# ============================================================
def generate_production(num_records=NUM_RECORDS):
    try:
        logger.info(f"Starting production generation ({num_records} records)...")

        records = []

        for _ in range(num_records):
            equipment = random.choice(EQUIPMENT_REGISTRY)
            is_dirty = random.random() < DIRTY_PERCENTAGE
            production_date = fake.date_time_between(start_date="-6m", end_date="now")
            oil_volume_bbl = round(random.uniform(100, 5000), 2)
            gas_volume_mcf = round(random.uniform(50,2000),2)
            water_volume_bbl = round(random.uniform(10, 500), 2)
            choke_size = round(random.uniform(16, 64), 2)
            wellhead_pressure = round(random.uniform(100, 5000), 2)
            deferred_production_bbls = round(random.uniform(0, 500), 2)
            operator = fake.name()
            # inject dirty data into 15% of records
            if is_dirty:
                production_date = None
                oil_volume_bbl = -99
                gas_volume_mcf = -99
                water_volume_bbl = -99
                choke_size = None
                wellhead_pressure = None
                deferred_production_bbls = None
            # build the record using fixed equipment registry
            record = {
                "production_id": fake.uuid4(),
                "equipment_id": equipment["equipment_id"],
                "field": equipment["field"],
                "team": equipment["team"],
                "category": equipment["category"],
                "production_date": production_date,
                "oil_volume_bbl": oil_volume_bbl,
                "gas_volume_mcf": gas_volume_mcf,
                "water_volume_bbl": water_volume_bbl,
                "choke_size": choke_size,
                "wellhead_pressure": wellhead_pressure,
                "deferred_production_bbls": deferred_production_bbls,
                "operator": operator,
            }
            records.append(record)

        # convert to dataframe and save to data/raw/
        df = pd.DataFrame(records)
        df.to_csv(f"{RAW_PATH}production.csv", index=False)
        logger.info(f"Production records generated: {len(df)} records saved to {RAW_PATH}production.csv")
    except Exception:
        logger.exception("❌ Production generation failed.")
        raise

# ============================================================
# MAINTENANCE GENERATOR
# ============================================================

def generate_maintenance(num_records=NUM_RECORDS):
    try:
        logger.info(f"Starting maintenance generation ({num_records} records)...")
        records = []

        for _ in range(num_records):
            equipment = random.choice(EQUIPMENT_REGISTRY)
            is_dirty = random.random() < DIRTY_PERCENTAGE
            issued_date = fake.date_time_between(start_date="-6m", end_date="now")
            potential_resolved = issued_date + timedelta(hours=random.uniform(1, 72))
            resolved_date = min(potential_resolved, datetime.now())
            maintenance_type = random.choice(["Preventive", "Corrective", "Predictive"])
            maintenance_cost= round(random.uniform(1000, 50000), 2)
            status = random.choice(["Open", "In Progress", "Resolved"])
            maintenance_duration_hours = round((resolved_date - issued_date).total_seconds() / 3600, 2)
            operator = fake.name()
            # inject dirty data into 15% of records
            if is_dirty:
                issued_date = None
                resolved_date = None
                maintenance_type = "UNKNOWN"
                maintenance_duration_hours = -99
                operator = None
            # build the record using fixed equipment registry
            record = {
                "maintenance_id": fake.uuid4(),
                "equipment_id": equipment["equipment_id"],
                "field": equipment["field"],
                "team": equipment["team"],
                "category": equipment["category"],
                "issued_date": issued_date,
                "resolved_date": resolved_date,
                "maintenance_type": maintenance_type,
                "maintenance_duration_hours": maintenance_duration_hours,
                "maintenance_cost": maintenance_cost,
                "status": status,
                "operator": operator,
            }
            records.append(record)

        # convert to dataframe and save to data/raw/
        df = pd.DataFrame(records)
        df.to_csv(f"{RAW_PATH}maintenance.csv", index=False)
        logger.info(f"Maintenance records generated: {len(df)} records saved to {RAW_PATH}maintenance.csv")
    except Exception:
        logger.exception("❌ Maintenance generation failed.")
        raise
# ============================================================
# HSE GENERATOR
# ============================================================

def generate_hse(num_records=NUM_RECORDS):
    try:
        logger.info(f"Starting HSE generation ({num_records} records)...")

        records = []

        # _ is a convention developers use when they don't need the loop counter
        for _ in range(num_records):
            equipment = random.choice(EQUIPMENT_REGISTRY)
            is_dirty = random.random() < DIRTY_PERCENTAGE

            incident_date = fake.date_time_between(start_date="-6m", end_date="now")

            # type of safety incident
            incident_type = random.choice([
                "Fire", "Chemical Spill", "Fall", 
                "Gas Leak", "Explosion", "Equipment Strike"
            ])

            # how serious the incident was
            severity = random.choice(["Critical", "High", "Medium", "Low"])

            # did something almost happen but didn't
            near_miss = random.choice(["Yes", "No"])

            # working days lost due to incident
            days_lost = random.randint(0, 30)

            # which department was involved
            department = random.choice([
                "Operations", "Maintenance", "Logistics", 
                "HSE", "Engineering"
            ])

            # exact location on the field
            location = random.choice([
                "Wellhead", "Storage Area", "Pipeline Junction",
                "Control Room", "Pump Station", "Compressor Area"
            ])

            reported_by = fake.name()
            investigator = fake.name()

            # inject dirty data into 15% of records
            if is_dirty:
                incident_date = None
                days_lost = -99
                department = "UNKNOWN"
                investigator = None

            # build the record using fixed equipment registry
            record = {
                "hse_id": fake.uuid4(),
                "equipment_id": equipment["equipment_id"],
                "field": equipment["field"],
                "team": equipment["team"],
                "category": equipment["category"],
                "incident_date": incident_date,
                "incident_type": incident_type,
                "severity": severity,
                "near_miss": near_miss,
                "days_lost": days_lost,
                "department": department,
                "location": location,
                "reported_by": reported_by,
                "investigator": investigator,
            }

            records.append(record)

        # convert to dataframe and save to data/raw/
        df = pd.DataFrame(records)
        df.to_csv(f"{RAW_PATH}hse.csv", index=False)
        logger.info(f"HSE records generated: {len(df)} records saved to {RAW_PATH}hse.csv")
    except Exception:
        logger.exception("❌ HSE generation failed.")
        raise

# ============================================================
# RUN THE GENERATORS
# ============================================================
if __name__ == "__main__":
    generate_incidents()
    generate_production()
    generate_maintenance()
    generate_hse()
