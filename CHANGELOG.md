# Changelog

## 2.0.0 — 2026-04-21 (DMAIC Edition)

### New
- Complete architecture rebuild around the DMAIC phase structure
  (Define / Measure / Analyze / Improve / Control).
- Thirteen Pro modules with full working implementations:
  MSA (Gage R&R, ANOVA method), DOE (2^k factorial), Hypothesis Tests,
  Sample Size, Advanced Capability (with Box-Cox), Multiple Regression,
  Advanced Control Charts (CUSUM and EWMA), Lean Calculators, Root Cause
  Tools, Solution Tools (PICK), Planning Tools (FMEA, Control Plan),
  Data Tools, Chart Editor.
- RSA-PSS signature verification for Pro licenses; graceful fall-back to
  Free mode when a signature is invalid, missing, or expired.
- Western Electric rules 1 through 8 on the XmR and Control Chart Review
  panels.
- Anderson-Darling and Shapiro-Wilk normality tests in Descriptive Stats.
- Tukey HSD post-hoc pairs on every one-way ANOVA.
- Mann-Kendall trend test in Run Chart.
- Per-user and per-machine MSI installers built from a single WiX source.
- Watson 4-Up chart available as a dedicated Free tool.

### Fixed
- Ordering: status bar is created before the central widget so panels can
  post status messages during construction.
- Accessibility: invalid `setAccessibleName()` calls on QAction, QMenu,
  QMenuBar, and QToolBar were removed (unsupported in PySide6 6.5+).
- License property: all call sites now use `license_manager.is_pro`
  instead of the earlier `is_valid`.
- Pro module dataclass issue: class references are stored and the widgets
  are instantiated on demand from `_build_phase_tab`, avoiding eager
  construction of dataclasses that require arguments.
- High-DPI environment variable is set before `QApplication` is created.
- Control phase Free tools now include a Control Chart Review panel
  (previously empty).

## 1.0.0 — 2026-03-01

Initial public release (pre-DMAIC architecture).
