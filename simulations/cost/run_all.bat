@echo off
REM POLLN Cost Simulations - Windows Batch Script
REM Quick launcher for running all cost simulations

echo ================================================================================
echo POLLN COST SIMULATIONS
echo ================================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Check if required packages are installed
echo Checking dependencies...
python -c "import numpy" >nul 2>&1
if errorlevel 1 (
    echo Installing numpy...
    pip install numpy
)

python -c "import matplotlib" >nul 2>&1
if errorlevel 1 (
    echo Installing matplotlib...
    pip install matplotlib
)

echo Dependencies OK
echo.

REM Run all simulations
echo ================================================================================
echo Running all simulations...
echo ================================================================================
echo.

python run_all.py

if errorlevel 1 (
    echo.
    echo ERROR: Simulations failed
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo SIMULATIONS COMPLETE
echo ================================================================================
echo.
echo Generated files:
echo   - COST_ANALYSIS_SUMMARY.txt (Executive summary)
echo   - cost_calculator.html (Interactive calculator)
echo   - *.png (Visualization charts)
echo   - *_report.txt (Detailed reports)
echo   - *_results.json (Machine-readable data)
echo.

REM Ask if user wants to open calculator
set /p OPEN_CALC="Open interactive calculator? (Y/N): "
if /i "%OPEN_CALC%"=="Y" (
    start cost_calculator.html
)

REM Ask if user wants to view summary
set /p VIEW_SUM="View summary report? (Y/N): "
if /i "%VIEW_SUM%"=="Y" (
    type COST_ANALYSIS_SUMMARY.txt | more
)

echo.
echo Done! Press any key to exit...
pause >nul
