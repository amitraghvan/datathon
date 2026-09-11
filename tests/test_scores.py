"""Unit tests for academic score normalization and subject standardization."""

from src.cleaning.scores import (
    normalize_academic_score,
    standardize_subject,
)


def test_percentage_scales():
    s1, m1, _, lg1 = normalize_academic_score("73.0%", "Percentage")
    assert s1 == 73.0
    assert m1 == "PERCENTAGE_DIRECT"
    assert lg1 is False

    s2, m2, _, _ = normalize_academic_score("63.4%", "pct")
    assert s2 == 63.4

    s3, m3, _, _ = normalize_academic_score("89.3%", "%")
    assert s3 == 89.3

def test_cgpa_scale():
    s1, m1, _, lg1 = normalize_academic_score("7.7", "CGPA", 10)
    assert s1 == 77.0
    assert m1 == "CGPA_TO_PERCENT"
    assert lg1 is False

    s2, _, _, _ = normalize_academic_score("4.8", "CGPA", 10)
    assert s2 == 48.0

def test_raw_marks_scale():
    s1, m1, _, lg1 = normalize_academic_score("21.6/50", "Raw Marks")
    assert s1 == 43.2
    assert m1 == "RAW_MARKS_TO_PERCENT"
    assert lg1 is False

    s2, _, _, _ = normalize_academic_score("16.0/25", "Raw Marks")
    assert s2 == 64.0

def test_letter_grade_proxy():
    grades = {"A+": 95.0, "A": 85.0, "B": 75.0, "C": 65.0, "D": 50.0, "E": 35.0}
    for g, exp in grades.items():
        s, m, _, is_lg = normalize_academic_score(g, "Letter Grade")
        assert s == exp
        assert m == "LETTER_GRADE_PROXY"
        assert is_lg is True

def test_subject_standardization():
    assert standardize_subject("Ganit")[0] == "Mathematics"
    assert standardize_subject("Math")[0] == "Mathematics"
    assert standardize_subject("Mathematics")[0] == "Mathematics"
    assert standardize_subject("Science")[0] == "Science"
    assert standardize_subject("English")[0] == "English"
    assert standardize_subject("Hindi")[0] == "Hindi"
    assert standardize_subject("Punjabi")[0] == "Punjabi"
    assert standardize_subject("EVS")[0] == "Environmental Studies"
