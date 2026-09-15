"""Analytics, risk modeling, and advanced insights package."""

from .advanced import (
    analyze_attendance_academic_association,
    calculate_welfare_gap_matrix,
    detect_procurement_outliers,
    run_letter_grade_sensitivity_analysis,
    run_risk_weight_sensitivity_analysis,
)
from .pipeline import run_phase4_analytics
from .risk import calculate_school_risk, classify_risk_level, get_recommended_intervention
from .segmentation import perform_school_segmentation

__all__ = [
    "calculate_school_risk",
    "classify_risk_level",
    "get_recommended_intervention",
    "analyze_attendance_academic_association",
    "calculate_welfare_gap_matrix",
    "run_risk_weight_sensitivity_analysis",
    "run_letter_grade_sensitivity_analysis",
    "detect_procurement_outliers",
    "perform_school_segmentation",
    "run_phase4_analytics",
]
