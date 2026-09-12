@echo off
chcp 65001 >nul
title "Tableau Data Storytelling Sprint - Apply on Job"
color 0B

echo ===============================================================================
echo   TABLEAU DATA STORYTELLING SPRINT (GP-026) -- APPLY ON JOB
echo   DuckDB Kimball Star Schema, Tableau LOD Calculations and Excel Scorecard
echo ===============================================================================
echo.

py -3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PY_CMD=py -3
) else (
    set PY_CMD=python
)

echo [*] Python Interpreter: %PY_CMD%
echo.

echo [1/5] Generating recruitment funnel dataset (50,000 records)...
%PY_CMD% src\data_generator.py --records 50000 --output data\raw_recruitment_applications.parquet
if %errorlevel% neq 0 (
    echo [ERROR] Data generation failed.
    exit /b 1
)

echo.
echo [2/5] Executing DuckDB Kimball Star Schema and Tableau LOD Engine...
%PY_CMD% src\tableau_prep_engine.py
if %errorlevel% neq 0 (
    echo [ERROR] Tableau Prep Engine failed.
    exit /b 1
)

echo.
echo [3/5] Generating C-Level Executive Excel Scorecard with OpenPyXL...
%PY_CMD% src\excel_reporter.py
if %errorlevel% neq 0 (
    echo [ERROR] Excel Scorecard generation failed.
    exit /b 1
)

echo.
echo [4/5] Running Pytest Verification Suite...
%PY_CMD% -m pytest tests\ -v --tb=short
if %errorlevel% neq 0 (
    echo [ERROR] Pytest suite failed.
    exit /b 1
)

echo.
echo [5/5] Running Quantitative Latency Benchmarks (15 iterations)...
%PY_CMD% tests\benchmark.py
if %errorlevel% neq 0 (
    echo [ERROR] Latency benchmarks failed.
    exit /b 1
)

echo.
echo ===============================================================================
echo   [SUCCESS] TABLEAU DATA STORYTELLING SPRINT COMPLETED (100%% GREEN STATE)
echo   * Raw Applications: data\raw_recruitment_applications.parquet
echo   * Curated Fact Table: data\curated_recruitment_funnel.parquet
echo   * Web Dashboard Data: web\data\tableau_metrics.json
echo   * Executive Excel Scorecard: reports\Executive_Hiring_Scorecard.xlsx
echo ===============================================================================
echo.
