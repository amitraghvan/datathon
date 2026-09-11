"""Bootstrap smoke tests verifying configuration, environment, and raw file availability."""

import pytest
from src.config import (
    FILE_SCHOOL_MASTER,
    FILE_ATTENDANCE,
    FILE_INFRASTRUCTURE,
    FILE_MDM,
    FILE_TEST_SCORES,
    get_raw_filepath,
    BOOLEAN_TRUE_TOKENS,
    BOOLEAN_FALSE_TOKENS,
    GRAIN_UNIT_PRICES,
)

def test_source_files_exist():
    """Verify all 5 competition source files are discoverable."""
    for fn in [FILE_SCHOOL_MASTER, FILE_ATTENDANCE, FILE_INFRASTRUCTURE, FILE_MDM, FILE_TEST_SCORES]:
        fp = get_raw_filepath(fn)
        assert fp.exists(), f"File {fn} does not exist at {fp}"
        assert fp.stat().st_size > 0, f"File {fn} is empty"

def test_boolean_tokens_disjoint():
    """Ensure boolean truthy and falsy token sets are completely disjoint."""
    overlap = BOOLEAN_TRUE_TOKENS.intersection(BOOLEAN_FALSE_TOKENS)
    assert len(overlap) == 0, f"Overlapping boolean tokens: {overlap}"

def test_grain_prices_configured():
    """Verify grain prices are set for all 4 primary commodities."""
    for g in ["Wheat", "Rice", "Pulses", "Cooking Oil"]:
        assert g in GRAIN_UNIT_PRICES
        assert GRAIN_UNIT_PRICES[g] > 0
