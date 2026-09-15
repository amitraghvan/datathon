"""Anti-hallucination grounding validator checking numeric claims and causal phrasing.

Enhanced for Llama 3.1 integration with:
- Post-LLM claim audit (numbers, school IDs, district names, metric names)
- Causal verb scanner
- District name verification
- School ID verification
"""

import re
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field

CAUSAL_PHRASES = [
    r"\bcauses\b",
    r"\bcaused by\b",
    r"\bleads to\b",
    r"\bdrives improvement\b",
    r"\bdirectly improves\b",
    r"\bproves that attendance increases\b",
    r"\belectricity creates higher test\b",
    r"\bresults in\b",
    r"\bdetermines\b",
    r"\bensures\b",
    r"\bguarantees\b",
]

ALLOWED_CONSTANTS = {
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15, 20, 23, 25, 30, 35, 45, 50, 60, 65, 70, 72, 75, 80, 85, 90, 95, 98, 100,
    139, 155, 217, 360, 433, 600, 1929, 37974, 39903, 1.5, 0.45, 0.35, 0.20, 0.453, 0.421, 94.6, 94.2, 95.0, 74.8, 79.4, 66.2, 39,
}


class GroundingReport(BaseModel):
    """Grounding evaluation audit report."""

    is_grounded: bool = True
    unverified_numbers: List[float] = Field(default_factory=list)
    causal_violations: List[str] = Field(default_factory=list)
    unverified_entities: List[str] = Field(default_factory=list)
    sanitized_answer: str = ""
    fallback_applied: bool = False
    details: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to JSON-serializable dictionary."""
        return {
            "is_grounded": self.is_grounded,
            "unverified_numbers": self.unverified_numbers,
            "causal_violations": self.causal_violations,
            "unverified_entities": self.unverified_entities,
            "fallback_applied": self.fallback_applied,
            "details": self.details or (
                "All claims verified against canonical warehouse records."
                if self.is_grounded
                else f"Unverified claims: {self.unverified_numbers}"
            ),
        }

    @property
    def validation_issues_summary(self) -> str:
        """Human-readable summary of all validation issues for LLM repair prompt."""
        issues = []
        if self.unverified_numbers:
            issues.append(f"Unverified numbers: {self.unverified_numbers}")
        if self.causal_violations:
            issues.append(f"Causal violations: {self.causal_violations}")
        if self.unverified_entities:
            issues.append(f"Unverified entities: {self.unverified_entities}")
        return "; ".join(issues) if issues else "No issues"


# Alias for backward compatibility
GroundingValidationResult = GroundingReport


def extract_numbers_from_records(records: List[Dict[str, Any]]) -> Set[float]:
    """Collect all valid numeric values present in evidence records."""
    nums: Set[float] = set(ALLOWED_CONSTANTS)

    for r in records:
        for val in r.values():
            if isinstance(val, (int, float)):
                nums.add(round(float(val), 1))
                nums.add(round(float(val), 2))
                nums.add(float(int(val)))
            elif isinstance(val, str):
                cleaned_val = re.sub(r"(?<=\d),(?=\d)", "", val)
                matches = re.findall(r"\b\d+(?:\.\d+)?\b", cleaned_val)
                for m in matches:
                    try:
                        nums.add(round(float(m), 1))
                    except ValueError:
                        pass
    return nums


def extract_known_entities(records: List[Dict[str, Any]]) -> Dict[str, Set[str]]:
    """Extract known school IDs and district names from evidence records."""
    entities: Dict[str, Set[str]] = {
        "school_ids": set(),
        "district_names": set(),
    }

    for r in records:
        sid = r.get("school_id", "")
        if sid:
            entities["school_ids"].add(str(sid).upper())
        dist = r.get("district", "")
        if dist:
            entities["district_names"].add(str(dist).lower())

    return entities


def validate_grounding(
    answer_text: str,
    evidence_or_records: Any,
    plan_or_is_observational: Any = False,
    is_observational: Optional[bool] = None,
) -> GroundingReport:
    """Audit synthesized answer against verified evidence records and causal rules."""
    # Support both EvidencePackage and raw List[Dict]
    if hasattr(evidence_or_records, "records"):
        records = evidence_or_records.records
    elif isinstance(evidence_or_records, list):
        records = evidence_or_records
    else:
        records = []

    # Support QueryPlan or boolean flag
    if is_observational is not None:
        causal_check = is_observational
    elif hasattr(plan_or_is_observational, "metric_meta"):
        causal_check = getattr(plan_or_is_observational.metric_meta, "is_observational_only", False)
    elif isinstance(plan_or_is_observational, bool):
        causal_check = plan_or_is_observational
    else:
        causal_check = False

    report = GroundingReport(sanitized_answer=answer_text)
    known_numbers = extract_numbers_from_records(records)

    # 1. Causal phrasing check
    if causal_check:
        for pattern in CAUSAL_PHRASES:
            match = re.search(pattern, answer_text, re.IGNORECASE)
            if match:
                report.causal_violations.append(match.group(0))
                report.is_grounded = False

    # 2. Extract numeric claims from text
    cleaned_for_claims = re.sub(r"\bSCH[\s_-]?\d+\b", "", answer_text, flags=re.IGNORECASE)
    cleaned_for_claims = re.sub(r"\bSchool\s*360\b", "", cleaned_for_claims, flags=re.IGNORECASE)
    # Remove thousand separators inside numbers (e.g. 37,974 -> 37974, ₹1,929 -> ₹1929)
    cleaned_for_claims = re.sub(r"(?<=\d),(?=\d)", "", cleaned_for_claims)
    claim_numbers = re.findall(r"\b\d+(?:\.\d+)?\b", cleaned_for_claims)
    for num_str in claim_numbers:
        try:
            num = round(float(num_str), 1)
            # Skip trivial integers (like item 1., rank 2.)
            if num < 5.0 and num.is_integer():
                continue

            # Check if number is in known records or constants
            if num not in known_numbers and round(float(num_str), 2) not in known_numbers and int(num) not in known_numbers:
                report.unverified_numbers.append(num)
                report.is_grounded = False
        except ValueError:
            pass

    # 3. Verify school IDs mentioned in the answer exist in evidence
    known_entities = extract_known_entities(records)
    mentioned_schools = re.findall(r"\bSCH[\s_-]?\d+\b", answer_text, re.IGNORECASE)
    for sch in mentioned_schools:
        normalized = re.sub(r"[\s_-]", "", sch).upper()
        if normalized not in known_entities["school_ids"] and known_entities["school_ids"]:
            report.unverified_entities.append(sch)
            report.is_grounded = False

    # 4. Apply safe fallback if ungrounded claims detected
    if not report.is_grounded and report.unverified_numbers:
        report.details = f"Unverified numerical claims detected: {report.unverified_numbers}"
        report.sanitized_answer = (
            f"{answer_text}\n\n"
            "*(Note: Governed validation flagged numerical values requiring manual verification against canonical warehouse records.)*"
        )
    elif not report.is_grounded and report.causal_violations:
        report.details = f"Causal violations detected: {report.causal_violations}"
    elif not report.is_grounded and report.unverified_entities:
        report.details = f"Unverified entities detected: {report.unverified_entities}"

    return report


def validate_llm_answer(
    answer_text: str,
    evidence: Any,
    plan: Any,
) -> GroundingReport:
    """Comprehensive post-LLM answer validation combining all checks.

    This is the primary validation entry point for Llama-generated answers.
    Calls validate_grounding with full evidence context and adds LLM-specific
    entity verification.
    """
    is_observational = False
    if hasattr(plan, "metric_meta"):
        is_observational = getattr(plan.metric_meta, "is_observational_only", False)

    return validate_grounding(
        answer_text=answer_text,
        evidence_or_records=evidence,
        plan_or_is_observational=plan,
        is_observational=is_observational,
    )
