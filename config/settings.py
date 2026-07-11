# ============================================================
# SETTINGS.PY
# Reads config.yaml and .env file
# Makes settings available to all scripts
# ============================================================

import yaml
import os
from dotenv import load_dotenv

# Load .env file first
load_dotenv()

# Get the path to config.yaml
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")

# Read the config file
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

# Paths — read from .env first, fallback to config.yaml
PATHS = {
    "raw": os.getenv("RAW_PATH", config["paths"]["raw"]),
    "clean": os.getenv("CLEAN_PATH", config["paths"]["clean"]),
    "errors": os.getenv("ERRORS_PATH", config["paths"]["errors"]),
    "alerts": os.getenv("ALERTS_PATH", config["paths"]["alerts"]),
    "database": os.getenv("DATABASE_PATH", config["paths"]["database"]),
}

# Generation settings
GENERATION = {
    "num_records": int(os.getenv("NUM_RECORDS", config["generation"]["num_records"])),
    "dirty_percentage": float(os.getenv("DIRTY_PERCENTAGE", config["generation"]["dirty_percentage"]))
}

# SLA rules stay in config.yaml — not sensitive
SLA_RULES = config["sla_rules"]
