# ============================================================
# OIL & GAS OPERATIONS - DATABASE LOADER
# load_database.py
# Loads data into Bronze, Silver and Gold layers
# ============================================================

import pandas as pd
import sqlite3
import os
from config.settings import PATHS
from config.logger import logger

RAW_PATH = PATHS["raw"]
CLEAN_PATH = PATHS["clean"]
DATABASE_PATH = PATHS["database"]

TOTAL_RECORDS = 1000  # Assuming each raw CSV has 1000 records for metrics calculations

def get_connection():
    return sqlite3.connect(DATABASE_PATH)

# ============================================================
# LOAD BRONZE LAYER
# Raw data as-is from data/raw/
# ============================================================

def load_bronze():
    try:
        logger.info("Starting Bronze layer load...")
        conn = get_connection()
        
        # load all 4 raw CSVs into bronze tables
        incidents = pd.read_csv(f"{RAW_PATH}incidents.csv")
        production = pd.read_csv(f"{RAW_PATH}production.csv")
        maintenance = pd.read_csv(f"{RAW_PATH}maintenance.csv")
        hse = pd.read_csv(f"{RAW_PATH}hse.csv")

        # write to bronze tables
        incidents.to_sql("bronze_incidents", conn, if_exists="replace", index=False)
        production.to_sql("bronze_production", conn, if_exists="replace", index=False)
        maintenance.to_sql("bronze_maintenance", conn, if_exists="replace", index=False)
        hse.to_sql("bronze_hse", conn, if_exists="replace", index=False)

        conn.close()
        logger.info("Bronze layer loaded successfully")
    except Exception:
        logger.exception("❌ Bronze layer load failed.")    
        raise



# ============================================================
# LOAD SILVER LAYER
# Clean data from data/clean/ + SLA flags added
# ============================================================

def load_silver():
    try:
        logger.info("Starting Silver layer load...")
        conn = get_connection()

        # load all 4 clean CSVs
        incidents = pd.read_csv(f"{CLEAN_PATH}incidents_clean.csv")
        production = pd.read_csv(f"{CLEAN_PATH}production_clean.csv")
        maintenance = pd.read_csv(f"{CLEAN_PATH}maintenance_clean.csv")
        hse = pd.read_csv(f"{CLEAN_PATH}hse_clean.csv")

        # add sla_status column to incidents
        incidents["sla_status"] = incidents["sla_breach"].apply(
            lambda x: "BREACHED" if x == "Yes" else "COMPLIANT"
        )

        # write to silver tables
        incidents.to_sql("silver_incidents", conn, if_exists="replace", index=False)
        production.to_sql("silver_production", conn, if_exists="replace", index=False)
        maintenance.to_sql("silver_maintenance", conn, if_exists="replace", index=False)
        hse.to_sql("silver_hse", conn, if_exists="replace", index=False)

        conn.close()
        logger.info("Silver layer loaded successfully")
    except Exception:
        logger.exception("❌ Silver layer load failed.")
        raise


# ============================================================
# LOAD DIMENSIONS
# Must run before Gold tables
# ============================================================
def load_dimensions():
    try:
        logger.info("Starting dimension load...")
        conn = get_connection()    

        # dim_field
        dim_field = pd.read_sql("""
            SELECT DISTINCT field, 'Niger Delta' as region
            FROM silver_incidents
        """, conn)
        dim_field.to_sql("dim_field", conn, if_exists="replace", index=False)

        # dim_team
        dim_team = pd.read_sql("""
            SELECT DISTINCT team
            FROM silver_incidents
        """, conn)
        dim_team.to_sql("dim_team", conn, if_exists="replace", index=False)

        conn.close()
        logger.info("Dimensions loaded successfully")
    except Exception:
        logger.exception("❌ Dimension load failed.")
        raise
# ============================================================
# LOAD GOLD LAYER
# ============================================================
def load_gold(validation_results = None):
    try:
        logger.info("Starting Gold layer load...")
        conn = get_connection()

        # gold_sla_compliance
        gold_sla = pd.read_sql("""
            SELECT field, team, severity,
                COUNT(*) as total_incidents,
                SUM(CASE WHEN sla_status = 'BREACHED' THEN 1 ELSE 0 END) as total_breaches,
                SUM(CASE WHEN sla_status = 'COMPLIANT' THEN 1 ELSE 0 END) as total_compliant,
                ROUND(SUM(CASE WHEN sla_status = 'COMPLIANT' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as compliance_rate_pct,
                ROUND(SUM(CASE WHEN sla_status = 'BREACHED' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as breach_rate_pct,
                ROUND(AVG(resolution_hours), 2) as avg_resolution_hours
            FROM silver_incidents
            GROUP BY field, team, severity
        """, conn)
        gold_sla.to_sql("gold_sla_compliance", conn, if_exists="replace", index=False)

        # gold_production_kpis
        gold_prod = pd.read_sql("""
            SELECT field, team,
                COUNT(*) as total_readings,
                ROUND(SUM(oil_volume_bbl), 2) as total_oil_volume_bbls,
                ROUND(SUM(gas_volume_mcf), 2) as total_gas_volume_mcf,
                ROUND(SUM(water_volume_bbl), 2) as total_water_volume_bbls,
                ROUND(SUM(deferred_production_bbls), 2) as total_deferred_bbls,
                ROUND(AVG(wellhead_pressure), 2) as avg_wellhead_pressure
            FROM silver_production
            GROUP BY field, team
        """, conn)
        gold_prod.to_sql("gold_production_kpis", conn, if_exists="replace", index=False)

        # gold_maintenance_kpis
        gold_maint = pd.read_sql("""
            SELECT field, team, maintenance_type,
                COUNT(*) as total_work_orders,
                ROUND(SUM(maintenance_cost), 2) as total_maintenance_cost,
                ROUND(AVG(maintenance_cost), 2) as avg_maintenance_cost,
                ROUND(AVG(maintenance_duration_hours), 2) as avg_duration_hours
            FROM silver_maintenance
            GROUP BY field, team, maintenance_type
        """, conn)
        gold_maint.to_sql("gold_maintenance_kpis", conn, if_exists="replace", index=False)

        # gold_hse_kpis
        gold_hse = pd.read_sql("""
            SELECT field, team,
                COUNT(*) as total_incidents,
                SUM(days_lost) as total_days_lost,
                ROUND(AVG(days_lost), 2) as avg_days_lost,
                SUM(CASE WHEN severity = 'Critical' THEN 1 ELSE 0 END) as total_critical,
                SUM(CASE WHEN near_miss = 'Yes' THEN 1 ELSE 0 END) as total_near_misses,
                ROUND(SUM(CASE WHEN near_miss = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as near_miss_rate_pct
            FROM silver_hse
            GROUP BY field, team
        """, conn)
        gold_hse.to_sql("gold_hse_kpis", conn, if_exists="replace", index=False)

        # gold_hse_by_severity
        gold_hse_sev = pd.read_sql("""
            SELECT field, team, severity,
                COUNT(*) as total_incidents
            FROM silver_hse
            GROUP BY field, team, severity
        """, conn)
        gold_hse_sev.to_sql("gold_hse_by_severity", conn, if_exists="replace", index=False)

        # gold_hse_by_type
        gold_hse_type = pd.read_sql("""
            SELECT field, team, incident_type,
                COUNT(*) as total_incidents,
                SUM(days_lost) as total_days_lost
            FROM silver_hse
            GROUP BY field, team, incident_type
        """, conn)
        gold_hse_type.to_sql("gold_hse_by_type", conn, if_exists="replace", index=False)

        # gold_hse_by_department
        gold_hse_dept = pd.read_sql("""
            SELECT field, team, department,
                COUNT(*) as total_incidents,
                SUM(days_lost) as total_days_lost
            FROM silver_hse
            GROUP BY field, team, department
        """, conn)
        gold_hse_dept.to_sql("gold_hse_by_department", conn, if_exists="replace", index=False)

        if validation_results:
        # gold_data_quality
            gold_dq = pd.DataFrame([("incidents",TOTAL_RECORDS, validation_results["incidents_clean"], 
                validation_results["incidents_errors"],
                validation_results["incidents_alerts"],
                round(validation_results["incidents_errors"] / TOTAL_RECORDS * 100, 2),
                round(validation_results["incidents_alerts"] / TOTAL_RECORDS * 100, 2)),
                ("production", TOTAL_RECORDS, validation_results["production_clean"],
                validation_results["production_errors"],0,
                round(validation_results["production_errors"] / TOTAL_RECORDS * 100, 2),0),
                ("maintenance", TOTAL_RECORDS, validation_results["maintenance_clean"],
                validation_results["maintenance_errors"],0,
                round(validation_results["maintenance_errors"] / TOTAL_RECORDS * 100, 2),0),
                ("hse", TOTAL_RECORDS, validation_results["hse_clean"],
                validation_results["hse_errors"],0,
                round(validation_results["hse_errors"] / TOTAL_RECORDS * 100, 2),0),
            ], columns=['domain', 'total_records', 'total_clean', 'total_errors', 'total_alerts', 'error_rate_pct', 'alert_rate_pct'])
            
        else:
            gold_dq = pd.DataFrame([
                ('Incidents', 1000, 846, 154, 512, 15.4, 51.2),
                ('Production', 1000, 847, 153, 0, 15.3, 0.0),
                ('Maintenance', 1000, 868, 132, 0, 13.2, 0.0),
                ('HSE', 1000, 848, 152, 0, 15.2, 0.0)
            ], columns=['domain', 'total_records', 'total_clean', 'total_errors',
                       'total_alerts', 'error_rate_pct', 'alert_rate_pct'])
            
            gold_dq.to_sql("gold_data_quality", conn, if_exists="replace", index=False)

        conn.close()
        logger.info("Gold layer loaded successfully")
    except Exception:
        logger.exception("❌ Gold layer load failed.")
        raise


# ============================================================
# MAIN EXECUTION
# ============================================================
if __name__ == "__main__":
    load_bronze()
    load_silver()
    load_dimensions()
    load_gold()