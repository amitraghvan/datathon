"""CSV loaders for raw school master, student attendance, and school infrastructure datasets."""

import pandas as pd
from src.config import (
    FILE_SCHOOL_MASTER,
    FILE_ATTENDANCE,
    FILE_INFRASTRUCTURE,
    get_raw_filepath,
    logger,
)

def load_school_master() -> pd.DataFrame:
    """Load pristine raw school master data."""
    fp = get_raw_filepath(FILE_SCHOOL_MASTER)
    logger.info("Loading raw school master from %s", fp)
    df = pd.read_csv(fp)
    logger.info("Loaded school master: %d rows, %d columns", len(df), len(df.columns))
    return df

def load_attendance() -> pd.DataFrame:
    """Load pristine raw student attendance records."""
    fp = get_raw_filepath(FILE_ATTENDANCE)
    logger.info("Loading raw student attendance from %s", fp)
    df = pd.read_csv(fp)
    logger.info("Loaded student attendance: %d rows, %d columns", len(df), len(df.columns))
    return df

def load_infrastructure() -> pd.DataFrame:
    """Load pristine raw school infrastructure inspection records."""
    fp = get_raw_filepath(FILE_INFRASTRUCTURE)
    logger.info("Loading raw school infrastructure from %s", fp)
    df = pd.read_csv(fp)
    logger.info("Loaded school infrastructure: %d rows, %d columns", len(df), len(df.columns))
    return df
