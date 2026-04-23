# CiviQual Stats

**Statistical Process Control for Public-Sector Quality Management**

Version 2.0.0 — DMAIC Edition

---

## Overview

CiviQual Stats is a desktop statistical analysis application designed for Lean Six Sigma practitioners in government agencies, courts, and public service organizations. It provides Yellow Belt through Black Belt statistical tools organized by DMAIC phase for intuitive workflow.

**Part of the CiviQual Suite** — Quality management tools for the public sector.

---

## Features

### DMAIC Phase Organization (v2.0)

Tools are organized by Lean Six Sigma DMAIC phases:

| Phase | Free Tools | Pro Tools |
|-------|------------|-----------|
| **Define** | SIPOC, Process Map, RACI, Data Sampling, Split Worksheet | — |
| **Measure** | 4-Up Chart, Descriptive Stats, Control Charts, Capability, Probability Plot, Histogram, Box Plot, Run Chart | ★ MSA, ★ Sample Size, ★ Advanced Capability |
| **Analyze** | ANOVA, Correlation, Pareto, Swim Lane, VSM, Fishbone | ★ Hypothesis Tests, ★ DOE, ★ Regression, ★ Root Cause, ★ Data Tools |
| **Improve** | ROI Calculator | ★ Solution Tools, ★ Lean Calculators |
| **Control** | — | ★ CUSUM/EWMA, ★ Planning Tools, ★ Chart Editor |

### Free Tier (Yellow Belt + Basic Green Belt)

- **Control Charts**: I-Chart, MR-Chart, I-MR with Western Electric rules (1-6)
- **Capability Analysis**: Cp, Cpk, Pp, Ppk with specification limits
- **Statistical Analysis**: ANOVA, correlation, descriptive statistics
- **Visualization**: Histogram, box plot, run chart, Pareto chart
- **Process Diagrams**: SIPOC, process map, RACI matrix, swim lane, VSM, fishbone
- **Data Tools**: Sampling, split worksheet

### Pro Tier (Advanced Green Belt + Black Belt)

- **Measurement System Analysis**: Gage R&R studies
- **Design of Experiments**: Full and fractional factorial
- **Hypothesis Testing**: t-tests, Mann-Whitney, Kruskal-Wallis, Chi-Square
- **Advanced Capability**: Ppk, non-normal distributions, confidence intervals
- **Regression**: Multiple regression with diagnostics
- **Advanced Control Charts**: CUSUM, EWMA for detecting small shifts
- **Lean Calculators**: DPMO, RTY, OEE, Takt Time
- **Planning Tools**: FMEA worksheet, Control Plan
- **Project Sessions**: Save/resume analysis projects (.civiqual files)
- **Chart Editor**: Customize colors, labels, formatting

---

## Installation

### Windows (MSI Installer)

1. Download `CiviQual_2.0.0.msi` from the Releases page
2. Run the installer
3. Launch from Start Menu or Desktop shortcut

### From Source

```bash
# Clone repository
git clone https://github.com/qualityincourts-lab/CiviQual.git
cd CiviQual

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

### Requirements

- Python 3.9 or higher
- PySide6 6.5.0 or higher
- pandas, numpy, scipy, matplotlib

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Alt+D | Define phase |
| Alt+M | Measure phase |
| Alt+A | Analyze phase |
| Alt+I | Improve phase |
| Alt+C | Control phase |
| 1-9 | Select tool within phase |
| Ctrl+O | Open data file |
| Ctrl+S | Save project (Pro) |
| Ctrl+E | Export chart |
| F5 | Run analysis |
| F1 | Help |
| F11 | Full screen |

---

## Sample Data

Sample data files are included demonstrating public-sector quality management scenarios:

- Court case processing
- Document management
- Permit processing
- Service delivery metrics

Load via **Help → Sample Data → Load Sample Data...**

---

## Accessibility

CiviQual Stats complies with Section 508 of the Rehabilitation Act and WCAG 2.1 Level AA:

- Full keyboard navigation
- Screen reader compatible (NVDA, JAWS, VoiceOver)
- High contrast mode
- Accessible names on all controls

---

## License

### Free Tier
Free for government agencies, courts, nonprofits, and educational institutions.

### Pro Tier
Commercial license required. Contact www.qualityincourts.com for pricing.

---

## Support

- **Documentation**: https://qualityincourts.com/docs
- **Support Email**: support@qualityincourts.com
- **Issues**: https://github.com/qualityincourts-lab/CiviQual/issues

---

## Credits

**CiviQual Stats** is developed by **A Step in the Right Direction LLC** as part of the **Quality in Courts** initiative.

© 2026 A Step in the Right Direction LLC. All Rights Reserved.
