"""Excel loader for raw Mid-Day Meal (MDM) procurement dataset."""

import pandas as pd

from src.config import FILE_MDM, get_raw_filepath, logger


def load_mdm_procurement() -> pd.DataFrame:
    """Load pristine raw MDM procurement data, utilizing calamine engine for performance."""
    fp = get_raw_filepath(FILE_MDM)
    logger.info("Loading raw MDM procurement from %s", fp)
    try:
        df = pd.read_excel(fp, engine="calamine")
    except Exception as e:
        logger.warning("Calamine engine unavailable or failed (%s); falling back to openpyxl", e)
        df = pd.read_excel(fp, engine="openpyxl")
    logger.info("Loaded MDM procurement: %d rows, %d columns", len(df), len(df.columns))
    return df
