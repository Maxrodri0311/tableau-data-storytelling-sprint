import pytest
import os
import pandas as pd
from src.data_generator import generate_recruitment_dataset
from src.tableau_prep_engine import TableauPrepEngine

@pytest.fixture(scope="module")
def sample_parquet(tmp_path_factory):
    fn = tmp_path_factory.mktemp("data") / "sample_apps.parquet"
    df = generate_recruitment_dataset(num_records=1500, random_seed=42)
    df.to_parquet(str(fn), index=False)
    return str(fn)

def test_duckdb_star_schema_and_lod(sample_parquet):
    engine = TableauPrepEngine()
    df_fact = engine.execute_star_schema(raw_parquet_path=sample_parquet)

    assert len(df_fact) == 1500
    assert "lod_fixed_dept_seniority_avg_salary" in df_fact.columns
    assert "lod_fixed_channel_avg_days_to_close" in df_fact.columns
    assert "budget_compliance_status" in df_fact.columns

    # Verify LOD calculated averages are positive numbers
    assert (df_fact["lod_fixed_dept_seniority_avg_salary"] > 0).all()
    assert (df_fact["lod_fixed_channel_avg_days_to_close"] > 0).all()
