# ============================================================
# OIL & GAS OPERATIONS - DATA EXPLORATION
# explore_data.py
# Explore raw data before validation
# ============================================================

import pandas as pd
from config.settings import PATHS

RAW_PATH = PATHS["raw"]

# ============================================================
# LOAD ALL 4 RAW DATASETS
# ============================================================

incidents = pd.read_csv(f"{RAW_PATH}incidents.csv")
production = pd.read_csv(f"{RAW_PATH}production.csv")
maintenance = pd.read_csv(f"{RAW_PATH}maintenance.csv")
hse = pd.read_csv(f"{RAW_PATH}hse.csv")

print("✅ All 4 datasets loaded successfully")
print(f"Incidents: {incidents.shape}")
print(f"Production: {production.shape}")
print(f"Maintenance: {maintenance.shape}")
print(f"HSE: {hse.shape}")

# ============================================================
# EXPLORE INCIDENTS
# ============================================================

print("\n" + "="*50)
print("INCIDENTS EXPLORATION")
print("="*50)

# first 5 rows
print("\n--- First 5 rows ---")
print(incidents.head())

# shape
print(f"\n--- Shape: {incidents.shape[0]} rows, {incidents.shape[1]} columns ---")

# column names and data types
print("\n--- Column types ---")
print(incidents.dtypes)

# missing values
print("\n--- Missing values ---")
print(incidents.isnull().sum())

# unique values in key columns
print("\n--- Unique severity values ---")
print(incidents["severity"].unique())

print("\n--- Unique status values ---")
print(incidents["status"].unique())

# negative values check
print("\n--- Negative resolution_hours ---")
print(incidents[incidents["resolution_hours"] < 0]["resolution_hours"].count())

print("\n--- Negative downtime_hours ---")
print(incidents[incidents["downtime_hours"] < 0]["downtime_hours"].count())