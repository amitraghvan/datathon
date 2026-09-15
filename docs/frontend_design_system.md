# EduPulse AI — Enterprise Frontend Design System
**Document Version:** 2.0 (Enterprise White Consulting Edition)  
**Standard:** McKinsey / BCG / Deloitte Analytical Briefing Guidelines  
**Audience:** State Education Secretaries, Chief Data Officers, District Education Officers, Frontend Engineering Team  

---

## 1. Design Philosophy & Vision

The EduPulse AI frontend has been redesigned from a dense dark-mode prototype into an authoritative, clean, minimal, enterprise-grade decision intelligence briefing platform. The design prioritizes **extreme legibility**, **information hierarchy**, **decision velocity**, and **transparent data provenance**.

### Core Tenets
1. **Light, Crisp Canvas:** Pure white cards (`#FFFFFF`) on a subtle slate canvas (`#F8FAFC`) with hair-line borders (`#E2E8F0`) provide maximum contrast and reduce cognitive fatigue during prolonged analytical sessions.
2. **Restrained Semantic Palette:** Color is strictly reserved for quantitative meaning and triage urgency. No arbitrary neon accents or decorative glows.
3. **Data Trust Prominence:** Every analytical surface explicitly communicates its underlying data gate status (10/10 gates passed), sample size ($N$), and DuckDB warehouse provenance.
4. **Consulting Presentation Quality:** Typography, table densities, quadrant charts, and narrative findings mirror boardroom briefing decks prepared by Tier-1 strategy consultancies.

---

## 2. Color Palette & Semantic Tokens

### 2.1 Surface & Neutral Tokens
| Token | Hex Value | CSS Variable / Tailwind | Application |
|---|---|---|---|
| **Canvas Background** | `#F8FAFC` | `bg-[#F8FAFC]` / `slate-50` | Primary application canvas |
| **Card / Surface Background** | `#FFFFFF` | `bg-white` | Analytical cards, tables, drawers, modals |
| **Subtle Card Fill** | `#F1F5F9` | `bg-slate-100` / `bg-slate-50` | KPI metric containers, table headers, code blocks |
| **Border Subtle** | `#E2E8F0` | `border-slate-200` | Universal card, divider, and table cell borders |
| **Border Hairline** | `#F1F5F9` | `border-slate-100` | Inner table row dividers |
| **Border Active / Focus** | `#0284C7` | `border-sky-600` | Active input borders, focused form controls |

### 2.2 Typography & Contrast Tokens
| Token | Hex Value | Tailwind Class | Contrast vs Canvas | Usage |
|---|---|---|---|---|
| **Primary Text** | `#0F172A` | `text-slate-900` | **16.1:1** (AAA) | Headings, primary KPI values, school identifiers |
| **Secondary Text** | `#334155` | `text-slate-700` | **10.5:1** (AAA) | Body copy, narrative findings, table content |
| **Muted Text** | `#64748B` | `text-slate-500` | **4.9:1** (AA) | Labels, timestamps, sample sizes ($N$), footnotes |
| **Subtle Text** | `#94A3B8` | `text-slate-400` | **3.0:1** (UI Components)| Icons, inactive tab icons, placeholder text |

### 2.3 Semantic Triaging Accents
| Semantic Role | Background Tint | Border | Text Accent | Hex Base | Usage |
|---|---|---|---|---|---|
| **Optimal / Verified** | `bg-emerald-50` | `border-emerald-200` | `text-emerald-700` | `#059669` | High attendance ($\ge 85\%$), 100% amenities, data trust |
| **Warning / Moderate** | `bg-amber-50` | `border-amber-200` | `text-amber-800` | `#D97706` | Attendance lag ($70-84\%$), spend outliers, caveats |
| **Critical / High Risk** | `bg-rose-50` | `border-rose-200` | `text-rose-700` | `#DC2626` | High priority triage, severe amenity deficits ($<70\%$) |
| **Analytical / Benchmark** | `bg-sky-50` | `border-sky-200` | `text-sky-700` | `#0284C7` | Primary chart series, active filters, model inference |
| **Governance / LLM** | `bg-purple-50` | `border-purple-200` | `text-purple-700` | `#7C3AED` | Llama 3.1 synthesis badge, reasoning pipeline steps |

---

## 3. Typography & Hierarchy Standards

- **Primary Font Family:** System font stack (`Inter`, `-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `Roboto`, `sans-serif`) for crisp, native rendering without external layout shifts.
- **Monospace Family:** `ui-monospace`, `SFMono-Regular`, `Menlo`, `Monaco`, `Consolas`, `monospace` for School IDs (`SCH0386`), SQL queries, and exact numeric statistics.

### Scale & Weight Matrix
- **Page Title (`h1`):** `text-xl sm:text-2xl font-bold text-slate-900 tracking-tight`
- **Section Heading (`h2`):** `text-sm sm:text-base font-bold text-slate-900 tracking-normal`
- **Card Subheading (`h3`):** `text-xs sm:text-sm font-semibold text-slate-800`
- **Metric Big Number:** `text-2xl sm:text-3xl font-bold text-slate-900 font-sans tracking-tight`
- **Section Kicker / Tag:** `text-[10px] sm:text-[11px] font-bold text-slate-500 uppercase tracking-wider`
- **Body Text:** `text-xs sm:text-sm text-slate-600 leading-relaxed`
- **Table Cell Text:** `text-xs text-slate-800 font-medium`

---

## 4. Reusable Component Specifications

### 4.1 MetricCard (`components/kpi/metric-card.tsx`)
- **Structure:** White card container (`bg-white border border-slate-200 rounded-xl p-5 shadow-2xs`).
- **Header:** Uppercase category label (`text-[11px] font-bold text-slate-500`) paired with a light icon badge.
- **Core Value:** Crisp charcoal numeral with formatted thousands separators or percentage sign.
- **Benchmarking Pill:** Subtle delta pill showing difference against state average (`+3.4 pts vs BM` in `bg-emerald-50 text-emerald-700`).
- **Footer:** Data trust provenance pill showing exact source table and data coverage percentage (`94.2% coverage`).

### 4.2 Editorial Insight AlertBanner (`components/kpi/alert-banner.tsx`)
- **Structure:** Pure white card with 4px left semantic border (`border-l-4 border-l-rose-500` / `amber-500` / `sky-600`).
- **Title & Badge:** Action-oriented headline (`text-sm font-bold text-slate-900`) with severity pill.
- **Editorial Breakdown:**
  - **Evidence:** Exact quantitative statistics grounded in DuckDB.
  - **Interpretation:** Pedagogical and administrative implications.
  - **Limitation / Caveat:** Causal boundaries (e.g. non-causal correlation).
- **Direct Link:** Deep navigation link to drill down into the affected school or view.

### 4.3 Interactive Data Tables (`components/tables/priority-schools-table.tsx`)
- **Structure:** Full-width bordered card with sticky header.
- **Header Row:** `bg-slate-50 border-b border-slate-200 text-[10px] uppercase font-bold text-slate-500`.
- **Data Rows:** Alternating hover highlight (`hover:bg-slate-50/80 transition-colors`).
- **School Identifier:** Clickable monospace link (`SCH0386` in `text-sky-700 font-bold font-mono hover:underline`).
- **Status Badges:** Compact pills with rounded borders (`bg-rose-50 text-rose-700 border border-rose-200`).

### 4.4 Analytical Charts (Recharts Configuration)
- **Background:** Transparent / Card White.
- **Cartesian Grid:** Light slate lines (`stroke="#F1F5F9"` or `#E2E8F0`).
- **Axis Styling:** Slate text (`stroke="#64748B"`, font size `10px` or `11px`).
- **Tooltip Container:** Pure white popover (`backgroundColor: "#FFFFFF", borderColor: "#CBD5E1", color: "#0F172A", boxShadow: "0 1px 3px rgba(0,0,0,0.08)"`).
- **Palette Series:**
  - Primary Series: `#0284C7` (Corporate Navy / Cerulean)
  - Secondary Series: `#059669` (Forest Emerald)
  - Warning / Outlier: `#D97706` (Executive Amber)
  - Critical / Deficit: `#DC2626` (Crimson Rose)

---

## 5. Responsive Behavior & Accessibility

- **Breakpoints:**
  - Mobile (`<640px`): Single-column stacking, collapsible sidebar, horizontal scrolling for dense data tables.
  - Tablet (`640px - 1024px`): 2-column KPI grid, responsive chart heights.
  - Desktop (`>1024px`): Fixed 230px executive sidebar, multi-column metric grids, 12-column analytical layouts.
- **WCAG 2.1 AA Compliance:** All text-to-background combinations meet or exceed 4.5:1 contrast ratio.
- **Touch Targets:** Buttons and filter selects have a minimum target size of 36px with clear focus outlines.
