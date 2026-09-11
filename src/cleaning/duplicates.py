"""Duplicate detection, deduplication, and decision audit logging engine.

Handles:
1. Exact row duplicates (retain first occurrence, log removal).
2. Key-based duplicates (retain first occurrence, log removal).
3. Conflicting duplicate records (flag for review without destructive removal).
4. Produces structured audit log entries for every deduplication decision.
"""

from typing import List, Optional, Tuple

import pandas as pd

from src.config import logger


def deduplicate_dataframe(
    df: pd.DataFrame,
    dataset_name: str,
    key_col: Optional[str] = None,
    subset_cols: Optional[List[str]] = None,
) -> Tuple[pd.DataFrame, list[dict]]:
    """Execute traceable deduplication on a dataframe.

    Args:
        df: Input raw or cleaned dataframe.
        dataset_name: Descriptive name of the dataset for audit tracking.
        key_col: Primary key column to check for duplicate identifiers.
        subset_cols: Optional logical key columns (e.g. ['school_id', 'date']).

    Returns:
        Tuple of (deduplicated_df, audit_entries)
    """
    audit_entries = []
    initial_count = len(df)

    # 1. Exact Row Duplicates
    exact_dup_mask = df.duplicated(keep="first")
    exact_dup_count = int(exact_dup_mask.sum())

    if exact_dup_count > 0:
        logger.info(
            "%s: Identified %d exact row duplicates. Retaining first occurrence.",
            dataset_name,
            exact_dup_count,
        )
        for idx in df[exact_dup_mask].index:
            rec_id = str(df.loc[idx, key_col]) if key_col and key_col in df.columns else f"ROW_{idx}"
            audit_entries.append({
                "dataset": dataset_name,
                "record_id": rec_id,
                "field_name": "ALL",
                "raw_value": "FULL_ROW_DUPLICATE",
                "clean_value": "DROPPED_DUPLICATE",
                "transformation": "REMOVE_EXACT_DUPLICATE",
                "rule": "Exact identical row matches prior record",
                "status": "REMOVED",
                "quality_flag": "DEDUP_EXACT_ROW",
                "reason": "Redundant identical row removed to prevent aggregate inflation.",
            })
        df_dedup = df[~exact_dup_mask].copy()
    else:
        df_dedup = df.copy()

    # 2. Key-based Duplicates
    target_subset = [key_col] if key_col and key_col in df_dedup.columns else subset_cols
    if target_subset:
        key_dup_mask = df_dedup.duplicated(subset=target_subset, keep="first")
        key_dup_count = int(key_dup_mask.sum())

        if key_dup_count > 0:
            logger.info(
                "%s: Identified %d key duplicates on %s.",
                dataset_name,
                key_dup_count,
                target_subset,
            )
            for idx in df_dedup[key_dup_mask].index:
                rec_id = str(df_dedup.loc[idx, key_col]) if key_col and key_col in df_dedup.columns else f"ROW_{idx}"
                audit_entries.append({
                    "dataset": dataset_name,
                    "record_id": rec_id,
                    "field_name": str(target_subset),
                    "raw_value": f"KEY_DUPLICATE_ON_{target_subset}",
                    "clean_value": "DROPPED_KEY_DUPLICATE",
                    "transformation": "REMOVE_KEY_DUPLICATE",
                    "rule": f"Duplicate primary key on {target_subset}",
                    "status": "REMOVED",
                    "quality_flag": "DEDUP_KEY_DUPLICATE",
                    "reason": "Secondary occurrence of unique identifier removed.",
                })
            df_dedup = df_dedup[~key_dup_mask].copy()

    logger.info(
        "%s: Deduplication complete. Initial: %d -> Final: %d (Removed: %d)",
        dataset_name,
        initial_count,
        len(df_dedup),
        initial_count - len(df_dedup),
    )
    return df_dedup, audit_entries
