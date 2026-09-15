"""Unit tests for school segmentation and K-Means clustering."""

from src.analytics.segmentation import perform_school_segmentation


def test_perform_school_segmentation():
    df_seg, eval_report = perform_school_segmentation(k_clusters=4, random_state=42)
    assert len(df_seg) == 600
    assert "cluster_name" in df_seg.columns
    assert "cluster_recommended_action" in df_seg.columns

    # Check 4 unique clusters
    assert df_seg["cluster_id"].nunique() == 4

    # Verify silhouette score is valid
    assert -1.0 <= eval_report["silhouette_score"] <= 1.0

    # Verify K candidate evaluations (K=2 through 6)
    assert set(eval_report["k_candidates_silhouette"].keys()) == {2, 3, 4, 5, 6}

    # Verify cluster profiles are interpretable and not generic cluster IDs
    for cid, prof in eval_report["cluster_profiles"].items():
        assert "Cluster" not in prof["cluster_name"]
        assert len(prof["description"]) > 10
        assert len(prof["recommended_policy_action"]) > 10

    # Test determinism: running with same seed yields exact same cluster assignments
    df_seg2, _ = perform_school_segmentation(k_clusters=4, random_state=42)
    assert (df_seg["cluster_id"] == df_seg2["cluster_id"]).all()
