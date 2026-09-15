# EduPulse AI Semantic Graph & Domain Ontology

## 1. Ontology Overview
The EduPulse AI Semantic Graph models the complex relationships between students, schools, educational administrative hierarchies, welfare infrastructure, and procurement operations. It serves as the domain truth model for intent classification, entity extraction, and multi-hop reasoning.

---

## 2. Entity Types (Nodes)

| Entity Type | Description | Key Identifier | Cardinality | Primary Attributes |
|---|---|---|---|---|
| `State` | Monitored educational state | `state_name` | 1 | Total districts, aggregate enrollment |
| `District` | Administrative educational district | `district_name` | 9 | Total schools, avg attendance, avg academic score |
| `Block` | Sub-district administrative unit | `block_name` | ~25 | District reference, school count |
| `School` | Educational institution | `school_id` (`SCH\d+`) | 600 | Category, medium, enrollment, risk tier, quadrant |
| `StudentCohort` | Aggregated student grade cohort | `(school_id, grade)` | ~3,000 | Attendance rate, FLN benchmark score |
| `Amenity` | Physical welfare infrastructure asset | `amenity_name` | 5 | Electricity, Drinking Water, Toilet, Wall, Playground |
| `Commodity` | Mid-Day Meal food supply item | `commodity_name` | 6 | Wheat, Rice, Pulses, Cooking Oil, Salt, Vegetables |
| `Vendor` | Procurement supply vendor | `vendor_name` | ~15 | Deliveries, transaction volume, spend |
| `ProcurementBatch` | Delivery shipment transaction | `transaction_id` | 1,200 | Cost per student, quantity kg, variance ratio |
| `Metric` | Governed analytical indicator | `metric_id` | 12 | Formula, calculation owner, caveats, unit |
| `WelfareQuadrant` | Strategic school segmentation cluster | `quadrant_name` | 4 | MODEL, RESILIENT, ACADEMIC, CRITICAL |
| `RiskDriver` | Primary vulnerability root cause | `driver_name` | 4 | INFRASTRUCTURE, ACADEMIC, ATTENDANCE, MULTI_FACTOR |
| `QualityGate` | Data governance compliance check | `gate_number` | 10 | Checks passed, records evaluated, pass rate |

---

## 3. Directional Relationships & Cardinalities (Edges)

```
[District] ──(1:N)──> [Block] ──(1:N)──> [School]
                                            │
               ┌────────────────────────────┼────────────────────────────┐
               │ (1:N)                      │ (1:N)                      │ (N:1)
               ▼                            ▼                            ▼
        [StudentCohort]               [Amenity]                  [WelfareQuadrant]
               │                            │
               │ (1:1)                      │ (Three-Valued)
               ▼                            ▼
        [AcademicScore]              [Status: AVAIL/MISS/UNK]
               │
               ▼
   [Non-Causal Association]
               ▲
               │ (Observational)
        [AttendanceRate]
               ▲
               │ (Welfare Incentive)
    [ProcurementDelivery] <──(N:1)── [Commodity] <──(N:1)── [Vendor]
```

### Edge Specifications:
1. `District HAS_BLOCK Block` (1:N, Join Key: `district`)
2. `Block CONTAINS_SCHOOL School` (1:N, Join Key: `block`)
3. `School OPERATES_COHORT StudentCohort` (1:N, Join Key: `school_id`)
4. `School EQUIPPED_WITH Amenity` (1:N, Join Key: `school_id`)
   - *Governance Rule*: Preserves three-valued logic (`AVAILABLE`, `MISSING`, `UNKNOWN`). `UNKNOWN` is never coerced to `FALSE`.
5. `School ASSIGNED_QUADRANT WelfareQuadrant` (N:1, Join Key: `welfare_quadrant`)
6. `School DRIVEN_BY RiskDriver` (N:1, Join Key: `primary_driver`)
7. `School RECEIVES_MDM ProcurementBatch` (1:N, Join Key: `school_id`)
8. `ProcurementBatch SUPPLIED_BY Vendor` (N:1, Join Key: `vendor_name`)
9. `ProcurementBatch DELIVERS Commodity` (N:1, Join Key: `commodity`)
10. `Attendance CORRELATES_WITH AcademicFLN` (Observational Bivariate, $r = 0.453$, $p < 0.001$)
    - *Governance Rule*: Non-causal phrasing strictly enforced.

---

## 4. Canonical Reasoning Paths

### 4.1 Intervention Diagnosis Path (`intervention_diagnosis`)
```
[School]
  ──(evaluates)──> [RetentionRiskScore: 0-100]
  ──(contextualizes)──> [DistrictRelativeGap]
  ──(computes)──> [InterventionPriorityScore: 0-100]
  ──(audits)──> [MissingPhysicalAmenities]
  ──(recommends)──> [School 360 Action Catalog Policy]
```

### 4.2 District Welfare Audit Path (`district_welfare_audit`)
```
[District]
  ──(aggregates)──> [AverageAttendanceRate]
  ──(aggregates)──> [AverageFLNScore]
  ──(aggregates)──> [InfrastructureReadinessPct]
  ──(identifies)──> [HighPrioritySchoolQueue]
  ──(formulates)──> [AcceleratedRemediationGrant]
```

### 4.3 Procurement Peer Exception Path (`procurement_peer_exception`)
```
[ProcurementBatch]
  ──(computes)──> [UnitCostPerStudentINR]
  ──(evaluates)──> [CommodityPeerDistributionBounds (Q1, Q3, IQR)]
  ──(flags)──> [Outlier if Cost > Q3 + 1.5 IQR]
  ──(audits)──> [Neutral Peer Benchmark Exception Notice]
  ──(recommends)──> [Supplier Invoice Reconciliation Protocol]
```

### 4.4 Attendance-Academic Association Path (`attendance_academic_association`)
```
[StudentCohortAttendance]
  ──(paired_with)──> [StudentCohortFLNTestScore]
  ──(computes)──> [Pearson r = 0.453, Spearman rho = 0.421]
  ──(audits)──> [Non-Causal Statistical Boundary Notice]
  ──(recommends)──> [Integrated Early Warning Retention Trigger]
```
