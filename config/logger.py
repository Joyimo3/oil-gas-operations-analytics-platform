import logging
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOG_FOLDER = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOG_FOLDER, exist_ok=True)

LOG_FILE = os.path.join(LOG_FOLDER, "pipeline.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE,encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ],
    force=True
)

logger = logging.getLogger("oil_gas_pipeline")