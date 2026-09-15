"""Entity resolution and synonym mapping for EduPulse AI semantic graph."""

import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

DISTRICT_NAMES = [
    "Amritsar",
    "Bathinda",
    "Ferozepur",
    "Jalandhar",
    "Ludhiana",
    "Moga",
    "Patiala",
    "Sangrur",
    "Unknown",
]

AMENITY_SYNONYMS: Dict[str, str] = {
    "electricity": "electricity",
    "power": "electricity",
    "electric": "electricity",
    "bijli": "electricity",
    "drinking water": "drinking_water",
    "water": "drinking_water",
    "clean water": "drinking_water",
    "pani": "drinking_water",
    "toilet": "functional_toilet",
    "sanitation": "functional_toilet",
    "washroom": "functional_toilet",
    "functional toilet": "functional_toilet",
    "shauchalaya": "functional_toilet",
    "boundary": "boundary_wall",
    "boundary wall": "boundary_wall",
    "fence": "boundary_wall",
    "wall": "boundary_wall",
    "diwar": "boundary_wall",
    "playground": "playground",
    "play area": "playground",
    "sports ground": "playground",
    "khel": "playground",
    "maidan": "playground",
}

WELFARE_QUADRANTS: Dict[str, str] = {
    "model": "MODEL",
    "resilient": "RESILIENT",
    "academic intervention": "ACADEMIC INTERVENTION",
    "academic deficit": "ACADEMIC INTERVENTION",
    "critical intervention": "CRITICAL INTERVENTION",
    "critical": "CRITICAL INTERVENTION",
    "critical quadrant": "CRITICAL INTERVENTION",
}

COMMODITIES: Dict[str, str] = {
    "wheat": "Wheat",
    "rice": "Rice",
    "pulses": "Pulses",
    "dal": "Pulses",
    "cooking oil": "Cooking Oil",
    "oil": "Cooking Oil",
    "kharcha": "total_spend_inr",
}

DRIVER_SYNONYMS: Dict[str, str] = {
    "infrastructure": "INFRASTRUCTURE",
    "infra": "INFRASTRUCTURE",
    "amenity": "INFRASTRUCTURE",
    "academic": "ACADEMIC",
    "fln": "ACADEMIC",
    "learning": "ACADEMIC",
    "attendance": "ATTENDANCE",
    "absence": "ATTENDANCE",
    "truancy": "ATTENDANCE",
    "multi-factor": "MULTI_FACTOR",
    "multifactor": "MULTI_FACTOR",
}


class ResolvedEntities(BaseModel):
    """Container for entities extracted from an administrator query."""

    school_ids: List[str] = Field(default_factory=list)
    districts: List[str] = Field(default_factory=list)
    amenities: List[str] = Field(default_factory=list)
    missing_amenities: List[str] = Field(default_factory=list)
    quadrants: List[str] = Field(default_factory=list)
    commodities: List[str] = Field(default_factory=list)
    drivers: List[str] = Field(default_factory=list)
    limit: Optional[int] = None
    time_window_days: Optional[int] = None
    raw_entities: Dict[str, Any] = Field(default_factory=dict)


def normalize_school_id(raw_id: str) -> str:
    """Normalize user input school ID to canonical format SCH0000."""
    cleaned = raw_id.upper().strip().replace("-", "").replace("_", "").replace(" ", "")
    # Match SCH followed by numbers
    match = re.search(r"SCH(\d+)", cleaned)
    if match:
        num = int(match.group(1))
        return f"SCH{num:04d}"
    return raw_id.upper()


def resolve_entities(query: str) -> ResolvedEntities:
    """Extract and normalize all domain entities mentioned in natural language query."""
    q_lower = query.lower()
    resolved = ResolvedEntities()

    # 1. School ID pattern matching (e.g. SCH0386, sch_0126, SCH 180)
    school_matches = re.findall(r"\b(SCH[\s_-]?\d+)\b", query, re.IGNORECASE)
    for sm in school_matches:
        norm = normalize_school_id(sm)
        if norm not in resolved.school_ids:
            resolved.school_ids.append(norm)

    # 2. District name matching
    for dist in DISTRICT_NAMES:
        pattern = r"\b" + re.escape(dist.lower()) + r"\b"
        if re.search(pattern, q_lower):
            if dist not in resolved.districts:
                resolved.districts.append(dist)

    # 3. Amenity matching & negation detection
    is_negated_query = any(
        neg in q_lower
        for neg in [
            "no ", "without", "missing", "lack", "deficit", "absent",
            "nahi", "bina", "lacking", "unverified", "deprived", "kahan nahi"
        ]
    )
    for phrase, canonical in AMENITY_SYNONYMS.items():
        pattern = r"\b" + re.escape(phrase) + r"\b"
        if re.search(pattern, q_lower):
            if is_negated_query:
                if canonical not in resolved.missing_amenities:
                    resolved.missing_amenities.append(canonical)
            else:
                if canonical not in resolved.amenities:
                    resolved.amenities.append(canonical)

    # 4. Welfare Quadrant matching
    for phrase, quad in WELFARE_QUADRANTS.items():
        pattern = r"\b" + re.escape(phrase) + r"\b"
        if re.search(pattern, q_lower):
            if quad not in resolved.quadrants:
                resolved.quadrants.append(quad)

    # 5. Commodity matching
    for phrase, comm in COMMODITIES.items():
        pattern = r"\b" + re.escape(phrase) + r"\b"
        if re.search(pattern, q_lower):
            if comm not in resolved.commodities:
                resolved.commodities.append(comm)

    # 6. Driver matching (only when query specifically asks about drivers or causes)
    if any(w in q_lower for w in ["driver", "driven by", "due to", "cause", "reason"]):
        for phrase, driver in DRIVER_SYNONYMS.items():
            pattern = r"\b" + re.escape(phrase) + r"\b"
            if re.search(pattern, q_lower):
                if driver not in resolved.drivers:
                    resolved.drivers.append(driver)

    # 7. Numerical limit / top N extraction
    limit_match = re.search(r"\b(?:top|first|highest|lowest|bottom)\s+(\d+)\b", q_lower)
    if limit_match:
        resolved.limit = min(int(limit_match.group(1)), 100)
    elif "top" in q_lower or "rank" in q_lower:
        resolved.limit = 10

    # 8. Time range extraction (e.g. 30 days, past month)
    if "30 day" in q_lower or "month" in q_lower:
        resolved.time_window_days = 30
    elif "90 day" in q_lower or "quarter" in q_lower:
        resolved.time_window_days = 90

    return resolved
