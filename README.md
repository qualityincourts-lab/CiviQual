# CiviQual Stats

**Version:** 2.0.0 (DMAIC Edition)
**Publisher:** A Step in the Right Direction, LLC
**Website:** https://qualityincourts.com

CiviQual Stats is a free, open-source desktop statistical process control and
Lean Six Sigma analytics application for public-sector organizations. A
separately licensed Pro edition unlocks the full Green Belt and Black Belt
statistical toolkit.

## Edition comparison

| Phase | Free tools | Pro tools |
|---|---|---|
| Define | SIPOC, Process Map, RACI, Data Sampling, Split Worksheet | — |
| Measure | 4-Up, Descriptive Stats, XmR Control Charts, Capability, Prob Plot, Histogram, Box Plot, Run Chart | MSA, Sample Size, Advanced Capability |
| Analyze | ANOVA (with Tukey HSD), Correlation, Pareto, Swim Lane, VSM, Fishbone | Hypothesis Tests, DOE, Regression, Root Cause, Data Tools |
| Improve | ROI Calculator | Solution Tools, Lean Calculators |
| Control | Control Chart Review | CUSUM / EWMA, Planning Tools (FMEA), Chart Editor |

## Installation

Download the installer from the releases page, then run
`CiviQualStats_<version>.msi`. Two variants are published:

- **Per-user**, installs to `%LOCALAPPDATA%\CiviQualStats`, no administrator
  rights required.
- **Per-machine**, installs to `%ProgramFiles%\CiviQualStats`, requires
  administrator rights.

## Running from source

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Pro licensing

A Pro license is a signed JSON file. To install:

1. Receive the license JSON file from the publisher.
2. Launch CiviQual Stats.
3. From the **License** menu choose *Install License File…* and select the JSON.
4. Restart the application. Pro tools will appear as sub-tabs in each phase.

## Disclaimer

CiviQual Stats is an analytical tool. Interpretation of statistical results
requires qualified judgment. CiviQual Stats is not a substitute for
professional statistical or engineering advice.

## License

The application source is distributed under the MIT License. See LICENSE.txt.
