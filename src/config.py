"""Central configuration, constants, and logging setup for EduPulse AI."""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = Path(os.getenv("DATA_RAW_DIR", DATA_DIR / "raw"))
PROCESSED_DATA_DIR = Path(os.getenv("DATA_PROCESSED_DIR", DATA_DIR / "processed"))
DOCS_DIR = BASE_DIR / "docs"
DUCKDB_PATH = Path(os.getenv("DUCKDB_PATH", PROCESSED_DATA_DIR / "edupulse.duckdb"))

# Ensure essential runtime directories exist
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("edupulse")

# ---------------------------------------------------------
# CANONICAL BUSINESS & DATA DICTIONARY CONSTANTS
# ---------------------------------------------------------

# Canonical File Names
FILE_SCHOOL_MASTER = "track4_school_master.csv"
FILE_ATTENDANCE = "track4_student_attendance.csv"
FILE_INFRASTRUCTURE = "track4_school_infrastructure.csv"
FILE_MDM = "track4_mid_day_meal_procurement.xlsx"
FILE_TEST_SCORES = "track4_test_scores.json"


def get_raw_filepath(filename: str) -> Path:
    """Resolve file path prioritizing data/raw/, falling back to workspace root."""
    raw_path = RAW_DATA_DIR / filename
    if raw_path.exists():
        return raw_path
    root_path = BASE_DIR / filename
    if root_path.exists():
        return root_path
    raise FileNotFoundError(f"Source file {filename} not found in {RAW_DATA_DIR} or {BASE_DIR}")


# Boolean Token Standardization
BOOLEAN_TRUE_TOKENS = {
    "true",
    "1",
    "yes",
    "y",
    "hai",
    "haan",
    "h",
    "functional",
    "working",
    "available",
}
BOOLEAN_FALSE_TOKENS = {
    "false",
    "0",
    "no",
    "n",
    "nahi",
    "nahi hai",
    "na",
    "kharab",
    "broken",
    "under repair",
    "not available",
}

# Grade Normalization (Roman Numerals & Strings to Integer)
GRADE_MAPPING = {
    "I": 1,
    "1": 1,
    "II": 2,
    "2": 2,
    "III": 3,
    "3": 3,
    "IV": 4,
    "4": 4,
    "V": 5,
    "5": 5,
    "VI": 6,
    "6": 6,
    "VII": 7,
    "7": 7,
    "VIII": 8,
    "8": 8,
    "IX": 9,
    "9": 9,
    "X": 10,
    "10": 10,
}

# Standardized Academic Subjects
SUBJECT_MAPPING = {
    "ganit": "Mathematics",
    "math": "Mathematics",
    "mathematics": "Mathematics",
    "science": "Science",
    "english": "English",
    "hindi": "Hindi",
    "punjabi": "Punjabi",
    "evs": "Environmental Studies",
}

# MDM Grain Types Standardization & Verified Fixed Unit Prices (₹/kg)
GRAIN_TYPE_MAPPING = {
    "sarson tel": "Cooking Oil",
    "mustard oil": "Cooking Oil",
    "cooking oil": "Cooking Oil",
    "oil": "Cooking Oil",
    "rice": "Rice",
    "chawal": "Rice",
    "pulses": "Pulses",
    "dal": "Pulses",
    "daal": "Pulses",
    "lentils": "Pulses",
    "wheat": "Wheat",
    "gehun": "Wheat",
    "atta": "Wheat",
}

GRAIN_UNIT_PRICES = {
    "Wheat": 30.0,
    "Rice": 40.0,
    "Pulses": 90.0,
    "Cooking Oil": 120.0,
}

# MDM Vendor Name Entity Resolution (12 strings -> 4 entities)
VENDOR_MAPPING = {
    "kumar & co.": "Kumar Supplies",
    "kumar general store": "Kumar Supplies",
    "kumar supplies": "Kumar Supplies",
    "singh brothers": "Singh Agro",
    "singh agro": "Singh Agro",
    "s. agro works": "Singh Agro",
    "sharma & sons": "Sharma Traders",
    "sharma traders pvt ltd": "Sharma Traders",
    "sharma traders": "Sharma Traders",
    "goyal enterprises": "Goyal Rice Mill",
    "goyal mill": "Goyal Rice Mill",
    "goyal rice mill": "Goyal Rice Mill",
}

# Letter Grade Mid-Point Analytical Proxy Mapping
LETTER_GRADE_PROXY = {
    "A+": 95.0,
    "A": 85.0,
    "B": 75.0,
    "C": 65.0,
    "D": 50.0,
    "E": 35.0,
}

# Risk Engine Weights & Thresholds
RISK_WEIGHTS = {
    "attendance": 0.45,
    "academics": 0.35,
    "infrastructure": 0.20,
}

INFRASTRUCTURE_WEIGHTS = {
    "has_functional_toilet": 0.30,
    "has_drinking_water": 0.30,
    "has_electricity": 0.20,
    "has_boundary_wall": 0.10,
    "has_playground": 0.10,
}

RISK_TIERS = {
    "LOW": (0.0, 25.0),
    "MODERATE": (25.0, 50.0),
    "HIGH": (50.0, 75.0),
    "CRITICAL": (75.0, 100.0),
}
