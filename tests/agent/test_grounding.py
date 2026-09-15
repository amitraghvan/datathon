"""Unit tests for Anti-Hallucination Grounding and Causal Auditing."""

from src.agent.grounding.validator import validate_grounding


def test_grounding_validates_known_evidence():
    """Ensure narrative containing numbers present in evidence passes verification."""
    records = [
        {"district": "Jalandhar", "avg_attendance_rate": 79.1, "avg_academic_score": 66.6},
        {"district": "Ludhiana", "avg_attendance_rate": 79.2, "avg_academic_score": 66.2},
    ]
    narrative = (
        "Jalandhar recorded an average attendance rate of 79.1% and an academic score of 66.6%. "
        "Ludhiana reported an attendance rate of 79.2%."
    )
    report = validate_grounding(narrative, records, is_observational=False)
    assert report.is_grounded is True
    assert len(report.unverified_numbers) == 0


def test_grounding_flags_unverified_numbers():
    """Ensure fabricated numbers not present in records or allowed constants are flagged."""
    records = [
        {"school_id": "SCH0001", "attendance_rate_pct": 72.4},
    ]
    narrative = "SCH0001 has an attendance rate of 72.4% with a fabricated test score of 93.7%."
    report = validate_grounding(narrative, records, is_observational=False)
    assert report.is_grounded is False
    assert 93.7 in report.unverified_numbers


def test_grounding_flags_causal_violations():
    """Ensure causal phrasing in observational context is strictly flagged."""
    records = [
        {"school_id": "SCH0001", "attendance_rate_pct": 72.4, "academic_score": 55.0},
    ]
    causal_narrative = "Higher student attendance directly causes higher test scores across all schools."
    report = validate_grounding(causal_narrative, records, is_observational=True)
    assert report.is_grounded is False
    assert len(report.causal_violations) > 0
