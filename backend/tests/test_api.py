"""Comprehensive test suite for FastAPI backend endpoints."""


def test_health_endpoints(client):
    """Verify health endpoints report connected status and trust score."""
    resp_root = client.get("/health")
    assert resp_root.status_code == 200
    data_root = resp_root.json()
    assert data_root["status"] == "healthy"
    assert data_root["warehouse_connected"] is True
    assert data_root["trust_score"] == 94.6

    resp_v1 = client.get("/api/v1/health")
    assert resp_v1.status_code == 200
    assert resp_v1.json()["warehouse_connected"] is True


def test_overview_endpoint(client):
    """Verify Executive Overview returns 6 core KPIs and dynamic alerts."""
    resp = client.get("/api/v1/overview")
    assert resp.status_code == 200
    data = resp.json()

    # Verify 6 KPIs exist
    kpis = data["kpis"]
    assert kpis["schools_monitored"]["value"] == 600
    assert kpis["average_attendance"]["unit"] == "%"
    assert kpis["average_academic_score"]["unit"] == "%"
    assert kpis["priority_schools"]["value"] >= 0
    assert kpis["infrastructure_readiness"]["unit"] == "%"
    assert kpis["data_quality_coverage"]["value"] >= 94.0

    # Verify dynamic alerts
    assert len(data["alerts"]) >= 3
    assert any(a["title"] == "Welfare Disparity Quadrant" for a in data["alerts"])

    # Verify district ranking and welfare matrix
    assert len(data["district_ranking"]) == 9
    assert len(data["welfare_matrix"]) == 600
    assert len(data["top_priorities"]) <= 10


def test_overview_filtering(client):
    """Verify Overview respects query parameter filters."""
    resp = client.get("/api/v1/overview?district=Ludhiana")
    assert resp.status_code == 200
    data = resp.json()
    assert data["kpis"]["schools_monitored"]["value"] < 600
    assert data["kpis"]["schools_monitored"]["value"] > 0


def test_districts_endpoints(client):
    """Verify District list and detail endpoints."""
    resp = client.get("/api/v1/districts")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_districts"] == 9
    assert len(data["districts"]) == 9

    # Valid district detail
    first_dist = data["districts"][0]["district"]
    resp_detail = client.get(f"/api/v1/districts/{first_dist}")
    assert resp_detail.status_code == 200
    detail = resp_detail.json()
    assert detail["summary"]["district"] == first_dist
    assert len(detail["schools"]) > 0

    # Non-existent district
    resp_bad = client.get("/api/v1/districts/NonExistentDistrictXYZ")
    assert resp_bad.status_code == 404
    assert resp_bad.json()["error"]["code"] == "DISTRICT_NOT_FOUND"


def test_schools_directory(client):
    """Verify school pagination and search."""
    resp = client.get("/api/v1/schools?page=1&page_size=10")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 600
    assert len(data["items"]) == 10
    assert data["page"] == 1
    assert data["total_pages"] == 60

    # Search
    sample_school = data["items"][0]
    resp_search = client.get(f"/api/v1/schools?search={sample_school['school_id']}")
    assert resp_search.status_code == 200
    assert resp_search.json()["total"] >= 1


def test_schools_dimensions(client):
    """Verify cascading filter dimension options."""
    resp = client.get("/api/v1/schools/dimensions")
    assert resp.status_code == 200
    dims = resp.json()
    assert len(dims["districts"]) == 9
    assert len(dims["blocks_by_district"]) == 9
    assert "MODEL" in dims["welfare_quadrants"]


def test_school_360_profile(client):
    """Verify complete School 360 profile and amenity logic."""
    # First get a valid school ID
    schools_resp = client.get("/api/v1/schools?page_size=1")
    sid = schools_resp.json()["items"][0]["school_id"]

    resp = client.get(f"/api/v1/schools/{sid}")
    assert resp.status_code == 200
    profile = resp.json()
    assert profile["school_id"] == sid
    assert "amenities" in profile
    assert profile["recommended_action"] is not None

    # Attendance timeseries
    att_resp = client.get(f"/api/v1/schools/{sid}/attendance")
    assert att_resp.status_code == 200
    assert len(att_resp.json()) > 0

    # Academics
    acad_resp = client.get(f"/api/v1/schools/{sid}/academics")
    assert acad_resp.status_code == 200
    assert len(acad_resp.json()) > 0

    # Procurement
    proc_resp = client.get(f"/api/v1/schools/{sid}/procurement")
    assert proc_resp.status_code == 200

    # 404 test
    resp_404 = client.get("/api/v1/schools/SCH9999")
    assert resp_404.status_code == 404
    assert resp_404.json()["error"]["code"] == "SCHOOL_NOT_FOUND"


def test_welfare_endpoints(client):
    """Verify welfare overview, matrix, and electricity comparison."""
    resp = client.get("/api/v1/welfare/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_schools"] == 600
    assert len(data["amenity_distributions"]) == 5
    assert len(data["electricity_comparison"]) >= 2
    assert "non_causal_disclaimer" in data

    # Matrix
    mat_resp = client.get("/api/v1/welfare/matrix")
    assert mat_resp.status_code == 200
    assert len(mat_resp.json()) == 600

    # Electricity comparison
    elec_resp = client.get("/api/v1/welfare/electricity-comparison")
    assert elec_resp.status_code == 200
    assert len(elec_resp.json()) >= 2


def test_procurement_endpoints(client):
    """Verify MDM procurement aggregates and peer benchmark exceptions."""
    resp = client.get("/api/v1/procurement/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_spend_inr"] > 0
    assert data["total_quantity_kg"] > 0
    assert len(data["anomalies"]) > 0
    assert "governance_notice" in data

    # Anomalies endpoint
    anom_resp = client.get("/api/v1/procurement/anomalies")
    assert anom_resp.status_code == 200
    assert len(anom_resp.json()) > 0


def test_risk_endpoints(client):
    """Verify risk vs priority separation and deterministic action catalog."""
    resp = client.get("/api/v1/risk/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_schools"] == 600
    # In observed cohort, critical risk severity is strictly 0
    assert data["critical_risk_count"] == 0
    # But priority schools exist
    assert data["priority_school_count"] > 0
    assert len(data["driver_distribution"]) > 0
    assert len(data["policy_action_catalog"]) == 4

    # Priorities queue
    pri_resp = client.get("/api/v1/risk/priorities?limit=20")
    assert pri_resp.status_code == 200
    queue = pri_resp.json()
    assert len(queue) == 20
    assert queue[0]["rank"] == 1
    assert queue[0]["intervention_priority_score"] >= queue[-1]["intervention_priority_score"]


def test_quality_endpoints(client):
    """Verify data trust score (94.6), 10 gates, and lineage contracts."""
    resp = client.get("/api/v1/quality/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["data_trust_score"] == 94.6
    assert len(data["quality_gates"]) == 10
    assert len(data["reconciliation_matrix"]) == 5

    lineage_resp = client.get("/api/v1/quality/lineage")
    assert lineage_resp.status_code == 200
    assert len(lineage_resp.json()) == 5


def test_insights_endpoints(client):
    """Verify attendance-academic correlation and segmentation endpoints."""
    resp_assoc = client.get("/api/v1/insights/association")
    assert resp_assoc.status_code == 200
    data_assoc = resp_assoc.json()
    assert data_assoc["overall_pearson_r"] == 0.453
    assert len(data_assoc["district_associations"]) == 9

    resp_seg = client.get("/api/v1/insights/segmentation")
    assert resp_seg.status_code == 200
    data_seg = resp_seg.json()
    assert data_seg["k_clusters"] == 4
    assert len(data_seg["cluster_profiles"]) == 4


def test_agent_query_endpoint(client):
    """Verify Phase 6 Graph-First AI Agent live query endpoint."""
    payload = {
        "query": "Which district has the lowest attendance rate?",
        "session_id": "test-session-1",
    }
    resp = client.post("/api/v1/agent/query", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "query_id" in data
    assert len(data["citations"]) > 0
    assert data["grounding_audit"]["is_grounded"] is True


def test_agent_capabilities_and_health_endpoints(client):
    """Verify capabilities and health check endpoints."""
    h_resp = client.get("/api/v1/agent/health")
    assert h_resp.status_code == 200
    assert h_resp.json()["status"] == "HEALTHY"

    c_resp = client.get("/api/v1/agent/capabilities")
    assert c_resp.status_code == 200
    assert len(c_resp.json()["supported_intents"]) > 0

