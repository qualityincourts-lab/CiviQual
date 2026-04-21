# CiviQual Stats Pro Features

CiviQual Stats Pro extends the free tier (Yellow Belt and basic Green Belt tools) with advanced statistical analysis, quality planning, and Lean Six Sigma tools designed for advanced Green Belt and Black Belt practitioners.

## Feature Overview

### Measurement System Analysis (MSA)
- **Gage R&R (Crossed Design)** - ANOVA method with variance components
- **%Contribution, %Study Variation, %Tolerance** - Standard MSA metrics
- **Number of Distinct Categories (ndc)** - Measurement discrimination assessment
- **Components of Variation Bar Charts** - Visual variance breakdown
- **Assessment Criteria** - ACCEPTABLE (<10%), MARGINAL (10-30%), UNACCEPTABLE (>30%)

### Hypothesis Testing (Non-Parametric)
- **Chi-Square Goodness of Fit** - Test distribution assumptions
- **Chi-Square Independence** - Test association with Cramér's V effect size
- **Mann-Whitney U Test** - Two-sample comparison with effect size r
- **Kruskal-Wallis Test** - Multi-group comparison with η² effect size
- **Wilcoxon Signed-Rank** - Paired/one-sample test
- **Mood's Median Test** - Robust median comparison
- **Test Selection Guidance** - Recommends appropriate test based on data

### Sample Size & Power Analysis
- **One-Sample Mean** - Sample size for t-tests
- **Two-Sample Means** - With unequal group ratios
- **One/Two Proportions** - Sample size for proportion tests
- **Power Curves** - Visual power analysis
- **Minimum Detectable Effect** - Given sample size
- **Quick Reference Table** - Common scenarios

### Advanced Capability Analysis
- **Pp/Ppk (Long-term)** - Overall capability indices
- **Cpm (Taguchi Index)** - Target-centered capability
- **Box-Cox Transformation** - Automatic λ optimization with normality tests
- **Non-Normal Capability** - Percentile, Weibull, and Lognormal methods
- **Capability Comparison** - All methods on same data

### Design of Experiments (DOE)
- **Full Factorial Design** - 2-4 factors with replicates
- **Randomization** - Standard run order randomization
- **Main Effects Calculation** - With statistical significance
- **Interaction Effects** - Two-way and three-way
- **Pareto of Effects** - Ranked effect magnitudes
- **ANOVA Table** - Complete analysis of variance
- **Prediction** - Response prediction from model

### Multiple Regression
- **Up to 5 Predictors** - Full multiple regression
- **VIF Analysis** - Multicollinearity detection
- **Coefficient Confidence Intervals** - With t-tests
- **Residual Diagnostics** - Cook's D, leverage, Durbin-Watson
- **Prediction Intervals** - CI and PI for new observations
- **Stepwise Selection** - Forward and backward selection

### Advanced Control Charts
- **CUSUM Chart** - Cumulative sum for small shifts
- **EWMA Chart** - Exponentially weighted moving average
- **Time-Varying Limits** - Exact EWMA limits
- **Design Parameters** - Optimal k, h, λ, L selection
- **ARL Comparison** - Sensitivity comparison across chart types

### Lean Calculators
- **Process Sigma Calculator** - With 1.5σ shift
- **DPMO Calculator** - DPO, DPU, DPMO
- **Rolled Throughput Yield (RTY)** - Multi-step yield
- **First Pass Yield (FPY)** - Single-step yield
- **Takt Time Calculator** - Demand-based pacing
- **Cycle Time Analysis** - Statistical summary
- **Little's Law Calculator** - WIP, throughput, lead time
- **Cost of Poor Quality (COPQ)** - Four-category model
- **Sigma Lookup Table** - Quick reference
- **Process Efficiency (PCE)** - Value-added time analysis
- **OEE Calculator** - Overall Equipment Effectiveness

### Root Cause Analysis
- **Fishbone Diagram Builder** - 6M, 4P, and custom frameworks
- **Court-Specific Categories** - People, Process, Technology, Policy, Resources, Environment
- **Sub-Causes** - Hierarchical cause structure
- **Text Export** - ASCII diagram output
- **5 Whys Template** - Structured root cause drill-down
- **Question Prompts** - Suggested follow-up questions
- **Validation** - Completeness checking

### Solution Tools
- **Pugh Matrix** - Concept selection against baseline
- **Weighted Scoring** - Customizable criterion weights
- **Impact/Effort Matrix** - Four-quadrant prioritization
- **Quick Wins Identification** - High impact, low effort
- **Priority Scoring** - Impact/effort ratio ranking

### Planning Tools
- **FMEA Worksheet** - Full Failure Mode and Effects Analysis
- **RPN Calculation** - Risk Priority Number
- **Severity/Occurrence/Detection Scales** - 1-10 ratings
- **Action Tracking** - Before/after RPN comparison
- **High-Risk Filtering** - Focus on critical failure modes
- **Control Plan Template** - Process control documentation
- **FMEA-to-Control Plan** - Automatic conversion

### Data Tools
- **Grubbs Test** - Single outlier detection
- **Iterative Grubbs** - Multiple outlier detection
- **IQR Method** - Robust outlier detection (k=1.5 and k=3.0)
- **Z-Score Method** - Standard and Modified Z-scores
- **Method Comparison** - Compare all methods
- **Missing Data Analysis** - Column and row analysis
- **Missing Pattern Assessment** - MCAR/MAR/MNAR heuristics
- **Recommendations** - Imputation guidance

### Chart Editor (Pro)
- **Reference Lines** - Horizontal and vertical with labels
- **Annotations** - Text annotations with positioning
- **Shaded Regions** - Specification highlighting
- **Color Customization** - Full color control
- **Export Options** - PNG, SVG, PDF

## License

CiviQual Stats Pro requires a valid license key for activation.

### Activation
1. Open CiviQual Stats
2. Go to Help → Enter License Key
3. Paste your license key
4. Click Activate

### License Types
- **Perpetual** - One-time purchase, never expires
- **Annual** - Subscription, renewable yearly

### Pricing
- Suggested retail: $149 (perpetual)
- Under federal micro-purchase threshold for easy procurement

## Integration Notes

All Pro features are integrated into the main CiviQual Stats application:
- Pro features are visible but disabled without a license
- Clicking a disabled Pro feature shows an upgrade prompt
- License validation is offline (no internet required)
- License is stored locally at:
  - Windows: `%LOCALAPPDATA%\CiviQualStats\license.key`
  - macOS/Linux: `~/.civiqual-stats/license.key`

## Requirements

No additional dependencies beyond standard CiviQual Stats requirements. The `cryptography` library is recommended for optimal license security but not strictly required.

---

© 2026 A Step in the Right Direction LLC
Quality in Courts | qualityincourts.com
