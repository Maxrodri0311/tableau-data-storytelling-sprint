"""
tests/test_suite.py - End-to-End Pipeline Integration Test
Verifies complete flow: Generation -> Kimball Star Schema in DuckDB -> Tableau Metrics Export -> Executive Excel Scorecard.
"""
import os
import pytest
from src.data_generator import generate_recruitment_dataset
from src.tableau_prep_engine import TableauPrepEngine
from src.excel_reporter import ExecutiveExcelReporter

def test_full_pipeline_end_to_end(tmp_path):
    # 1. Generate Raw Data
    raw_path = str(tmp_path / "raw.parquet")
    df_raw = generate_recruitment_dataset(num_records=500, output_path=raw_path, random_seed=77)
    assert len(df_raw) == 500
    assert os.path.exists(raw_path)

    # 2. Execute DuckDB Star Schema & LOD Engine
    engine = TableauPrepEngine()
    df_fact = engine.execute_star_schema(raw_parquet_path=raw_path)
    assert len(df_fact) == 500
    assert "lod_fixed_dept_seniority_avg_salary" in df_fact.columns

    # 3. Generate Executive Excel Scorecard
    out_xlsx = str(tmp_path / "Executive_Hiring_Scorecard.xlsx")
    reporter = ExecutiveExcelReporter(parquet_path="data/curated_recruitment_funnel.parquet")
    generated_path = reporter.generate_executive_workbook(output_path=out_xlsx)
    assert os.path.exists(generated_path)
    assert os.path.getsize(generated_path) > 5000
