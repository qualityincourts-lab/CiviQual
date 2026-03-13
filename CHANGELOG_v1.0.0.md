# CiviQual v1.0.0 Change Log

**Release Date:** March 2026  
**Rebranded from:** Watson for Lean Six Sigma v1.3.0

---

## Complete Rebrand: Watson → CiviQual

All files have been updated with CiviQual branding:
- Application name changed throughout
- Icon files renamed (civiqual_icon.ico, civiqual_icon.png)
- Splash screen updated with CiviQual branding
- Config directory changed to CiviQual
- Installer files renamed and updated
- README.md completely rewritten

---

## Bug Fixes Implemented

### Fix #1: Windows Dark Mode Support
**File:** `main.py`  
**Status:** ✅ Complete

- Added system dark mode detection for Windows via registry
- Created light and dark color palettes
- Updated all UI stylesheets to be theme-aware
- Chart display areas now adapt to system theme
- Tables, tabs, menus, and inputs all support dark mode
- Brand colors (burgundy buttons, menu bar) remain consistent

### Fix #2: Chart Export Broken
**File:** `main.py` (function `_export_chart`)  
**Status:** ✅ Complete

- Previously: Export dialog opened but file was never saved
- Now: Correctly saves the current tab's chart pixmap to file
- Added format detection (PNG/JPEG based on extension)
- Added error handling and success confirmation

### Fix #3: I-Chart Shows All Tests (Not Selected Subset)
**Files:** `visualizations.py`, `main.py`  
**Status:** ✅ Complete

- `rules` parameter now properly passed through entire call chain
- `_plot_ichart()` updated to accept and use `rules` parameter
- `generate_ichart()` and `generate_imr_chart()` now forward rules
- Only selected Western Electric tests are applied to flagged point detection

### Fix #4: I-Chart Dots Too Large
**File:** `visualizations.py`  
**Status:** ✅ Complete

- Reduced flagged point marker size from `s=100` to `s=60`
- Added test failure labels (e.g., "T1", "T1,2") above flagged points
- Labels alternate position to reduce overlap

### Fix #5: I-Chart Report Does Not List Failures by Test
**File:** `main.py` (function `_generate_control_chart_analysis`)  
**Status:** ✅ Complete

- Added "FLAGGED POINTS DETAIL" section to analysis output
- Lists each flagged observation with its value and triggering test(s)
- Shows test counts in stability summary (e.g., "T1:3, T2:1")

### Fix #6: Cp=1 Default Should Not Assume Normal Distribution
**File:** `visualizations.py`  
**Status:** ✅ Complete

- Added Anderson-Darling normality test before displaying Cp=1 limits
- Warning displayed when data fails normality test at 5% level
- Message: "⚠ Non-normal data - Cp=1 assumes normality"

### Fix #7b: Capability LSL Should Not Go Below 0 for Positive Data
**Files:** `visualizations.py`, `main.py`  
**Status:** ✅ Complete

- Natural LSL (mean - 3σ) now clamped to 0 when all data is positive
- Chart displays "(clamped)" indicator when LSL is adjusted
- Text output shows original calculated value alongside clamped value

### Fix #8: Charts Show Negative Y-Axis When Data is All Positive
**File:** `visualizations.py`  
**Status:** ✅ Complete

- X-axis limits now constrained to prevent negative display for positive data
- Histogram shading areas only drawn within visible axis range
- Capability chart x-axis starts at 0 when appropriate

---

## Files Modified

| File | Changes |
|------|---------|
| `main.py` | Dark mode, chart export, I-chart analysis, capability output, full rebrand |
| `visualizations.py` | I-chart rules, dot size, labels, capability chart fixes, rebrand |
| `statistics_engine.py` | Rebrand only |
| `data_handler.py` | Rebrand only |
| `report_generator.py` | Full rebrand |
| `process_diagrams.py` | Rebrand only |
| `build_installer.py` | Full rebrand |
| `create_icon.py` | Rebrand only |
| `README.md` | Completely rewritten |
| `INSTALLATION.md` | Rebrand |
| `SECTION_508_COMPLIANCE.md` | Rebrand |
| `installer/*.iss, *.bat, *.md` | Full rebrand |
| `installer/msi/*.wxs, *.bat, *.ps1, *.md` | Full rebrand |

---

## Files Renamed

| Old Name | New Name |
|----------|----------|
| `watson_icon.ico` | `civiqual_icon.ico` |
| `watson_icon.png` | `civiqual_icon.png` |
| `watson_logo.svg` | `civiqual_logo.svg` |
| `watson_logo_horizontal.svg` | `civiqual_logo_horizontal.svg` |
| `installer/Watson_Setup.iss` | `installer/CiviQual_Setup.iss` |
| `installer/msi/Watson.wxs` | `installer/msi/CiviQual.wxs` |

---

## Testing Recommendations

Before release, test the following:

1. **Dark Mode:** Enable Windows dark mode and verify UI is readable
2. **Chart Export:** Generate any chart, press Ctrl+E, verify file saves correctly
3. **I-Chart Rules:** Uncheck some rules, generate chart, verify only checked rules flag points
4. **Capability (Positive Data):** Load positive-only data (e.g., processing times), verify:
   - LSL shows as 0 (clamped) if natural LSL would be negative
   - Histogram doesn't extend below 0
5. **Non-Normal Data:** Load skewed data, verify normality warning appears

---

*CiviQual - Quality Analytics for Public Service*  
*© 2026 A Step in the Right Direction LLC*
