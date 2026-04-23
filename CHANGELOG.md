# CiviQual Stats Changelog

All notable changes to CiviQual Stats are documented in this file.

## [2.0.0] - DMAIC Edition - April 2026

### Major Changes

**DMAIC Phase Organization**
- Complete UI restructure: Tools organized by DMAIC phase (Define, Measure, Analyze, Improve, Control)
- Phase tabs with keyboard shortcuts (Alt+D, Alt+M, Alt+A, Alt+I, Alt+C)
- Tool number shortcuts (1-9) within each phase
- Clear Free/Pro tier separation within each phase

**Pro Module Integration**
- All 13 Pro modules now integrated into UI with license gating
- Measure: MSA (Gage R&R), Sample Size Calculator, Advanced Capability
- Analyze: Hypothesis Tests, DOE, Multiple Regression, Root Cause Tools, Data Tools
- Improve: Solution Tools, Lean Calculators
- Control: CUSUM/EWMA Charts, Planning Tools, Chart Editor

**Project Session Save (Pro Feature)**
- Save/Open project files (.civiqual)
- Preserves: data file path, column selections, spec limits, chart settings
- Analysis history with timestamps
- Auto-save with crash recovery
- Recent Projects menu

**New Menu Structure**
- Added Edit menu: Undo, Redo, Copy, Paste, Find in Data
- Added View menu: Phase shortcuts, Zoom controls, High Contrast, Full Screen
- Added Tools menu: Quick access to utilities and Pro Features submenu
- Help menu: Sample Data submenu, Accessibility dialog

**Chart Editor**
- Available as both tab (Control phase) and toolbar overlay
- Customize chart colors, labels, formatting
- Pro feature

### Improvements

- ROI Calculator moved from Control to Improve phase
- Updated license dialog to dual license terms (Free/Pro tiers)
- Fixed email addresses (accessibility@ → support@)
- All sample data files updated with public sector context
- Improved Section 508 accessibility compliance
- Added accessible names and descriptions to all Pro features

### Sample Data Updates

Free tier samples now include:
- sample_control_chart.csv - Court case processing with control signals
- sample_capability.csv - Document processing cycle time
- sample_anova.csv - Processing by court division
- sample_correlation.csv - Case complexity factors
- sample_pareto.csv - Filing defect categories
- sample_court_operations.csv - Comprehensive 50-case dataset

Pro tier samples added:
- sample_msa_gage_rr.csv - Case file quality review
- sample_doe_factorial.csv - Court process optimization
- sample_hypothesis_tests.csv - Workflow comparison study
- sample_regression.csv - Processing time predictors
- sample_cusum_ewma.csv - Weekly metrics with drift
- sample_lean_metrics.csv - 12-step process metrics
- sample_fmea.csv - Court process failure modes

### Technical Changes

- Version updated to 2.0.0
- New ProjectSession class for session management
- ProGatedWidget for license-aware feature display
- DMaicPhaseWidget for phase organization
- Settings persistence via QSettings
- Auto-save timer with configurable interval

---

## [1.2.0] - April 2026

### Added
- Enterprise licensing support
- All Pro module backend implementations complete
- Western Electric Tests 5 and 6
- Tukey HSD post-hoc function
- Data Sampling tab improvements

### Fixed
- WiX 6.0.2 MSI build compatibility
- Various bug fixes in statistics_engine.py

---

## [1.1.0] - March 2026

### Added
- License manager with RSA signature verification
- Pro tier module structure
- 4-Up Chart with Watson output format

---

## [1.0.0] - February 2026

### Initial Release
- Yellow Belt statistical tools
- Control charts (I, MR, I-MR)
- Capability analysis (Cp, Cpk)
- ANOVA and correlation
- Process diagrams (SIPOC, Process Map, RACI, etc.)
- Section 508 accessibility compliance
- MSI installer with code signing
