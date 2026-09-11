-- ============================================================
-- EDUPULSE AI — CANONICAL ANALYTICAL DATA WAREHOUSE SCHEMA
-- Database Engine: DuckDB
-- Model Type: Dimensional Star Schema
-- ============================================================

-- ------------------------------------------------------------
-- 1. DIMENSIONS
-- ------------------------------------------------------------

-- Dimension: School
CREATE TABLE IF NOT EXISTS dim_school (
    school_key INTEGER PRIMARY KEY,
    school_id VARCHAR UNIQUE NOT NULL,
    school_name VARCHAR NOT NULL,
    district VARCHAR NOT NULL,
    block VARCHAR NOT NULL,
    total_enrolled_students INTEGER NOT NULL,
    school_type VARCHAR NOT NULL,
    medium VARCHAR NOT NULL,
    district_imputation_status VARCHAR NOT NULL
);

-- Dimension: Date
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR NOT NULL,
    quarter INTEGER NOT NULL,
    week INTEGER NOT NULL,
    day_of_week VARCHAR NOT NULL,
    day_name VARCHAR NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_sunday BOOLEAN NOT NULL,
    is_month_start BOOLEAN NOT NULL,
    is_month_end BOOLEAN NOT NULL
);

-- Dimension: Grade
CREATE TABLE IF NOT EXISTS dim_grade (
    grade_key INTEGER PRIMARY KEY,
    grade_number INTEGER UNIQUE NOT NULL,
    grade_label VARCHAR NOT NULL
);

-- Dimension: Subject
CREATE TABLE IF NOT EXISTS dim_subject (
    subject_key INTEGER PRIMARY KEY,
    subject_standard VARCHAR UNIQUE NOT NULL,
    subject_category VARCHAR NOT NULL
);

-- Dimension: Vendor
CREATE TABLE IF NOT EXISTS dim_vendor (
    vendor_key INTEGER PRIMARY KEY,
    vendor_id VARCHAR UNIQUE NOT NULL,
    vendor_name VARCHAR NOT NULL,
    vendor_name_standard VARCHAR NOT NULL
);

-- Dimension: Grain
CREATE TABLE IF NOT EXISTS dim_grain (
    grain_key INTEGER PRIMARY KEY,
    grain_standard VARCHAR UNIQUE NOT NULL,
    price_per_kg DOUBLE NOT NULL,
    price_source VARCHAR NOT NULL,
    unit_basis VARCHAR NOT NULL
);

-- ------------------------------------------------------------
-- 2. FACTS
-- ------------------------------------------------------------

-- Fact: Student Attendance
CREATE TABLE IF NOT EXISTS fact_attendance (
    record_key INTEGER PRIMARY KEY,
    record_id VARCHAR NOT NULL,
    school_key INTEGER NOT NULL REFERENCES dim_school(school_key),
    date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    grade_key INTEGER NOT NULL REFERENCES dim_grade(grade_key),
    school_id VARCHAR NOT NULL,
    date DATE NOT NULL,
    grade_number INTEGER NOT NULL,
    total_students INTEGER NOT NULL,
    present_students INTEGER NOT NULL,
    attendance_rate DOUBLE,
    teacher_present VARCHAR NOT NULL,
    marked_by VARCHAR NOT NULL,
    is_impossible_attendance BOOLEAN NOT NULL,
    is_proxy_attendance BOOLEAN NOT NULL,
    is_trusted_attendance BOOLEAN NOT NULL,
    quality_status VARCHAR NOT NULL,
    attendance_anomaly_reason VARCHAR
);

-- Fact: Academic FLN Assessment
CREATE TABLE IF NOT EXISTS fact_assessment (
    assessment_key INTEGER PRIMARY KEY,
    assessment_id VARCHAR NOT NULL,
    school_key INTEGER NOT NULL REFERENCES dim_school(school_key),
    date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    grade_key INTEGER NOT NULL REFERENCES dim_grade(grade_key),
    subject_key INTEGER NOT NULL REFERENCES dim_subject(subject_key),
    school_id VARCHAR NOT NULL,
    date DATE NOT NULL,
    grade_number INTEGER NOT NULL,
    subject_standard VARCHAR NOT NULL,
    grading_scale VARCHAR NOT NULL,
    normalized_score_pct DOUBLE,
    score_normalization_method VARCHAR NOT NULL,
    is_letter_grade_proxy BOOLEAN NOT NULL,
    total_students_assessed INTEGER NOT NULL,
    quality_status VARCHAR NOT NULL
);

-- Fact: School Infrastructure Inspection
CREATE TABLE IF NOT EXISTS fact_infrastructure (
    inspection_key INTEGER PRIMARY KEY,
    inspection_id VARCHAR NOT NULL,
    school_key INTEGER NOT NULL REFERENCES dim_school(school_key),
    date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    school_id VARCHAR NOT NULL,
    date DATE NOT NULL,
    has_electricity VARCHAR NOT NULL,
    has_drinking_water VARCHAR NOT NULL,
    has_functional_toilet VARCHAR NOT NULL,
    has_boundary_wall VARCHAR NOT NULL,
    has_playground VARCHAR NOT NULL,
    inspector_name VARCHAR NOT NULL,
    remarks VARCHAR NOT NULL
);

-- Fact: MDM Procurement
CREATE TABLE IF NOT EXISTS fact_procurement (
    procurement_key INTEGER PRIMARY KEY,
    procurement_id VARCHAR NOT NULL,
    school_key INTEGER NOT NULL REFERENCES dim_school(school_key),
    date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    vendor_key INTEGER NOT NULL REFERENCES dim_vendor(vendor_key),
    grain_key INTEGER NOT NULL REFERENCES dim_grain(grain_key),
    school_id VARCHAR NOT NULL,
    date DATE NOT NULL,
    vendor_id VARCHAR NOT NULL,
    grain_standard VARCHAR NOT NULL,
    quantity_kg DOUBLE,
    unit_standard VARCHAR NOT NULL,
    price_per_kg DOUBLE,
    total_cost DOUBLE,
    payment_status VARCHAR NOT NULL,
    quantity_rescue_method VARCHAR NOT NULL,
    cost_rescue_method VARCHAR NOT NULL,
    quality_status VARCHAR NOT NULL
);

-- ------------------------------------------------------------
-- 3. OPTIMIZATION INDEXES
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_att_school ON fact_attendance(school_key);
CREATE INDEX IF NOT EXISTS idx_att_date ON fact_attendance(date_key);
CREATE INDEX IF NOT EXISTS idx_att_trusted ON fact_attendance(is_trusted_attendance);

CREATE INDEX IF NOT EXISTS idx_ass_school ON fact_assessment(school_key);
CREATE INDEX IF NOT EXISTS idx_ass_subject ON fact_assessment(subject_key);

CREATE INDEX IF NOT EXISTS idx_inf_school ON fact_infrastructure(school_key);
CREATE INDEX IF NOT EXISTS idx_pro_school ON fact_procurement(school_key);
CREATE INDEX IF NOT EXISTS idx_pro_vendor ON fact_procurement(vendor_key);
