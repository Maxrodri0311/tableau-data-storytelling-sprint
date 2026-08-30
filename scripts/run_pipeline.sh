#!/usr/bin/env bash
set -euo pipefail

echo "================================================================"
echo " [Apply on Job] Running Tableau Data Storytelling Pipeline     "
echo "================================================================"

# 1. Ingest & Generate 50,000+ Recruitment Funnel Records
echo "[1/3] Generating 50,000+ recruitment funnel application events..."
python src/data_generator.py

# 2. Materialize Star Schema & Tableau Prep LOD Engine in DuckDB
echo "[2/3] Materializing Kimball Star Schema & Tableau LOD in DuckDB..."
python src/tableau_prep_engine.py

# 3. Generate Automated C-Level Executive Excel Report
echo "[3/3] Generating Executive Excel Scorecard with OpenPyXL..."
python src/excel_reporter.py

echo "================================================================"
echo " [SUCCESS] Pipeline execution complete. Artifacts ready!        "
echo "================================================================"
