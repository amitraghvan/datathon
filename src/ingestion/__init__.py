"""Raw data ingestion modules."""

from .csv_loader import load_attendance, load_infrastructure, load_school_master
from .excel_loader import load_mdm_procurement
from .json_loader import load_test_scores

__all__ = [
    "load_school_master",
    "load_attendance",
    "load_infrastructure",
    "load_mdm_procurement",
    "load_test_scores",
]
