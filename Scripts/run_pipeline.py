# ============================================================
# OIL & GAS OPERATIONS - PIPELINE AUTOMATION
# run_pipeline.py
# Runs the entire pipeline end to end in one command:
# generate -> validate -> load database
# ============================================================
import os
import time
import csv
from datetime import datetime
from config.logger import logger
from Scripts.generate_daily_data import(
    generate_incidents,
    generate_production,
    generate_maintenance,
    generate_hse    
)
from Scripts.validation_pipeline import(
    validate_incidents,
    validate_production,
    validate_maintenance,
    validate_hse
)
from Scripts.load_database import(
    load_bronze,
    load_silver,
    load_dimensions,
    load_gold
)

def save_metrics(duration, validation_results, phase1_time, phase2_time, phase3_time):
    metrics_path = "monitoring/pipeline_metrics.csv"
    os.makedirs("monitoring", exist_ok=True)
    
    file_exists = os.path.exists(metrics_path)
    
    with open(metrics_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "date", "runtime_seconds","status",
            "phase1_time", "phase2_time", "phase3_time",
            "incidents_clean", "incidents_errors", "incidents_alerts",
            "production_clean", "production_errors",
            "maintenance_clean", "maintenance_errors",
            "hse_clean", "hse_errors"
        ])
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "runtime_seconds": duration,
            "phase1_time": phase1_time,
            "phase2_time": phase2_time,
            "phase3_time": phase3_time,
            **validation_results
        })
    
    logger.info(f"Monitoring metrics saved to {metrics_path}")

# ============================================================
# MAIN PIPELINE
# ============================================================
def save_pipeline_status(status,runtime):
    status_path = "monitoring/pipeline_status.csv"

    os.makedirs("monitoring", exist_ok=True)

    file_exists = os.path.exists(status_path)

    with open(status_path, "a", newline="") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "date",
                "status",
                "runtime_seconds"
            ]
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": status,
            "runtime_seconds": runtime
        })
    logger.info(f"Pipeline status saved to {status_path}")

def run_pipeline():
    start_time = time.time()

    try: 
        logger.info("="*50)
        logger.info(f"PIPELINE STARTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*50)

        phase1_start = time.time()  
        logger.info("PHASE 1: Generating data...")
        generate_incidents()
        generate_production()
        generate_maintenance()
        generate_hse()
        phase1_time = round(time.time() - phase1_start, 2)
        logger.info(f"✅ Phase 1 complete in {phase1_time} seconds - data generated")

        phase2_start = time.time()
        logger.info("PHASE 2: Validating data...")
        incident_results = validate_incidents()
        production_results = validate_production()
        maintenance_results =  validate_maintenance()
        hse_results = validate_hse()
        phase2_time = round(time.time() - phase2_start, 2)
    

        validation_results = {
        "incidents_clean": incident_results["incidents_clean"],
        "incidents_errors": incident_results["incidents_errors"],
        "incidents_alerts": incident_results["incidents_alerts"],

        "production_clean": production_results["production_clean"],
        "production_errors": production_results["production_errors"],

        "maintenance_clean": maintenance_results["maintenance_clean"],
        "maintenance_errors": maintenance_results["maintenance_errors"],

        "hse_clean": hse_results["hse_clean"],
        "hse_errors": hse_results["hse_errors"]
        }

        logger.info(f"✅ Phase 2 complete in {phase2_time} seconds - data validated")

        phase3_start = time.time()
        logger.info("PHASE 3: Loading to database...")
        load_bronze()
        load_silver()
        load_dimensions()
        load_gold(validation_results)
        phase3_time = round(time.time() - phase3_start, 2)
        logger.info(f"✅ Phase 3 complete in {phase3_time} seconds - database loaded")

        end_time = time.time()
        duration = round(end_time - start_time, 2)
        save_metrics(duration, validation_results, phase1_time, phase2_time, phase3_time)
        save_pipeline_status("SUCCESS", duration)

        logger.info("="*50)
        logger.info("✅ PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info(f"⏱️  Total runtime: {duration} seconds")
        logger.info(f"🕐 Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*50)

    except Exception as e:
        duration = round(time.time() - start_time, 2)
        save_pipeline_status("FAILURE", duration)
        logger.exception(f"❌ Pipeline failed: {str(e)}")
        raise

# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    run_pipeline()
  
    