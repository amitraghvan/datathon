"""JSON loader for raw standardized test scores dataset."""

import json
import pandas as pd
from src.config import FILE_TEST_SCORES, get_raw_filepath, logger

def load_test_scores() -> pd.DataFrame:
    """Load pristine raw standardized test scores records from JSON."""
    fp = get_raw_filepath(FILE_TEST_SCORES)
    logger.info("Loading raw test scores from %s", fp)
    with open(fp, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    logger.info("Loaded test scores: %d records, %d columns", len(df), len(df.columns))
    return df
