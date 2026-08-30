import pytest
import os
import pandas as pd
from src.data_generator import generate_recruitment_dataset

def test_data_generation_dimensions():
    df = generate_recruitment_dataset(num_records=1000, random_seed=99)
    assert len(df) == 1000
    assert "application_hash" in df.columns
    assert "candidate_id" in df.columns
    assert "department" in df.columns
    assert "target_role" in df.columns
    assert "sourcing_channel" in df.columns
    assert "highest_funnel_stage" in df.columns

def test_data_distributions_and_ranges():
    df = generate_recruitment_dataset(num_records=2000, random_seed=99)
    # Check candidate ages
    assert df["candidate_age"].min() >= 18
    assert df["candidate_age"].max() <= 75
    # Check budget positivity
    assert (df["budget_min_usd"] > 0).all()
    assert (df["budget_max_usd"] >= df["budget_min_usd"]).all()
    # Check hash uniqueness
    assert df["application_hash"].nunique() == 2000
    # Check binary hired flag
    assert set(df["is_hired"].unique()).issubset({0, 1})
