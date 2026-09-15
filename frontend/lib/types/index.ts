/**
 * TypeScript Data Models matching FastAPI Governed API Schemas
 */

export interface MetricContext {
  value: number;
  unit: string;
  metric: string;
  coverage_pct: number;
  source: string;
  method: string;
  benchmark?: number | null;
}

export interface DynamicAlert {
  title: string;
  finding: string;
  evidence: string;
  interpretation: string;
  limitation: string;
  level: "critical" | "warning" | "info" | "success";
}

export interface ExecutiveKPIs {
  schools_monitored: MetricContext;
  average_attendance: MetricContext;
  average_academic_score: MetricContext;
  priority_schools: MetricContext;
  infrastructure_readiness: MetricContext;
  data_quality_coverage: MetricContext;
}

export interface ExecutiveOverviewResponse {
  kpis: ExecutiveKPIs;
  alerts: DynamicAlert[];
  district_ranking: Array<{
    district: string;
    school_count: number;
    total_enrollment: number;
    avg_attendance_rate: number;
    avg_academic_score: number;
    avg_infrastructure_readiness: number;
    avg_data_quality_rate: number;
    high_priority_school_count: number;
    priority_school_rate_pct: number;
  }>;
  welfare_matrix: Array<{
    school_id: string;
    school_name: string;
    district: string;
    infrastructure_readiness_pct: number;
    academic_score: number;
    welfare_quadrant: string;
    intervention_priority_score: number;
    enrollment: number;
  }>;
  attendance_academic_summary: {
    pearson_r: number;
    spearman_rho: number;
    sample_size: number;
    coverage_pct: number;
    points: Array<{
      school_id: string;
      school_name: string;
      district: string;
      attendance_rate_pct: number;
      academic_score: number;
      enrollment: number;
    }>;
  };
  top_priorities: Array<{
    rank: number;
    school_id: string;
    school_name: string;
    district: string;
    block: string;
    enrollment: number;
    intervention_priority_score: number;
    intervention_priority_tier: string;
    risk_score: number;
    risk_tier: string;
    primary_driver: string;
    attendance_rate_pct: number;
    academic_score: number;
    infrastructure_readiness_pct: number;
    recommended_action: string;
  }>;
  trust_pipeline: {
    data_trust_score: number;
    raw_records?: number;
    deduplicated_records?: number;
    rescued_records?: number;
    trusted_records?: number;
    quarantined_records?: number;
    last_refreshed?: string;
  };
  active_filters: Record<string, any>;
}

export interface DistrictPerformanceItem {
  district: string;
  school_count: number;
  total_enrollment: number;
  avg_attendance_rate: number;
  avg_academic_score: number;
  avg_infrastructure_readiness: number;
  avg_data_quality_rate: number;
  high_priority_school_count: number;
  moderate_priority_school_count: number;
  critical_quadrant_school_count: number;
  priority_school_rate_pct: number;
}

export interface SchoolSummaryItem {
  school_id: string;
  school_name: string;
  district: string;
  block: string;
  school_type: string;
  medium: string;
  enrollment: number;
  attendance_rate_pct: number;
  academic_score: number;
  student_teacher_ratio: number;
  infrastructure_readiness_pct: number;
  risk_score: number;
  risk_tier: string;
  primary_driver: string;
  secondary_driver: string;
  intervention_priority_score: number;
  intervention_priority_tier: string;
  welfare_quadrant: string;
  data_quality_rate_pct: number;
}

export interface AmenityStatusMap {
  electricity?: boolean | null;
  drinking_water?: boolean | null;
  functional_toilet?: boolean | null;
  boundary_wall?: boolean | null;
  playground?: boolean | null;
}

export interface SchoolProfileResponse {
  school_id: string;
  school_name: string;
  district: string;
  block: string;
  school_type: string;
  medium: string;
  enrollment: number;
  student_teacher_ratio: number;
  attendance_rate_pct: number;
  academic_score: number;
  infrastructure_readiness_pct: number;
  risk_score: number;
  risk_tier: string;
  intervention_priority_score: number;
  intervention_priority_tier: string;
  welfare_quadrant: string;
  quadrant_action?: string | null;
  primary_driver: string;
  secondary_driver: string;
  attendance_deficit: number;
  academic_deficit: number;
  infrastructure_deficit: number;
  data_coverage_score: number;
  confidence_score: number;
  amenities: AmenityStatusMap;
  amenities_available_count?: number;
  amenities_reported_count?: number;
  recommended_action: string;
  recommendation_details: string;
  district_benchmark: {
    district_avg_attendance: number;
    district_avg_academic: number;
    district_avg_infrastructure: number;
  };
}

export interface AttendanceTimeseriesPoint {
  date: string;
  present: number;
  total: number;
  attendance_pct: number;
  records_count: number;
  has_flagged_record: boolean;
  has_proxy_record: boolean;
}

export interface AssessmentSubjectItem {
  subject: string;
  grade: number;
  avg_score: number;
  assessment_count: number;
  avg_total_marks: number;
  has_proxy_score: boolean;
}

export interface SchoolProcurementSummary {
  school_id: string;
  school_name: string;
  district: string;
  total_spend_inr: number;
  total_quantity_kg: number;
  procurement_records: number;
  avg_cost_per_kg: number;
  avg_cost_per_student: number;
  grain_count: number;
  vendor_count: number;
  is_procurement_outlier: boolean;
  procurement_anomaly_reason?: string | null;
  spend_per_student_iqr_threshold?: number | null;
}

export interface WelfareOverviewResponse {
  total_schools: number;
  avg_infrastructure_readiness: number;
  amenity_distributions: Array<{
    amenity_name: string;
    available_count: number;
    missing_count: number;
    unknown_count: number;
    availability_rate_pct: number;
    reporting_coverage_pct: number;
  }>;
  electricity_comparison: Array<{
    electricity?: string | null;
    electricity_label: string;
    school_count: number;
    avg_academic_score: number;
    avg_attendance_rate: number;
    avg_data_coverage_score: number;
  }>;
  welfare_gap_matrix: Array<{
    school_id: string;
    school_name: string;
    district: string;
    infrastructure_readiness_pct: number;
    academic_score: number;
    welfare_quadrant: string;
    intervention_priority_score: number;
  }>;
  quadrant_counts: Record<string, number>;
  non_causal_disclaimer: string;
}

export interface ProcurementAnomalyItem {
  school_id: string;
  school_name: string;
  district: string;
  enrollment: number;
  total_spend_inr: number;
  total_quantity_kg: number;
  avg_cost_per_student: number;
  spend_per_student_iqr_threshold: number;
  procurement_anomaly_reason: string;
  operational_context: string;
}

export interface ProcurementOverviewResponse {
  total_spend_inr: number;
  total_quantity_kg: number;
  avg_cost_per_kg: number;
  avg_cost_per_student: number;
  schools_covered: number;
  outlier_count: number;
  spend_by_district: Array<{ district: string; total_spend_inr: number }>;
  quantity_by_grain: Array<{ grain_name: string; quantity_kg: number; total_spend_inr: number }>;
  vendor_breakdown: Array<{ vendor_name: string; delivery_count: number; total_spend_inr: number }>;
  anomalies: ProcurementAnomalyItem[];
  governance_notice: string;
}

export interface PrioritySchoolItem {
  rank: number;
  school_id: string;
  school_name: string;
  district: string;
  block: string;
  enrollment: number;
  intervention_priority_score: number;
  intervention_priority_tier: string;
  risk_score: number;
  risk_tier: string;
  primary_driver: string;
  secondary_driver: string;
  attendance_rate_pct: number;
  academic_score: number;
  infrastructure_readiness_pct: number;
  recommended_action: string;
}

export interface RiskSummaryResponse {
  total_schools: number;
  priority_school_count: number;
  high_priority_count: number;
  critical_risk_count: number;
  critical_welfare_quadrant_count: number;
  driver_distribution: Array<{ driver: string; school_count: number; percentage: number }>;
  risk_tier_distribution: Record<string, number>;
  priority_tier_distribution: Record<string, number>;
  risk_vs_priority_points: Array<any>;
  policy_action_catalog: Array<{ driver: string; trigger: string; action: string; protocol: string }>;
  sensitivity_proof: Record<string, string>;
}

export interface QualitySummaryResponse {
  data_trust_score: number;
  total_schools: number;
  total_operational_records: number;
  trusted_records: number;
  flagged_records: number;
  excluded_records: number;
  duplicates_removed: number;
  quality_gates: Array<{
    gate_number: number;
    check_name: string;
    dataset: string;
    records_evaluated: number;
    records_flagged: number;
    resolution_method: string;
    pass_status: string;
  }>;
  reconciliation_matrix: Array<{
    dataset: string;
    raw_records: number;
    exact_duplicates: number;
    rescued_records: number;
    trusted_records: number;
    status: string;
  }>;
  lineage_catalog: Array<{
    metric_name: string;
    formula: string;
    source_table: string;
    governed_view: string;
    filters_applied: string;
    exclusions: string;
    aggregation_policy: string;
  }>;
}

export interface DimensionOptionsResponse {
  districts: string[];
  blocks_by_district: Record<string, string[]>;
  school_types: string[];
  mediums: string[];
  risk_tiers: string[];
  drivers: string[];
  welfare_quadrants: string[];
}

export interface FilterState {
  district?: string;
  block?: string;
  school_type?: string;
  medium?: string;
  risk_tier?: string;
  primary_driver?: string;
  welfare_quadrant?: string;
  search?: string;
}

export interface DistrictListResponse {
  districts: DistrictPerformanceItem[];
  total_districts: number;
}

export interface DistrictDetailResponse {
  summary: DistrictPerformanceItem;
  schools: Array<Record<string, any>>;
}

export interface DistrictAssociationItem {
  district: string;
  school_count: number;
  pearson_r: number;
  spearman_rho: number;
  avg_attendance: number;
  avg_academic: number;
}

export interface AttendanceAcademicAssociationResponse {
  overall_pearson_r: number;
  overall_spearman_rho: number;
  sample_size: number;
  coverage_pct: number;
  p_value_estimate: number;
  district_associations: DistrictAssociationItem[];
  non_causal_disclaimer: string;
}

export interface SegmentationClusterProfile {
  cluster_id: number;
  cluster_name: string;
  school_count: number;
  avg_attendance: number;
  avg_academic: number;
  avg_infrastructure: number;
  avg_risk_score: number;
  recommended_policy_focus: string;
}

export interface SchoolSegmentationResponse {
  k_clusters: number;
  silhouette_score: number;
  cluster_profiles: SegmentationClusterProfile[];
  school_cluster_assignments: Array<Record<string, any>>;
}

export interface EvidenceCitation {
  source_view: string;
  record_identifier: string;
  metric_id: string;
  metric_name: string;
  value: any;
  unit: string;
  driver?: string;
  district?: string;
  generated_at: string;
  methodology_reference: string;
}

export interface RecommendedActionItem {
  action_code: string;
  action_title: string;
  target_entity: string;
  urgency: string;
  rationale: string;
  estimated_impact: string;
  owner: string;
}

export interface ChartPlanItem {
  chart_type: string;
  title: string;
  subtitle: string;
  x_key: string;
  y_keys: string[];
  series_labels?: Record<string, string>;
  color_scheme?: string;
  data: Array<Record<string, any>>;
  kpi_value?: string;
  kpi_subtext?: string;
  is_renderable: boolean;
}

export interface AgentQueryRequest {
  query: string;
  session_id?: string;
  context_override?: Record<string, any>;
  active_filters?: Record<string, any>;
}

export interface AgentQueryResponse {
  query_id: string;
  query: string;
  intent_type: string;
  confidence: number;
  answer: string;
  summary: string;
  primary_metric: string;
  primary_metric_label: string;
  evidence_count: number;
  evidence_records: Array<Record<string, any>>;
  citations: EvidenceCitation[];
  chart_plan: ChartPlanItem;
  recommendations: RecommendedActionItem[];
  methodology: Record<string, any>;
  caveats: string[];
  follow_up_questions: string[];
  grounding_audit: Record<string, any>;
  timings_ms: Record<string, number>;
  session_id?: string;

  // Phase 6 LLM integration fields
  reasoning_mode?: string;
  llm_provider?: string;

  // Backward compatibility fields
  chart_type?: string;
  chart_data?: Array<Record<string, any>>;
  confidence_score?: number;
  intent?: string;
  metric?: string;
  dimensions?: string[];
  filters?: Record<string, any>;
  coverage?: Record<string, any>;
}

export interface AgentCapabilitiesResponse {
  supported_intents: string[];
  governed_metrics: Array<Record<string, any>>;
  supported_districts: string[];
  guardrails: string[];
  architecture: string;
  llm_provider?: string;
  reasoning_mode?: string;
}

export interface LLMStatusResponse {
  provider: string;
  reasoning_mode: string;
  is_configured: boolean;
  is_available: boolean;
  circuit_breaker_active: boolean;
  model: string;
  base_url_configured: boolean;
}



