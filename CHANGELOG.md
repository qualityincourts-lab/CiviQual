# CiviQual Stats Changelog

## v1.2.0 - CiviQual Stats Pro Release

**Release Date:** April 2026

### Product Family Announcement

CiviQual is now the master brand for a suite of public-sector quality management tools. This application has been renamed from **CiviQual** to **CiviQual Stats** to reflect its specific focus on statistical process control.

Future products in the CiviQual Suite will include:
- **CiviQual Tier** - G1:2026 maturity assessment (in development)
- **CiviQual Risk** - Enterprise risk management platform (planned)

### Branding Updates

- Product renamed from "CiviQual" to "CiviQual Stats"
- New tagline: "Statistical Process Control for Public-Sector Quality Management"
- Paid tier renamed from "CiviQual Pro" to "CiviQual Stats Pro"
- Updated all UI text, window titles, and documentation
- Config directory renamed from `CiviQual` to `CiviQualStats`
- MSI installer renamed to `CiviQualStats_1.2.0.msi`

### CiviQual Stats Pro Features (New)

#### Measurement System Analysis (MSA)
- Gage R&R (Crossed Design) with ANOVA method
- %Contribution, %Study Variation, %Tolerance
- Number of Distinct Categories (ndc)
- Components of Variation bar charts

#### Hypothesis Testing (Non-Parametric)
- Chi-Square Goodness of Fit and Independence tests
- Mann-Whitney U Test with effect size
- Kruskal-Wallis Test with η² effect size
- Wilcoxon Signed-Rank Test
- Mood's Median Test

#### Sample Size & Power Analysis
- One-sample and two-sample mean calculations
- Proportion sample size calculators
- Power curves
- Minimum detectable effect calculator

#### Advanced Capability Analysis
- Pp/Ppk (Long-term capability)
- Cpm (Taguchi capability index)
- Box-Cox transformation with automatic λ optimization
- Non-normal capability (Percentile, Weibull, Lognormal)

#### Design of Experiments (DOE)
- 2-4 factor full factorial design
- Main effects and interaction calculation
- Pareto of effects
- ANOVA table and model statistics

#### Multiple Regression
- Up to 5 predictors
- VIF (Variance Inflation Factor) for multicollinearity
- Residual diagnostics (Cook's D, leverage, Durbin-Watson)
- Prediction and confidence intervals
- Stepwise selection (forward/backward)

#### Advanced Control Charts
- CUSUM (Cumulative Sum) charts
- EWMA (Exponentially Weighted Moving Average) charts
- Design parameter calculators
- ARL sensitivity comparison

#### Lean Calculators
- Process Sigma calculator (with 1.5σ shift)
- DPMO, DPO, DPU calculations
- Rolled Throughput Yield (RTY)
- First Pass Yield (FPY)
- Takt Time calculator
- Little's Law calculator
- Cost of Poor Quality (COPQ)
- OEE (Overall Equipment Effectiveness)

#### Root Cause Analysis Tools
- Fishbone Diagram Builder (6M, 4P, Court-specific frameworks)
- 5 Whys Template with validation

#### Solution Tools
- Pugh Matrix for concept selection
- Impact/Effort Matrix with quadrant prioritization

#### Planning Tools
- FMEA Worksheet with RPN calculation
- Control Plan template
- FMEA-to-Control Plan conversion

#### Data Tools
- Outlier detection (Grubbs, IQR, Z-score methods)
- Missing data analysis and recommendations

#### Chart Editor (Pro)
- Reference lines (horizontal/vertical)
- Text annotations
- Shaded regions
- Export to PNG, SVG, PDF

### License System

- Offline RSA cryptographic license validation
- Pro features visible but disabled without license
- License stored locally (no internet required)
- Perpetual and annual license types

### Technical Notes

- Version: 1.2.0
- Installer: CiviQualStats_1.2.0.msi
- Minimum Python: 3.9+
- Framework: PySide6
- Certificate: A Step in the Right Direction LLC (Certum, expires Jan 2027)

---

## v1.1.0 - Section 508 Accessibility Release

**Release Date:** April 2026

### Rebranding

- Complete rebrand from Watson to CiviQual
- New tagline: "Quality Analytics for Public Service"
- Updated all UI text, window titles, and references
- Renamed icon and logo files (civiqual_icon.ico, civiqual_logo.svg)
- Updated copyright to 2026
- Removed IBM Watson disclaimer (no longer applicable)

### Bug Fixes

#### ANOVA Analysis
- **Fixed:** "List index out of range" error when running ANOVA with groups containing no data
- **Added:** Tukey HSD post-hoc analysis showing which specific group pairs differ significantly
- **Added:** Identification of groups most likely causing statistical significance
- **Fixed:** ANOVA button now correctly switches to ANOVA tab (was incorrectly switching to Probability Plot)

#### Control Charts
- **Added:** Western Electric Test 5 - 6 consecutive points steadily increasing or decreasing (trend detection)
- **Added:** Western Electric Test 6 - 14 consecutive points alternating up and down
- **Added:** Test 5 and Test 6 checkboxes in Control Charts tab
- **Added:** "Export Flagged Points" button - exports complete data rows for all flagged observations with test indicators (T1, T2, etc.)

#### CiviQual 4-Up Chart
- **Fixed:** I-Chart quadrant now uses only Test 1 (points beyond 3σ) as intended for exploratory analysis
- **Added:** 80% reference line automatically displayed on Probability Plot quadrant
- **Added:** 80th percentile value shown in statistics box

#### Probability Plot (Standalone)
- **Added:** "Show 80% Line" checkbox option
- **Added:** 80th percentile values displayed in statistics output when enabled

#### Data Sampling
- **Added:** "Select by Observation" input field - enter specific row numbers (e.g., "1,5,10-15,20")
- **Added:** "Export entire data row" checkbox - exports all columns for sampled observations
- **Improved:** Export now includes all data columns when full row option is selected

---

*CiviQual Stats - Statistical Process Control for Public-Sector Quality Management*
*Part of the CiviQual Suite*
*© 2026 A Step in the Right Direction LLC*
