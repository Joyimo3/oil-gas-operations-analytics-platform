# ============================================================
# OIL & GAS OPERATIONS - AIRFLOW DAG
# orchestration/dag_pipeline.py
#
# NOTE: This DAG is designed for Apache Airflow deployment.
# It cannot be executed locally without an Airflow environment.
# The pipeline logic is implemented in Scripts/run_pipeline.py
# for local execution.
# ============================================================

from datetime import datetime, timedelta

# Airflow imports — available in Airflow environment
try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
    from airflow.utils.dates import days_ago
    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False
    print("Airflow not installed — DAG definition only, not executable locally")

# ============================================================
# DEFAULT ARGUMENTS
# Applied to every task in the DAG
# ============================================================
default_args = {
    "owner": "joy_imo",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# ============================================================
# DAG DEFINITION
# Runs daily at 6am — simulates real production pipeline
# ============================================================
if AIRFLOW_AVAILABLE:
    dag = DAG(
        dag_id="oil_gas_pipeline",
        description="Daily Oil & Gas Operations ETL Pipeline",
        default_args=default_args,
        schedule_interval="0 6 * * *",  # runs every day at 6am
        start_date=days_ago(1),
        catchup=False,
        tags=["oil_gas", "etl", "production"]
    )

    # ============================================================
    # TASK DEFINITIONS
    # ============================================================

    def task_generate_data():
        from Scripts.generate_daily_data import (
            generate_incidents, generate_production,
            generate_maintenance, generate_hse
        )
        generate_incidents()
        generate_production()
        generate_maintenance()
        generate_hse()

    def task_validate_data():
        from Scripts.validation_pipeline import (
            validate_incidents, validate_production,
            validate_maintenance, validate_hse
        )
        validate_incidents()
        validate_production()
        validate_maintenance()
        validate_hse()

    def task_load_bronze():
        from Scripts.load_database import load_bronze
        load_bronze()

    def task_load_silver():
        from Scripts.load_database import load_silver
        load_silver()

    def task_load_dimensions():
        from Scripts.load_database import load_dimensions
        load_dimensions()

    def task_load_gold():
        from Scripts.load_database import load_gold
        load_gold()

    # ============================================================
    # AIRFLOW TASK OPERATORS
    # ============================================================

    generate = PythonOperator(
        task_id="generate_data",
        python_callable=task_generate_data,
        dag=dag
    )

    validate = PythonOperator(
        task_id="validate_data",
        python_callable=task_validate_data,
        dag=dag
    )

    load_bronze_task = PythonOperator(
        task_id="load_bronze",
        python_callable=task_load_bronze,
        dag=dag
    )

    load_silver_task = PythonOperator(
        task_id="load_silver",
        python_callable=task_load_silver,
        dag=dag
    )

    load_dimensions_task = PythonOperator(
        task_id="load_dimensions",
        python_callable=task_load_dimensions,
        dag=dag
    )

    load_gold_task = PythonOperator(
        task_id="load_gold",
        python_callable=task_load_gold,
        dag=dag
    )

    # ============================================================
    # TASK DEPENDENCIES
    # Defines the order tasks run in
    # This is the DAG structure — Directed Acyclic Graph
    # ============================================================

    generate >> validate >> load_bronze_task >> load_silver_task >> load_dimensions_task >> load_gold_task