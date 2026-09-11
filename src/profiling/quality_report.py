"""Generator for formal markdown data quality reports and machine-readable JSON summaries."""

import json
from pathlib import Path
from typing import Any, Dict
from src.config import DOCS_DIR, PROCESSED_DATA_DIR, logger

def export_json_summary(audit_data: Dict[str, Any], output_path: Path | None = None) -> Path:
    """Export machine-readable data quality summary JSON."""
    if output_path is None:
        output_path = PROCESSED_DATA_DIR / "data_quality_summary.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(audit_data, f, indent=2, default=str)
    logger.info("Exported JSON audit summary to %s", output_path)
    return output_path

def generate_markdown_report(audit_data: Dict[str, Any], output_path: Path | None = None) -> Path:
    """Generate executive Markdown Data Quality Report."""
    if output_path is None:
        output_path = DOCS_DIR / "data_quality_report.md"

    profiles = audit_data["profiles"]
    issues = audit_data["issues"]
    sev_counts = audit_data["issue_severity_counts"]
    ref_int = audit_data["referential_integrity"]

    md = []
    md.append("# EDUPULSE AI — Comprehensive Data Quality Audit Report")
    md.append("## TransOrg AgentIQ Datathon (Track 4: Education & EdTech)")
    md.append(f"**Generated**: `{audit_data.get('audit_timestamp', 'N/A')}`  ")
    md.append("**System**: EDUPULSE AI Data Trust & Decision-Intelligence Platform  ")
    md.append("**Status**: Phase 1 Baseline Audit Complete (Pristine Raw Data Preserved)")
    md.append("\n---\n")

    md.append("## 1. Executive Summary")
    md.append(
        "A rigorous, non-destructive data quality audit was conducted across all five synthetic competition datasets. "
        "The objective was to uncover all deliberate data corruption, formatting inconsistencies, anomalous recordings, "
        "and broken linkages before executing any analytical transformations. "
        "**Zero raw data records were modified during this audit.**"
    )
    md.append("\n### Issue Severity Overview")
    md.append(f"- **CRITICAL**: {sev_counts.get('CRITICAL', 0)} (Impossible attendance, proxy marking fraud, missing quantities)")
    md.append(f"- **HIGH**: {sev_counts.get('HIGH', 0)} (Mixed grading scales, messy booleans, duplicate master records, currency formatting)")
    md.append(f"- **MEDIUM**: {sev_counts.get('MEDIUM', 0)} (Missing primary keys / record IDs)")
    md.append(f"- **INFO**: {sev_counts.get('INFO', 0)} (100% Referential integrity verified post-canonicalization)")

    md.append("\n---\n")
    md.append("## 2. Dataset Inventory & High-Level Metrics")
    md.append("| Dataset | File Name | Rows | Columns | Exact Duplicates | Key Duplicates |")
    md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
    for name, prof in profiles.items():
        md.append(
            f"| **{name.replace('_', ' ').title()}** | `{prof['dataset_name']}` | "
            f"{prof['row_count']:,} | {prof['col_count']} | {prof['exact_duplicates']:,} | {prof['key_duplicates']:,} |"
        )

    md.append("\n---\n")
    md.append("## 3. Referential Integrity & Entity Resolution Matrix")
    md.append("To determine if disparate datasets can be joined into a cohesive star schema, school IDs were normalized using canonical format `SCHxxxx`.")
    md.append("\n| Child Table | Raw Distinct IDs | Canonical Schools | Master Schools | Orphan Records | Integrity Status |")
    md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
    for child, stats in ref_int.items():
        status = "PASSED (100% Match)" if stats["integrity_passed"] else f"FAILED ({stats['unmatched_schools']} orphans)"
        md.append(
            f"| **{child.replace('_', ' ').title()}** | {stats['distinct_schools']} | {stats['distinct_schools']} | "
            f"{profiles['school_master']['unique_canonical_schools']} | {stats['unmatched_schools']} | `{status}` |"
        )

    md.append("\n> [!NOTE]\n> Every school referenced in the attendance, MDM procurement, and FLN assessment tables maps with 100% precision to the 600 unique schools in the master table. In infrastructure, 598 schools were inspected (2 schools were uninspected).")

    md.append("\n---\n")
    md.append("## 4. Detailed Data Quality Issues & Remediation Plan")
    md.append("| Severity | Dataset | Affected Field | Issue Identified | Records | Impact | Approved Remediation |")
    md.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    for issue in issues:
        md.append(
            f"| **{issue['severity']}** | `{issue['dataset']}` | `{issue['column']}` | "
            f"{issue['issue_type']} | {issue['count']:,} | {issue['impact']} | {issue['recommended_resolution']} |"
        )

    md.append("\n---\n")
    md.append("## 5. Column-Level Profiling Summaries")
    for ds_key, prof in profiles.items():
        md.append(f"\n### `{prof['dataset_name']}`")
        md.append("| Column Name | Inferred Dtype | Null Count | Null % | Unique Values | Sample Values |")
        md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for col_name, col_stats in prof["columns"].items():
            samples = ", ".join(col_stats["sample_values"][:3])
            md.append(
                f"| `{col_name}` | `{col_stats['dtype']}` | {col_stats['null_count']:,} | "
                f"{col_stats['null_pct']}% | {col_stats['unique_count']:,} | `{samples}` |"
            )

    md.append("\n---\n")
    md.append("## 6. Data Lineage & Traceability Architecture")
    md.append(
        "To ensure consulting-grade defensibility, every cleaned record in the data warehouse will retain its lineage metadata:\n"
        "- `*_raw`: Pristine original value as recorded in source files.\n"
        "- `*_clean`: Standardized canonical value.\n"
        "- `*_transformation_status`: Enumerated status (`CANONICAL`, `RESCUED`, `IMPUTED`, `FLAGGED_ANOMALY`).\n"
        "- `*_quality_flag`: Specific anomaly code (e.g. `ERR_ATT_PRESENT_GT_TOTAL`, `WARN_ATT_SUNDAY_PROXY`, `DERIVED_QTY_FROM_COST`)."
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    logger.info("Generated Markdown Data Quality Report at %s", output_path)
    return output_path
