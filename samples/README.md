# CiviQual Stats Sample Data Files

All sample data files use **public sector contexts** appropriate for government agencies, courts, and public service organizations.

---

## Free Tier Samples

| File | Context | Key Columns | Recommended Analysis |
|------|---------|-------------|---------------------|
| `sample_control_chart.csv` | Court case processing times | Processing_Time, Case_Type, Clerk | I-Chart, I-MR Chart (Tests 1-6) |
| `sample_capability.csv` | Document processing cycle time | Processing_Days (LSL=14.5, USL=15.5) | Capability (Cp/Cpk) |
| `sample_anova.csv` | Processing by court division | Processing_Days, Division | ANOVA, Box Plot |
| `sample_correlation.csv` | Case complexity vs processing | Pages_Filed, Processing_Hours | Correlation, Scatter Plot |
| `sample_pareto.csv` | Filing defect categories | Defect_Category, Count | Pareto Chart |
| `sample_court_operations.csv` | Comprehensive case data | Multiple columns | 4-Up Chart, any analysis |
| `sample_court_cases.csv` | Court case tracking | Case metrics | Descriptive Statistics |
| `sample_court_clerk.csv` | Clerk productivity | Clerk performance data | Control Charts |
| `sample_311_services.csv` | Municipal service requests | Response times | Run Chart |
| `sample_citizen_services.csv` | Citizen service center | Wait times, satisfaction | Histogram |
| `sample_permits.csv` | Building permit processing | Permit cycle times | Box Plot |
| `sample_inspections.csv` | Code enforcement inspections | Inspection outcomes | Pareto |
| `sample_public_records.csv` | FOIA/public records requests | Response times | Control Charts |
| `sample_public_health.csv` | Health department services | Service delivery metrics | Capability |
| `sample_mail_processing.csv` | Government mail center | Processing volume | Run Chart |
| `sample_benefits.csv` | Benefits administration | Application processing | ANOVA |

---

## Pro Tier Samples (★)

| File | Context | Key Columns | Recommended Analysis |
|------|---------|-------------|---------------------|
| `pro/sample_msa_gage_rr.csv` | Case file quality review | Case_File, Reviewer, Completeness_Score | ★ MSA (Gage R&R) |
| `pro/sample_doe_factorial.csv` | Court process optimization | Staff_Level, Filing_Method, Complexity | ★ DOE (2³ factorial) |
| `pro/sample_hypothesis_tests.csv` | Workflow comparison study | Process_Method, Processing_Days | ★ Hypothesis Tests |
| `pro/sample_regression.csv` | Processing time predictors | Processing_Time vs Staff, Complexity | ★ Multiple Regression |
| `pro/sample_cusum_ewma.csv` | Weekly processing trends | Avg_Processing_Days, Target | ★ CUSUM/EWMA Charts |
| `pro/sample_lean_metrics.csv` | Court process step metrics | Defects, Opportunities, Cycle_Time | ★ Lean Calculators |
| `pro/sample_fmea.csv` | Court process failure modes | Process_Step, Severity, Occurrence | ★ FMEA Worksheet |

---

## Detailed File Descriptions

### sample_control_chart.csv

**Context:** Court clerk office tracking daily case processing times.

**Built-in signals:**
- Observation 21: Point beyond 3σ (Rule 1 violation)
- Observations 31-37: 6+ consecutive points trending up (Rule 5 violation)

**Columns:**
- `Observation`: Sequence number (1-50)
- `Date`: Date of observation
- `Processing_Time`: Days to process case (target ~12.5)
- `Case_Type`: Civil or Criminal
- `Clerk`: Processing clerk identifier

---

### sample_capability.csv

**Context:** Document processing time in a clerk's office.

**Specification limits:**
- LSL: 14.50 days
- USL: 15.50 days
- Target: 15.00 days

**Columns:**
- `Document_ID`: Document identifier
- `Processing_Days`: Days to complete processing
- `Clerk_ID`: Clerk who processed document
- `Case_Type`: Civil or Criminal
- `Filing_Method`: Electronic or Paper
- `Timestamp`: Date and time processed

---

### sample_anova.csv

**Context:** Comparing case processing times across court divisions.

**Groups:** Civil, Criminal, Family, Probate

**Expected result:** Significant F-statistic showing divisions differ in processing time.

**Columns:**
- `Case_ID`: Case identifier
- `Division`: Court division (factor for ANOVA)
- `Processing_Days`: Days to process (response)
- `Filing_Type`: Original or Appeal
- `Fiscal_Year`: Year identifier

---

### sample_correlation.csv

**Context:** Examining factors that affect case processing time.

**Expected correlations:**
- Pages_Filed vs Processing_Hours: Strong positive (r ≈ 0.95)
- Complexity_Score vs Processing_Hours: Strong positive (r ≈ 0.85)
- Processing_Hours vs Litigant_Satisfaction: Moderate negative (r ≈ -0.80)

**Columns:**
- `Case_ID`: Case identifier (CV-2026-XXX)
- `Pages_Filed`: Number of pages in filing
- `Processing_Hours`: Staff hours to process
- `Staff_Assigned`: Number of staff assigned
- `Complexity_Score`: Case complexity (1-5)
- `Litigant_Satisfaction`: Litigant satisfaction rating (1-5)

---

### sample_pareto.csv

**Context:** Defects identified during case filing quality review.

**Expected result:** Top 4 categories account for ~80% of all defects.

**Columns:**
- `Defect_Category`: Type of filing defect
- `Count`: Number of occurrences
- `Department`: Organizational unit

---

### sample_court_operations.csv

**Context:** Comprehensive court case management data.

**Suitable for:**
- 4-Up Chart (Processing_Days)
- Control Charts (Processing_Days over time)
- ANOVA (by Division or Case_Type)
- Correlation (Pages vs Processing_Days)
- Box Plot (by Division)
- Pareto (by Case_Type)

---

## Pro Sample Details

### pro/sample_msa_gage_rr.csv

**Context:** Quality review of case files by supervisory staff — assessing whether different supervisors rate case file completeness consistently.

**Study design:**
- 10 case files
- 3 supervisors (Adams, Baker, Chen)
- 3 review rounds per file-supervisor combination
- 90 total completeness scores

**Tolerance:** 20 points (acceptable range 80-100)

**Expected results:**
- High %Contribution from Case File Variation (good measurement system)
- Low %Contribution from Reviewer Variation (supervisors agree)

---

### pro/sample_doe_factorial.csv

**Context:** 2³ factorial experiment to optimize court case processing.

**Factors:**
- Staff_Level: -1 (Standard staffing), +1 (Enhanced staffing)
- Filing_Method: -1 (Paper), +1 (Electronic)
- Case_Complexity: -1 (Simple), +1 (Complex)

**Response:** Processing_Days

**Expected results:**
- Main effects: All three factors significant
- Interaction: Staff_Level × Case_Complexity significant

---

### pro/sample_hypothesis_tests.csv

**Context:** Comparing three workflow approaches for case processing.

**Groups:**
- New_Workflow: Redesigned process (pilot program)
- Standard_Process: Current standard operating procedure
- Legacy_System: Old system still in limited use

**Suitable tests:**
- Mann-Whitney U: Compare New_Workflow vs Standard_Process
- Kruskal-Wallis: Compare all three groups
- Chi-Square: Outcome (Complete/Incomplete) by Process_Method

---

### pro/sample_regression.csv

**Context:** Predicting case processing time from multiple factors.

**Response (Y):** Processing_Time

**Predictors (X):**
- Staff_Count: Clerks assigned (negative effect)
- Case_Complexity: 1-5 scale (positive effect)
- Digital_Filing: 1=yes, 0=no (negative effect)
- Experience_Years: Staff experience (negative effect)
- Caseload: Current caseload (positive effect)

**Expected R²:** 0.85-0.95

---

### pro/sample_cusum_ewma.csv

**Context:** Weekly monitoring of civil division average processing time.

**Built-in shift:** Process mean increases from 15.0 to approximately 16.5 days starting at week 21 (gradual drift).

**Target:** 15 days

**CUSUM settings:** k=0.5, h=4-5
**EWMA settings:** λ=0.2, L=2.7

**Expected result:** CUSUM or EWMA detects drift around week 25-28.

---

### pro/sample_lean_metrics.csv

**Context:** End-to-end court case processing workflow metrics.

**Process steps:** Filing Receipt → Initial Review → Document Check → Assignment → Scheduling → Hearing Prep → Hearing → Decision Draft → Review → Final Order → Distribution → Closing

**Suitable calculations:**
- DPMO: Defects per Million Opportunities by step
- RTY: Rolled Throughput Yield across entire process
- First Pass Yield: By individual step
- Cycle Time Analysis: Bottleneck identification

---

### pro/sample_fmea.csv

**Context:** Failure Mode and Effects Analysis for court case processing.

**Pre-populated failure modes across:**
- Filing (missing documents, incorrect fees)
- Initial Review (missed deadlines, wrong classification)
- Document Processing (lost documents, data entry errors)
- Scheduling (double booking, incorrect notices)
- Hearing (recording failures, late starts)
- Order Entry (typos, wrong party names)
- Distribution (wrong recipients, delays)
- Closing (incomplete files)

**Highest RPN items:** Scheduling "Late start" (210) and Filing "Missing Signature" (210)

---

## Usage Instructions

### Loading Sample Data

1. Launch CiviQual Stats
2. Click **Load Data File** or press **Ctrl+O**
3. Navigate to the `samples` folder
4. Select the appropriate sample file
5. Choose the analysis column when prompted

### Recommended Learning Path

**Free Tier:**
1. `sample_court_operations.csv` → 4-Up Chart
2. `sample_control_chart.csv` → I-Chart with Western Electric rules
3. `sample_capability.csv` → Capability Analysis (set LSL=14.5, USL=15.5)
4. `sample_anova.csv` → ANOVA (Division as factor)
5. `sample_pareto.csv` → Pareto Chart

**Pro Tier:**
1. `pro/sample_msa_gage_rr.csv` → MSA (Gage R&R)
2. `pro/sample_doe_factorial.csv` → DOE
3. `pro/sample_cusum_ewma.csv` → CUSUM/EWMA
4. `pro/sample_regression.csv` → Multiple Regression
5. `pro/sample_lean_metrics.csv` → Lean Calculators
6. `pro/sample_fmea.csv` → FMEA Worksheet

---

## File Specifications

| Property | Value |
|----------|-------|
| Format | CSV (comma-separated values) |
| Encoding | UTF-8 |
| Header row | Yes (first row contains column names) |
| Decimal separator | Period (.) |
| Date format | YYYY-MM-DD |
| Missing values | Empty cell |

---

## Public Sector Context Note

All sample data in CiviQual Stats uses **fictional data** representing typical scenarios in:

- **Courts:** Case processing, filings, hearings, clerk operations
- **Municipal government:** Permits, inspections, service requests
- **Public health:** Service delivery, response times
- **Benefits administration:** Application processing
- **Public records:** FOIA requests, document management

No actual government data is used. All names, case numbers, and metrics are simulated for training and demonstration purposes.

---

© 2026 A Step in the Right Direction LLC
