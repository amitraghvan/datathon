# EDUPULSE AI — Comprehensive Data Quality Audit Report
## TransOrg AgentIQ Datathon (Track 4: Education & EdTech)
**Generated**: `2026-09-11T11:47:47.275195`  
**System**: EDUPULSE AI Data Trust & Decision-Intelligence Platform  
**Status**: Phase 1 Baseline Audit Complete (Pristine Raw Data Preserved)

---

## 1. Executive Summary
A rigorous, non-destructive data quality audit was conducted across all five synthetic competition datasets. The objective was to uncover all deliberate data corruption, formatting inconsistencies, anomalous recordings, and broken linkages before executing any analytical transformations. **Zero raw data records were modified during this audit.**

### Issue Severity Overview
- **CRITICAL**: 3 (Impossible attendance, proxy marking fraud, missing quantities)
- **HIGH**: 5 (Mixed grading scales, messy booleans, duplicate master records, currency formatting)
- **MEDIUM**: 1 (Missing primary keys / record IDs)
- **INFO**: 1 (100% Referential integrity verified post-canonicalization)

---

## 2. Dataset Inventory & High-Level Metrics
| Dataset | File Name | Rows | Columns | Exact Duplicates | Key Duplicates |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **School Master** | `track4_school_master.csv` | 618 | 7 | 18 | 18 |
| **Student Attendance** | `track4_student_attendance.csv` | 20,800 | 8 | 800 | 1,204 |
| **School Infrastructure** | `track4_school_infrastructure.csv` | 3,150 | 10 | 150 | 150 |
| **Mdm Procurement** | `track4_mid_day_meal_procurement.xlsx` | 12,360 | 9 | 360 | 360 |
| **Test Scores** | `track4_test_scores.json` | 8,000 | 9 | 0 | 0 |

---

## 3. Referential Integrity & Entity Resolution Matrix
To determine if disparate datasets can be joined into a cohesive star schema, school IDs were normalized using canonical format `SCHxxxx`.

| Child Table | Raw Distinct IDs | Canonical Schools | Master Schools | Orphan Records | Integrity Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Student Attendance** | 600 | 600 | 600 | 0 | `PASSED (100% Match)` |
| **School Infrastructure** | 598 | 598 | 600 | 0 | `PASSED (100% Match)` |
| **Mdm Procurement** | 600 | 600 | 600 | 0 | `PASSED (100% Match)` |
| **Test Scores** | 600 | 600 | 600 | 0 | `PASSED (100% Match)` |

> [!NOTE]
> Every school referenced in the attendance, MDM procurement, and FLN assessment tables maps with 100% precision to the 600 unique schools in the master table. In infrastructure, 598 schools were inspected (2 schools were uninspected).

---

## 4. Detailed Data Quality Issues & Remediation Plan
| Severity | Dataset | Affected Field | Issue Identified | Records | Impact | Approved Remediation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **HIGH** | `track4_school_master.csv` | `ALL` | Exact Row Duplicates | 18 | Artificially inflates school count and district aggregations if not deduplicated. | Deduplicate on canonical school_id keeping the first occurrence. |
| **HIGH** | `track4_school_master.csv` | `district` | Missing Mandatory Dimension | 23 | Excludes schools from district-level retention and welfare tracking. | Impute 21 records deterministically via 1:1 block-district relationship; flag remaining 2 as Unknown. |
| **CRITICAL** | `track4_student_attendance.csv` | `present_students` | Impossible Attendance Record | 835 | Produces attendance rates > 100%, corrupting school and district performance rankings. | Preserve record in fact table, flag with is_impossible_attendance=True, and exclude from trusted KPI calculations. |
| **CRITICAL** | `track4_student_attendance.csv` | `date / present_students` | Proxy Attendance Fraud | 1,011 | Distorts operational welfare monitoring and hides chronic absenteeism via falsified proxy logs. | Flag records as is_proxy_attendance=True, exclude from trusted correlation analyses, and expose in Fraud & Quality Center. |
| **MEDIUM** | `track4_student_attendance.csv` | `record_id` | Missing Primary Key | 425 | Primary key null violation preventing relational constraint enforcement. | Synthesize deterministic UUID/hash surrogate keys from (school_id, date, grade). |
| **HIGH** | `track4_school_infrastructure.csv` | `Amenities (5 boolean cols)` | Messy Multilingual Booleans & Missing Values | 779 | Cannot calculate infrastructure readiness index without standardization. | Normalize strings to canonical TRUE/FALSE/UNKNOWN using dictionary tokens; compute readiness with unknown penalty. |
| **CRITICAL** | `track4_mid_day_meal_procurement.xlsx` | `quantity / unit` | Missing Quantity & Mixed Units | 1,909 | Prevents grain consumption and wastage analytics. | Extract embedded units; mathematically derive missing quantity via exact grain price (₹30, ₹40, ₹90, ₹120); standardize all to kg. |
| **HIGH** | `track4_mid_day_meal_procurement.xlsx` | `total_cost` | Messy Currency Formatting & Missing Costs | 646 | Inaccurate financial and procurement budget tracking. | Strip currency symbols and commas to parse numeric INR; derive missing cost via quantity_kg * unit_price. |
| **HIGH** | `track4_test_scores.json` | `grading_scale / avg_score` | Mixed Academic Grading Scales | 8,000 | Direct comparison across schools or grades without normalization is statistically invalid. | Normalize Percentage, pct, %, CGPA (x10), Raw Marks (num/den), and Letter Grades (documented mid-point proxy) into normalized_score_pct (0–100). |
| **INFO** | `ALL (Referential Integrity)` | `school_id` | Referential Integrity Audit | 0 | Flawless foreign key join integrity achieved across the entire data warehouse. | Enforce canonical school ID transformation in the ingestion/cleaning pipeline. |

---

## 5. Column-Level Profiling Summaries

### `track4_school_master.csv`
| Column Name | Inferred Dtype | Null Count | Null % | Unique Values | Sample Values |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `school_id` | `str` | 0 | 0.0% | 600 | `SCH0050, SCH0583, SCH0083` |
| `school_name` | `str` | 0 | 0.0% | 517 | `Govt. Senior Secondary School Tank, Govt. Middle School Dara, Govt. Primary School Dutta` |
| `district` | `str` | 23 | 3.72% | 17 | `Moga, Ferozepur, Bathinda` |
| `block` | `str` | 64 | 10.36% | 33 | `Moga-I, Makhu, Talwandi Sabo` |
| `total_enrolled_students` | `int64` | 0 | 0.0% | 303 | `424, 436, 196` |
| `school_type` | `str` | 0 | 0.0% | 8 | `Secondary, Higher Secondary, Primary` |
| `medium` | `str` | 0 | 0.0% | 5 | `Punjabi, Hindi, hindi` |

### `track4_student_attendance.csv`
| Column Name | Inferred Dtype | Null Count | Null % | Unique Values | Sample Values |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `record_id` | `str` | 425 | 2.04% | 19,596 | `ATT0014650, ATT0009232, ATT0006474` |
| `date` | `str` | 0 | 0.0% | 2,190 | `07-26-2025, 03.11.2025, 05-16-2025` |
| `school_id` | `str` | 0 | 0.0% | 3,443 | `SCH-0596, sch_0054, SCH-0433` |
| `grade` | `str` | 0 | 0.0% | 15 | `5, I, 6` |
| `total_students` | `int64` | 0 | 0.0% | 261 | `85, 197, 58` |
| `present_students` | `int64` | 0 | 0.0% | 291 | `60, 119, 52` |
| `teacher_present` | `str` | 1,025 | 4.93% | 23 | `True, Available, haan` |
| `marked_by` | `str` | 3,484 | 16.75% | 6 | `Admin, Class Teacher, Clerk` |

### `track4_school_infrastructure.csv`
| Column Name | Inferred Dtype | Null Count | Null % | Unique Values | Sample Values |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `inspection_id` | `str` | 0 | 0.0% | 3,000 | `INSP02966, INSP00970, INSP01386` |
| `date` | `str` | 0 | 0.0% | 1,608 | `2025/04/02, 13.05.2025, 2025/06/26` |
| `school_id` | `str` | 0 | 0.0% | 1,787 | `sch_0476, SCH0337, SCH0127` |
| `has_electricity` | `str` | 170 | 5.4% | 23 | `H, True, False` |
| `has_drinking_water` | `str` | 146 | 4.63% | 23 | `True, No, False` |
| `has_functional_toilet` | `str` | 140 | 4.44% | 23 | `True, Yes, False` |
| `has_boundary_wall` | `str` | 177 | 5.62% | 23 | `Yes, True, Working` |
| `has_playground` | `str` | 146 | 4.63% | 23 | `H, Functional, Broken` |
| `inspector_name` | `str` | 332 | 10.54% | 2,665 | `Fariq Tripathi, Unnati Kulkarni, Girik Natt` |
| `remarks` | `str` | 513 | 16.29% | 6 | `Good condition, Toilets locked, Average` |

### `track4_mid_day_meal_procurement.xlsx`
| Column Name | Inferred Dtype | Null Count | Null % | Unique Values | Sample Values |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `procurement_id` | `str` | 0 | 0.0% | 12,000 | `MDM008522, MDM010158, MDM007882` |
| `date` | `str` | 0 | 0.0% | 2,175 | `2026/01/14, 2025-08-10, 03/11/2025` |
| `school_id` | `str` | 0 | 0.0% | 3,165 | `SCH0249, SCH0140, SCH-0514` |
| `vendor_name` | `str` | 0 | 0.0% | 12 | `Singh Brothers, kumar general store, sharma traders pvt ltd` |
| `grain_type` | `str` | 0 | 0.0% | 18 | `WHEAT, gehun, Oil` |
| `quantity` | `object` | 1,909 | 15.44% | 1,985 | `40.7, 54.2, 0.8` |
| `unit` | `str` | 3,804 | 30.78% | 13 | `KGS, 50kg Bags, Grams` |
| `total_cost` | `object` | 646 | 5.23% | 5,553 | `336/-, 1221, 6504` |
| `payment_status` | `str` | 1,719 | 13.91% | 7 | `PENDING, Cleared, Paid` |

### `track4_test_scores.json`
| Column Name | Inferred Dtype | Null Count | Null % | Unique Values | Sample Values |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `assessment_id` | `str` | 0 | 0.0% | 8,000 | `TST005495, TST003026, TST006793` |
| `date` | `str` | 0 | 0.0% | 2,122 | `2025/05/05, 01.07.2025, 06-Mar-2026` |
| `school_id` | `str` | 0 | 0.0% | 2,800 | `sch0083, sch0103, sch_0147` |
| `grade` | `str` | 0 | 0.0% | 6 | `8, 5, 7` |
| `subject` | `str` | 0 | 0.0% | 8 | `English, Punjabi, Math` |
| `grading_scale` | `str` | 0 | 0.0% | 6 | `Letter Grade, pct, CGPA` |
| `avg_score` | `str` | 0 | 0.0% | 1,366 | `C, 63.4%, 7.7` |
| `max_marks` | `object` | 0 | 0.0% | 5 | `NA, 100, 10` |
| `total_students_assessed` | `int64` | 0 | 0.0% | 131 | `125, 76, 123` |

---

## 6. Data Lineage & Traceability Architecture
To ensure consulting-grade defensibility, every cleaned record in the data warehouse will retain its lineage metadata:
- `*_raw`: Pristine original value as recorded in source files.
- `*_clean`: Standardized canonical value.
- `*_transformation_status`: Enumerated status (`CANONICAL`, `RESCUED`, `IMPUTED`, `FLAGGED_ANOMALY`).
- `*_quality_flag`: Specific anomaly code (e.g. `ERR_ATT_PRESENT_GT_TOTAL`, `WARN_ATT_SUNDAY_PROXY`, `DERIVED_QTY_FROM_COST`).