@echo off
REM Granular Reasoning Validation - Run All Simulations (Windows)
REM This script executes all four simulation modules

echo ========================================================================
echo GRANULAR REASONING VALIDATION - RUNNING ALL SIMULATIONS
echo ========================================================================
echo.

REM Create results directory
if not exist results mkdir results

REM Record start time
set start_time=%time%

REM Run simulations
echo 1. Running Decision Theory Simulation...
python decision_theory.py
echo + Decision Theory complete
echo.

echo 2. Running Information Theory Simulation...
python information_theory.py
echo + Information Theory complete
echo.

echo 3. Running Error Propagation Simulation...
python error_propagation.py
echo + Error Propagation complete
echo.

echo 4. Running Double-Slit Experiment Simulation...
python double_slit.py
echo + Double-Slit Experiment complete
echo.

echo ========================================================================
echo ALL SIMULATIONS COMPLETE
echo ========================================================================
echo.
echo Results saved to: .\results\
echo   - CSV files: Raw data
echo   - JSON files: Serialized results
echo   - PNG files: Publication-quality figures
echo   - TXT files: Summary reports
echo.
echo Next steps:
echo   1. Review summary reports in .\results\
echo   2. Examine figures for validation
echo   3. Open granular_reasoning_validation.ipynb for interactive analysis
echo.
echo ========================================================================

pause
