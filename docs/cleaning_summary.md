# EDUPULSE AI — Phase 2 Data Cleaning & Rescue Summary
**Execution Timestamp**: `2026-09-11T11:58:42.701126`  
**Pipeline Runtime**: `1.64s`  
**Master Data Trust Score**: **94.9 / 100**  

---

## 1. Data Trust Score Composition
- **Record Trustworthiness Points**: 37.0 / 40.0
- **Referential Integrity Points**: 30.0 / 30.0
- **Value Rescue Points**: 20.0 / 20.0
- **Anomaly Containment Points**: 7.9 / 10.0

*Formula*: `Score = (TrustedRatio * 40) + ReferentialScore(30) + RescueScore(20) + ContainmentScore(10)`

---

## 2. Dataset Processing Reconciliation Matrix
| Dataset | Raw Rows | Clean Rows | Trusted Rows | Flagged / Anomaly | Excluded | Duplicates Removed | Missing Rescued |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Schools** | 618 | 600 | 598 | 2 | 0 | 18 | 20 |
| **Attendance** | 20,800 | 19,994 | 18,065 | 1,929 | 1,929 | 806 | 405 |
| **Infrastructure** | 3,150 | 3,000 | 3,000 | 0 | 0 | 150 | 0 |
| **Procurement** | 12,360 | 12,000 | 11,909 | 91 | 0 | 360 | 2,292 |
| **Assessments** | 8,000 | 8,000 | 8,000 | 1,983 | 0 | 0 | 1,983 |

---

## 3. Key Transformation & Rescue Accomplishments
1. **School ID Canonicalization**: Standardized all variants to `SCHxxxx` with 100% referential integrity across 600 unique schools.
2. **Date Format Harmonization**: Decoded all 6 formatting patterns across 365 calendar days into ISO `YYYY-MM-DD` and enriched calendar attributes.
3. **District Imputation**: Imputed 21 missing districts from administrative blocks deterministically; assigned 2 unresolvable records to 'Unknown'.
4. **Attendance Anomaly Containment**: Flagged 835 impossible records (`present > total`) and 1,011 Sunday proxy records without altering raw student counts.
5. **MDM Unit Conversion & Price-Based Rescue**: Converted bags, sacks, bori, and grams to standard kg. Derived missing quantities and costs using verified commodity prices (Wheat ₹30, Rice ₹40, Pulses ₹90, Oil ₹120).
6. **Academic Score Normalization**: Normalized 6 grading scales to 0.0–100.0%. Documented letter grade proxies and enabled sensitivity toggles.
7. **Audit Lineage**: Exported full decision audit to `data/processed/cleaning_audit.parquet`.