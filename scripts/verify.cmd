@echo off
REM Verify that every expected module is present in the install folder.
REM Run AFTER installing the MSI. Pass the install folder as argument 1,
REM or let the script default to the per-user location.

setlocal
set TARGET=%1
if "%TARGET%"=="" set TARGET=%LOCALAPPDATA%\A Step in the Right Direction, LLC\CiviQual Stats

echo Checking files in: %TARGET%
echo.

set MODULES=main.py version.py license_manager.py data_handler.py statistics_engine.py visualizations.py process_diagrams.py report_generator.py ui_common.py free_tools.py msa.py doe.py hypothesis_tests.py sample_size.py advanced_capability.py multiple_regression.py advanced_control_charts.py lean_calculators.py root_cause_tools.py solution_tools.py planning_tools.py data_tools.py chart_editor.py civiqual_icon.ico

set MISSING=0
for %%F in (%MODULES%) do (
    if not exist "%TARGET%\%%F" (
        echo MISSING: %%F
        set /a MISSING+=1
    )
)

if exist "%TARGET%\docs\user_guide.html" (
    echo OK: docs\user_guide.html
) else (
    echo MISSING: docs\user_guide.html
    set /a MISSING+=1
)

echo.
if %MISSING%==0 (
    echo All expected files are present.
) else (
    echo %MISSING% file(s) missing. Review the installer package list.
)
endlocal
