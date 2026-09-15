"""Unit tests for boolean normalization."""

import pytest

from src.cleaning.booleans import normalize_boolean


@pytest.mark.parametrize(
    "raw_val, expected_clean",
    [
        ("True", "TRUE"),
        ("true", "TRUE"),
        (True, "TRUE"),
        ("1", "TRUE"),
        (1, "TRUE"),
        ("yes", "TRUE"),
        ("Yes", "TRUE"),
        ("Y", "TRUE"),
        ("hai", "TRUE"),
        ("Haan", "TRUE"),
        ("haan", "TRUE"),
        ("H", "TRUE"),
        ("functional", "TRUE"),
        ("Functional", "TRUE"),
        ("working", "TRUE"),
        ("Working", "TRUE"),
        ("available", "TRUE"),
        ("Available", "TRUE"),
    ],
)
def test_boolean_true_tokens(raw_val, expected_clean):
    clean, status, flag = normalize_boolean(raw_val)
    assert clean == expected_clean
    assert "TRUE" in status


@pytest.mark.parametrize(
    "raw_val, expected_clean",
    [
        ("False", "FALSE"),
        ("false", "FALSE"),
        (False, "FALSE"),
        ("0", "FALSE"),
        (0, "FALSE"),
        ("no", "FALSE"),
        ("No", "FALSE"),
        ("N", "FALSE"),
        ("nahi", "FALSE"),
        ("Nahi", "FALSE"),
        ("nahi hai", "FALSE"),
        ("Nahi hai", "FALSE"),
        ("na", "FALSE"),
        ("kharab", "FALSE"),
        ("Kharab", "FALSE"),
        ("broken", "FALSE"),
        ("Broken", "FALSE"),
        ("under repair", "FALSE"),
        ("Under Repair", "FALSE"),
        ("not available", "FALSE"),
        ("Not Available", "FALSE"),
    ],
)
def test_boolean_false_tokens(raw_val, expected_clean):
    clean, status, flag = normalize_boolean(raw_val)
    assert clean == expected_clean
    assert "FALSE" in status


@pytest.mark.parametrize(
    "raw_val",
    [None, "", "   ", float("nan"), "random_unrecognized_word"],
)
def test_boolean_unknown_preservation(raw_val):
    clean, status, flag = normalize_boolean(raw_val)
    assert clean == "UNKNOWN"
    assert clean != "FALSE"  # Crucial rule: UNKNOWN is never conflated with FALSE
