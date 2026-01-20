# WATSON for Lean Six Sigma

**Workbench for Analysis, Testing, Statistics, Optimization & Navigation**

Version 1.3.0 - Section 508 Accessibility Release

---

## Overview

WATSON is a statistical analysis tool designed for Lean Six Sigma practitioners in government and public service organizations. It provides the analytical capabilities needed to complete DMAIC projects, replicating the methods taught in Lean Six Sigma Green Belt and Black Belt training.

### About the Name

WATSON (Workbench for Analysis, Testing, Statistics, Optimization & Navigation) for Lean Six Sigma is statistical analysis software not affiliated with IBM Corporation or IBM Watson.

---

## What's New in Version 1.3.0

This release includes **Section 508 accessibility compliance**, **CPI Process Diagram tools**, and **colorblind-friendly visualizations**.

### Colorblind-Friendly Color Scheme

All charts use the Wong colorblind-safe palette (Wong, B. *Nature Methods* 8, 441, 2011):
- **Blue (#0072B2)** - Primary data color
- **Orange (#E69F00)** - Secondary/fit lines
- **Green (#009E73)** - Center lines/targets
- **Vermillion (#D55E00)** - Control limits/alerts
- **Purple (#CC79A7)** - Additional series
- **Sky Blue (#56B4E9)** - Light accents

### Watson 4-Up Chart (Corrected)

The 4-Up Chart now displays the correct four quadrants:
1. **Statistical Summary** - Histogram with normal curve overlay
2. **Probability Plot** - Normal probability plot with R² value
3. **I-Chart** - Individuals control chart with Western Electric rules
4. **Capability Analysis** - Process capability with spec limits

### New Probability Plot Tab

- Compare multiple data series on a single probability plot
- Select multiple columns using Ctrl+Click
- Individual normality statistics for each series
- Anderson-Darling test results

### Capability Analysis Chart

### Capability Analysis Chart

The Capability Analysis tab now includes a visual chart showing:
- Distribution histogram with normal curve
- LSL, USL, and Target lines
- Shaded out-of-spec regions
- PPM defect estimates

**Cp=1.0 Natural Tolerance Option:**
- Check "Show Cp=1.0 Natural Tolerance Limits" to display what specification limits would result in Cp=1.0 based on current process variation
- Natural LSL = Mean - 3σ
- Natural USL = Mean + 3σ
- Useful for setting realistic specifications or understanding required variation reduction

**Enhanced Interpretation:**
- Detailed explanation of Cp, Cpk, Cpu, and Cpl indices
- Capability ratings (Capable ≥1.33, Marginal ≥1.0, Not Capable <1.0)
- Centering analysis (identifies shift toward upper or lower spec)
- Required standard deviation reduction to achieve Cp=1.0

### Accessibility Improvements

| Feature | Description |
|---------|-------------|
| **Enhanced Focus Indicators** | Blue outline on buttons, light blue background on focused inputs |
| **Accessible Names** | All interactive controls have programmatic names for screen readers |
| **Accessible Descriptions** | Detailed descriptions explain control purpose and keyboard shortcuts |
| **Label Associations** | Form labels properly associated with controls using setBuddy() |
| **Tooltips** | All input fields include helpful tooltips |
| **Keyboard Shortcuts Dialog** | Help → Keyboard Shortcuts shows all available shortcuts |
| **Accessibility Info Dialog** | Help → Accessibility Information explains all features |
| **Screen Reader Support** | Compatible with NVDA, JAWS, and Windows Narrator |

### New Process Diagram Tools (CPI Project Tools)

| Diagram | DMAIC Phase | Description |
|---------|-------------|-------------|
| **SIPOC Diagram** | Define | Suppliers → Inputs → Process → Outputs → Customers |
| **Process Map** | Define | Flowchart with Start/End [S], Decision [D], and process steps |
| **RACI Matrix** | Define | Responsible, Accountable, Consulted, Informed roles matrix |
| **Swim Lane Diagram** | Analyze | Process flow across roles/departments showing handoffs |
| **Value Stream Map** | Analyze | Process flow with cycle time, wait time, and efficiency |
| **Fishbone Diagram** | Analyze | Cause-and-effect with CPI-specific categories |

---

## Complete Feature List

### Statistical Analysis Tools

| Feature | DMAIC Phase | Description |
|---------|-------------|-------------|
| **Watson 4-Up Chart** | Measure | Four complementary views: Statistical Summary, Probability Plot, I-Chart, Capability Analysis |
| **Descriptive Statistics** | Measure | Mean, median, mode, std dev, variance, quartiles, skewness, kurtosis, Anderson-Darling test |
| **Control Charts** | Measure/Control | I-Chart and I-MR Chart with all 4 Western Electric rules |
| **Capability Analysis** | Measure/Analyze | Cp, Cpk, Cpu, Cpl indices with capability chart visualization |
| **Probability Plot** | Measure | Multi-series normality assessment (X=value, Y=percentage) with Anderson-Darling test |
| **ANOVA with Box Plots** | Analyze | One-way ANOVA with F-statistic, p-value, eta-squared, grouped box plots |
| **Correlation Analysis** | Analyze | Pearson r, R-squared, p-value, scatter plot with regression line |
| **Run Chart** | Measure/Analyze | Sequential plot with median line, runs analysis for non-random patterns |
| **Histogram** | Measure | Distribution visualization with normal curve overlay, skewness, kurtosis |
| **Box Plot** | Measure | Quartile visualization with outlier detection, IQR calculation |
| **Pareto Analysis** | Analyze | 80/20 rule identifying vital few vs trivial many |
| **Pre/Post Analysis** | Control | Two-sample t-test, Cohen's d effect size |

### Utility Tools

| Feature | Description |
|---------|-------------|
| **Data Sampling** | Random sample selection (configurable, default 30 points) |
| **Split Worksheet** | Split data by categorical factor/rational subgroup |
| **ROI Calculator** | Calculate project ROI with multi-year projections |
| **Report Generation** | Export analysis to Word (.docx) or HTML |
| **Chart Export** | Export all charts to PNG files |
| **User Guide** | Downloadable comprehensive documentation |

---

## New in v1.3: Statistical Tools Details

### Correlation Analysis
Examines the relationship between two numeric variables:
- Pearson correlation coefficient (r)
- R-squared (coefficient of determination)
- P-value for significance testing
- Scatter plot with optional regression line
- 95% prediction band
- Interpretation of correlation strength (negligible/weak/moderate/strong/very strong)

**Important**: Correlation does not prove causation. Use as a clue for further investigation.

### Run Chart
Sequential data plot for initial stability assessment (simpler than I-Chart):
- Data plotted in time sequence
- Median line (center line)
- Runs analysis test for non-random patterns
- Color-coded points above/below median
- P-value for randomness test

**Use Case**: Quick check for trends or shifts before formal SPC analysis.

### Histogram
Distribution visualization with comprehensive statistics:
- Configurable number of bins (or automatic)
- Optional normal distribution curve overlay
- Mean and median lines
- Skewness and kurtosis values
- Full descriptive statistics panel

### Box Plot (Standalone)
Quartile-based distribution summary:
- Median, Q1, Q3, IQR
- Whiskers showing data range
- Outlier detection (1.5 × IQR rule)
- Optional jittered data points
- Mean marker

---

## System Requirements

- Windows 10 or later (64-bit)
- 4 GB RAM minimum (8 GB recommended)
- 200 MB available disk space
- 1280x800 minimum display resolution

---

## Installation

### Using the Installer (Recommended)

1. Download `Watson_Setup_1.3.0.exe`
2. Run the installer
3. Follow the installation wizard
4. Launch Watson from the Start Menu or Desktop shortcut

### Enterprise Deployment (MSI)

Watson provides an MSI installer for both individual users and enterprise deployment:

**Interactive Installation (Individual Users):**
- Double-click `Watson_1.3.0.msi` to launch the installation wizard
- Standard Windows installer with Add/Remove Programs integration

**Silent Installation (Enterprise):**
```powershell
msiexec /i Watson_1.3.0.msi /qn
```

**With Logging:**
```powershell
msiexec /i Watson_1.3.0.msi /qn /l*v C:\Logs\watson.log
```

**Supported Deployment Methods:**
- Group Policy (GPO)
- Microsoft Endpoint Configuration Manager (SCCM/MECM)
- Microsoft Intune
- Any MSI-compatible deployment tool

See `installer/msi/MSI_DEPLOYMENT_GUIDE.md` for complete deployment instructions.

### From Source

1. Ensure Python 3.9 or higher is installed
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run Watson:
   ```
   python main.py
   ```

---

## Keyboard Shortcuts

### File Operations
| Shortcut | Action |
|----------|--------|
| Ctrl+O | Open data file |
| Ctrl+S | Save report |
| Ctrl+E | Export chart |
| Ctrl+Q | Quit application |

### Navigation
| Shortcut | Action |
|----------|--------|
| Tab | Move to next control |
| Shift+Tab | Move to previous control |
| Ctrl+Tab | Switch to next tab |
| Alt+1 to Alt+9 | Jump to tab 1-9 |

### Analysis
| Shortcut | Action |
|----------|--------|
| Ctrl+G | Generate 4-Up Chart |
| Ctrl+D | Descriptive Statistics |
| Ctrl+I | Generate I-Chart |
| Ctrl+P | Pareto Chart |

### Help
| Shortcut | Action |
|----------|--------|
| F1 | Quick Reference |
| Ctrl+? | Keyboard Shortcuts |
| Ctrl+Shift+F1 | Accessibility Information |

---

## Process Diagram Usage

### SIPOC Diagram
Enter suppliers, inputs, process steps (3-5), outputs, and customers in separate fields. Click Generate to create the diagram.

### Process Map
Enter process steps (one per line):
- `[S] Start` or `[S] End` for Start/End ovals
- `[D] Question?` for Decision diamonds
- Plain text for process rectangles

### RACI Matrix
1. Enter roles separated by commas
2. Enter tasks with assignments: `Task Name | R,A,C,I`
   - R = Responsible (does the work)
   - A = Accountable (final authority)
   - C = Consulted (provides input)
   - I = Informed (kept updated)

### Swim Lane Diagram
Format: `Lane Name | Step Description`
- Use `[S]` prefix for Start/End
- Use `[D]` prefix for Decision

### Value Stream Map
Format: `Step Name, Cycle Time, Wait Time`
- Times in minutes
- Calculates: Lead Time, Process Efficiency

### Fishbone Diagram
1. Enter the effect/problem
2. Add causes under each CPI category:
   - Policy/Standards
   - Materials
   - Process/Procedures
   - Physical Environment
   - People
   - IT Systems/Equipment

---

## Accessibility

Watson 1.3 meets **Section 508** and **WCAG 2.0 Level AA** accessibility standards.

### Screen Reader Compatibility
- NVDA (recommended)
- Windows Narrator
- JAWS

### Visual Accessibility
- High-contrast focus indicators
- 4.5:1 minimum contrast ratio for all text
- Compatible with Windows High Contrast themes
- Supports display scaling up to 200%

### Motor Accessibility
- Full keyboard navigation
- No time limits on operations
- Large click targets (44x44 pixels minimum)

For accessibility feedback: accessibility@qualityincourts.com

---

## License

Watson is provided **FREE** for:
- Government agencies (federal, state, local, tribal)
- Courts and judicial organizations
- Public educational institutions
- 501(c)(3) nonprofit organizations

**Commercial use requires a separate license.**

Contact: www.qualityincourts.com

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.3.0 | December 2025 | Section 508 Accessibility + CPI Process Diagrams |
| 1.2.0 | November 2025 | Windows installer, license acceptance dialog |
| 1.1.0 | October 2025 | Watson 4-Up Chart, brand identity |
| 1.0.0 | September 2025 | Initial release |

---

*Copyright © 2025 A Step in the Right Direction LLC. All Rights Reserved.*
