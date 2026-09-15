# 3-Minute Hackathon Demo Script — EduPulse AI

**Platform:** EduPulse AI — Education Welfare Command Center  
**Target Audience:** Technical Judges, Policy Architects, Data Science Evaluators  
**Tagline:** "Clean. Connect. Detect. Explain. Act."  
**Demo Duration:** 3 to 5 minutes  

---

## Scene 1: The Problem (0:00 – 0:30)

**Presenter:**  
> "Education departments across India manage thousands of schools, but their data is trapped in fragmented, messy spreadsheets. Attendance logs have duplicate dates and impossible percentages. Infrastructure files have missing values. Test scores are mixed with letter grades. Procurement invoices have currency symbols and inconsistent units.
> 
> As a result, decision-makers are flying blind.
> 
> Welcome to **EduPulse AI** — an enterprise Education Welfare Command Center that cleans messy operational data, connects attendance, academics, welfare, and procurement signals, and delivers evidence-grounded decisions."

---

## Scene 2: Data Trust & 10 Quality Gates (0:30 – 1:00)

**Action:** Open `/quality` (Data Trust & Governance Center).  

**Presenter:**  
> "Before we show a single dashboard, we prove our data can be trusted.
> 
> Here in the Data Trust Center, you see our **94.6 / 100 Master Data Trust Score**.
> We ingested 44,928 raw records across 5 heterogeneous state datasets. Our pipeline executed **10 deterministic quality gates**:
> 
> - Standardizing school IDs and eliminating 18 duplicates down to 600 canonical schools.
> - Quarantining 214 attendance anomalies where present students exceeded enrollment.
> - Preserving three-valued boolean logic (`Available`, `Missing`, `Unknown`) so unverified amenities are never falsely treated as missing.
> - Resolving CBSE letter grades to midpoints and standardizing procurement to Kilograms and Indian Rupees.
> 
> The result? **43,594 operational rows with zero foreign-key orphans** in DuckDB."

---

## Scene 3: Executive Command Center (1:00 – 1:30)

**Action:** Navigate to `/` (Executive Command Center).  

**Presenter:**  
> "This is our Executive Command Center. In under 5 seconds, a state secretary can answer:
> 
> - **How many schools?** Exactly 600 monitored institutions.
> - **How is attendance?** 79.4% state average.
> - **Academic FLN performance?** 66.2 / 100 baseline.
> - **How many schools need immediate review?** 39 schools in the Priority Queue.
> - **Can I trust this data?** Verified 94.6 Data Trust Score.
> 
> Notice our single compact filter bar: as I filter by district, medium, or risk driver, all six KPIs, the district ranking, the 2×2 Welfare Gap Matrix, and the attendance-academic scatter update dynamically from compiled DuckDB views — with zero client-side metric calculation."

---

## Scene 4: Risk Severity vs. Intervention Priority (1:30 – 2:15)

**Action:** Navigate to `/intervention` (Intervention & Risk Command Center).  

**Presenter:**  
> "Now, look at a core analytical breakthrough: the distinction between **Risk Severity** and **Intervention Priority**.
> 
> Look at these cards:
> - **Priority Queue:** 39 schools.
> - **Critical Risk Severity:** 0 schools.
> 
> This is NOT a contradiction.
> **Risk Severity** measures the absolute magnitude of observed vulnerability. No school in our state has collapsed into catastrophic ruin.
> But **Intervention Priority** is an administrative sequencing order. It incorporates relative district performance deficits, confidence boosts, and multi-factor vulnerability flags.
> 
> 39 schools exhibit acute relative deficits that demand targeted administrative intervention right now."

---

## Scene 5: School 360 Deep Dive (2:15 – 2:45)

**Action:** Click on `SCH0386` in the priority queue (navigating to `/schools/SCH0386`).  

**Presenter:**  
> "Let's inspect our top-ranked school: **SCH0386** — Govt. Elementary School Sama in Moga.
> 
> Here is the School 360 profile:
> - We see its 79.1% attendance rate and 64.8% FLN score.
> - Its statutory amenity checklist shows **Drinking Water: Available**, but **Electricity: Missing** and **Playground: Unverified**.
> - Its dominant constraint is **Infrastructure Deficit**.
> - And here is the **Recommended Operational Policy Action**:
>   *'Standard Protocol: Priority Capital Works Allocation — Accelerated electricity and sanitation restoration.'*
> 
> Clear, actionable, evidence-based policy guidance."

---

## Scene 6: Welfare & Infrastructure Intelligence (2:45 – 3:15)

**Action:** Navigate to `/welfare`.  

**Presenter:**  
> "On the Welfare page, we track the five core physical amenities across all 600 institutions.
> Notice our category labels: **With Functional Electricity (N = 433)**, **Without Functional Electricity (N = 139)**, and **Electricity Status Unknown (N = 28)**.
> 
> We also display the competition-required electricity benchmark. Schools with functional electricity show an average FLN score of 66.2% versus 66.3% without.
> 
> Notice our mandatory governance banner:
> *'Observed performance differences reflect observational associations; they do not establish causal effects without controlled experimentation.'*
> We never overclaim."

---

## Scene 7: Graph-First AI Analyst (3:15 – 4:00)

**Action:** Navigate to `/ai-analyst`.  

**Presenter:**  
> "Finally, let's explore our **Graph-First AI Decision Intelligence Analyst**.
> This is NOT a generic chatbot or an LLM wrapper.
> 
> Let's ask:
> *'Which 10 schools should be reviewed first?'*
> 
> Look at the pipeline:
> 1. Our Semantic Graph classifies the intent as `ranking` and resolves the metric to `intervention_priority`.
> 2. The Deterministic Planner compiles a read-only DuckDB SQL query.
> 3. Llama 3.1 synthesizes the narrative strictly from the returned DuckDB evidence.
> 4. The Claim Validator audits every number and school ID against the warehouse.
> 5. Our Text-to-Chart engine automatically selects a `horizontal_bar` chart with full interactivity.
> 
> And if a user enters casual text like *'hi'*, our fast-path responds in 0.06 milliseconds without touching the database.
> If an adversary enters *'delete all records'*, our Prompt Injection Guard deflects it instantly."

---

## Scene 8: The Conclusion (4:00 – 4:15)

**Presenter:**  
> "EduPulse AI does not just show school data.
> 
> It rescues messy operational records, enforces statistical truth, and transforms fragmented signals into trusted, explainable education decisions.
> 
> Clean. Connect. Detect. Explain. Act.
> 
> Thank you."
