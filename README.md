# CiviQual

**Quality Analytics for Public Service**

Version 1.0.0 - Initial Public Release

---

## Overview

CiviQual is a statistical analysis tool designed for Lean Six Sigma practitioners in government and public service organizations. It provides the analytical capabilities needed to complete DMAIC projects, replicating the methods taught in Lean Six Sigma Green Belt and Black Belt training.

### About CiviQual

CiviQual (pronounced "SIV-i-qual") combines "Civic" and "Quality" to emphasize its focus on quality improvement in public service. The methodology is based on the exploratory data analysis approach developed by Dr. Gregory H. Watson.

**Free for government, courts, and nonprofit organizations.**

---

## What's New in Version 1.0.0

This initial release includes:

- **Full Windows dark mode support** - Automatic system theme detection
- **Section 508 accessibility compliance**
- **CPI Process Diagram tools**
- **Colorblind-friendly visualizations**
- **Enhanced I-Chart with Western Electric rule filtering**
- **Improved capability analysis with normality checking**

### Dark Mode Support

CiviQual automatically detects your Windows theme setting and adapts the interface accordingly. All UI elements, charts, and text areas support both light and dark modes.

### Colorblind-Friendly Color Scheme

All charts use the Wong colorblind-safe palette (Wong, B. *Nature Methods* 8, 441, 2011):
- **Blue (#0072B2)** - Primary data color
- **Orange (#E69F00)** - Secondary/fit lines
- **Green (#009E73)** - Center lines/targets
- **Vermillion (#D55E00)** - Control limits/alerts
- **Purple (#CC79A7)** - Additional series
- **Sky Blue (#56B4E9)** - Light accents

### CiviQual 4-Up Chart

The signature 4-Up Chart displays four complementary views of your data:
1. **Statistical Summary** - Histogram with normal curve overlay
2. **Probability Plot** - Normal probability plot with R² value
3. **I-Chart** - Individuals control chart with Western Electric rules
4. **Capability Analysis** - Process capability with spec limits

### Enhanced I-Chart Features

- **Rule Filtering** - Select which Western Electric tests to apply (Tests 1-4)
- **Point Labels** - Flagged points show which test(s) triggered them (e.g., "T1", "T1,2")
- **Detailed Reports** - Analysis output lists each flagged point with its test failures

### Capability Analysis Improvements

- **Normality Warning** - Anderson-Darling test alerts when data is non-normal
- **LSL Clamping** - For all-positive data, natural LSL is clamped to 0 when appropriate
- **Axis Constraints** - Charts don't show negative values for positive-only data
- **Cpk Display** - All capability indices (Cp, Cpk, Cpu, Cpl) prominently displayed

### Chart Export Fix

Charts can now be exported properly via File → Export Chart (Ctrl+E). Supports PNG and JPEG formats.

---

## Complete Feature List

### Statistical Analysis Tools

| Feature | DMAIC Phase | Description |
|---------|-------------|-------------|
| CiviQual 4-Up Chart | Measure | Four-quadrant exploratory data analysis |
| Descriptive Statistics | Measure | Mean, median, std dev, skewness, kurtosis |
| Control Charts | Measure/Control | I-Chart, MR Chart, I-MR Chart |
| Capability Analysis | Analyze | Cp, Cpk, Pp, Ppk, PPM calculations |
| Probability Plot | Analyze | Normal probability with confidence bands |
| ANOVA | Analyze | One-way analysis of variance |
| Correlation Analysis | Analyze | Scatter plot with regression |
| Run Chart | Control | Time series with centerline |
| Histogram | Measure | Distribution visualization |
| Box Plot | Analyze | Outlier detection and comparison |
| Pareto Analysis | Analyze | 80/20 rule visualization |

### Process Diagram Tools (CPI)

| Diagram | DMAIC Phase | Description |
|---------|-------------|-------------|
| SIPOC Diagram | Define | Suppliers → Inputs → Process → Outputs → Customers |
| Process Map | Define | Flowchart with decision points |
| RACI Matrix | Define | Responsibility assignment matrix |
| Swim Lane Diagram | Analyze | Cross-functional process flow |
| Value Stream Map | Analyze | Process efficiency analysis |
| Fishbone Diagram | Analyze | Cause-and-effect analysis |

### Other Tools

| Feature | Description |
|---------|-------------|
| ROI Calculator | Return on investment for improvement projects |
| Data Sampling | Random sampling with seed control |
| Split Worksheet | Divide data by category |

---

## Accessibility (Section 508)

CiviQual meets Section 508 of the Rehabilitation Act:

- Keyboard navigation for all functions
- Screen reader compatible (NVDA, JAWS, Windows Narrator)
- High contrast support
- Focus indicators on all controls
- Accessible names and descriptions

**Help → Accessibility Information** provides full details.

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+O | Open data file |
| Ctrl+G | Generate CiviQual 4-Up Chart |
| Ctrl+E | Export current chart |
| Ctrl+S | Save report |
| Ctrl+Q | Quit application |
| Alt+1-9 | Switch to tab 1-9 |
| F1 | User guide |

---

## Installation

### Requirements

- Windows 10/11 (64-bit)
- 4 GB RAM minimum
- 200 MB disk space

### Running from Source

```bash
pip install -r requirements.txt
python main.py
```

### Building Installer

See `installer/` directory for build instructions.

---

## Data Formats

CiviQual supports:
- CSV files (.csv)
- Excel files (.xlsx, .xls)

Sample data files are included in the `samples/` directory.

---

## License

Copyright © 2026 A Step in the Right Direction LLC. All Rights Reserved.

Free for use by government agencies, courts, and nonprofit organizations.

---

## Acknowledgments

CiviQual is based on the exploratory data analysis methodology developed by Dr. Gregory H. Watson, a leading international quality expert who has contributed significantly to the advancement of Lean Six Sigma practices worldwide.

---

*CiviQual - Quality Analytics for Public Service*
