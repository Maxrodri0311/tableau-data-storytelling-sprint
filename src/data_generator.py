"""
Apply on Job - Enterprise Recruitment Funnel & Talent Acquisition Data Generator
Generates realistic stochastic datasets (50,000+ records) modeling candidate progression,
compensation dynamics, sourcing channel unit economics, and hiring velocity.
"""
import os
import time
import argparse
import hashlib
import numpy as np
import pandas as pd

def generate_recruitment_dataset(
    num_records: int = 50000,
    output_path: str = "data/raw_recruitment_applications.parquet",
    random_seed: int = 42
) -> pd.DataFrame:
    """
    Generates high-density recruitment funnel applications with reproducible stochastic properties.
    Conforms strictly to Kimball star-schema requirements and Tableau LOD benchmarks.
    """
    print(f"[*] Generating {num_records:,} recruitment funnel records (Seed: {random_seed})...")
    start_time = time.perf_counter()
    rng = np.random.default_rng(random_seed)

    # 1. Structural Identifiers & Deterministic Hashes
    app_ids = [f"APP-{100000 + i}" for i in range(num_records)]
    cand_ids = [f"CAND-{rng.integers(10000, 99999):05d}" for _ in range(num_records)]
    
    # Generate unique hashes using vectorized string representations
    app_hashes = [
        hashlib.sha256(f"{random_seed}-{i}-{app_ids[i]}".encode()).hexdigest()[:16]
        for i in range(num_records)
    ]

    # 2. Demographic & Candidate Profiles
    candidate_ages = rng.integers(21, 62, size=num_records)
    genders = rng.choice(["Female", "Male", "Non-Binary"], size=num_records, p=[0.48, 0.48, 0.04])

    departments = ["Engineering", "Data & AI", "Product Management", "Revenue Operations", "Design"]
    dept_weights = [0.35, 0.25, 0.15, 0.15, 0.10]
    dept_choices = rng.choice(departments, size=num_records, p=dept_weights)

    roles_by_dept = {
        "Engineering": ["Senior Backend Engineer", "Fullstack Developer", "Platform Architect", "DevOps Engineer"],
        "Data & AI": ["Data Scientist", "Staff ML Engineer", "Data Analyst", "Analytics Engineer"],
        "Product Management": ["Lead Product Manager", "Technical Product Manager", "Associate PM"],
        "Revenue Operations": ["RevOps Analyst", "Sales Engineering Specialist", "Growth Ops Lead"],
        "Design": ["Lead Product Designer", "UI/UX Researcher", "Design Systems Engineer"]
    }

    target_roles = [rng.choice(roles_by_dept[dept]) for dept in dept_choices]

    seniority_levels = ["Junior", "Mid-Level", "Senior", "Staff / Lead"]
    seniority_choices = rng.choice(seniority_levels, size=num_records, p=[0.20, 0.35, 0.30, 0.15])

    # 3. Sourcing Channel & Unit Economics
    channels = [
        "LinkedIn Jobs",
        "Direct Sourcing Outreach",
        "Employee Referral",
        "External Headhunting Agency",
        "Inbound Careers Page"
    ]
    channel_choices = rng.choice(channels, size=num_records, p=[0.38, 0.22, 0.15, 0.10, 0.15])

    channel_base_costs = {
        "LinkedIn Jobs": (350.0, 75.0),
        "Direct Sourcing Outreach": (850.0, 150.0),
        "Employee Referral": (1800.0, 200.0),
        "External Headhunting Agency": (11500.0, 2000.0),
        "Inbound Careers Page": (45.0, 15.0)
    }

    sourcing_costs = np.array([
        max(10.0, rng.normal(channel_base_costs[ch][0], channel_base_costs[ch][1]))
        for ch in channel_choices
    ]).round(2)

    # 4. Compensation Benchmarks & Financial Dynamics
    base_salary_by_seniority = {
        "Junior": (55000.0, 75000.0),
        "Mid-Level": (80000.0, 110000.0),
        "Senior": (120000.0, 155000.0),
        "Staff / Lead": (165000.0, 210000.0)
    }

    budget_mins = np.array([
        base_salary_by_seniority[s][0] + rng.integers(-3000, 3000)
        for s in seniority_choices
    ], dtype=float)

    budget_maxs = np.array([
        base_salary_by_seniority[s][1] + rng.integers(2000, 8000)
        for s in seniority_choices
    ], dtype=float)

    # Ensure strictly positive and budget_max >= budget_min
    budget_mins = np.maximum(budget_mins, 40000.0).round(2)
    budget_maxs = np.maximum(budget_maxs, budget_mins + 10000.0).round(2)

    # Candidate expectation centered between budget_min and budget_max with market dispersion
    expectation_deltas = rng.normal(0.0, 12000.0, size=num_records)
    mid_budgets = (budget_mins + budget_maxs) / 2.0
    candidate_expectations = (mid_budgets + expectation_deltas).round(2)
    candidate_expectations = np.maximum(candidate_expectations, budget_mins * 0.75)

    salary_deltas = (candidate_expectations - budget_maxs).round(2)

    # 5. Hiring Funnel Progression & Conversion
    funnel_stages = [
        "1_Application_Review",
        "2_Technical_Screening",
        "3_System_Design_Interview",
        "4_Cultural_Fit",
        "5_Executive_Offer"
    ]
    
    # Referral and direct sourcing advance deeper into the funnel
    stage_indices = []
    is_hired_list = []
    days_in_pipeline_list = []
    app_statuses = []

    for i in range(num_records):
        ch = channel_choices[i]
        sen = seniority_choices[i]
        
        # Progression probability weights
        if ch in ["Employee Referral", "Direct Sourcing Outreach"]:
            weights = [0.25, 0.25, 0.25, 0.15, 0.10]
        elif ch == "External Headhunting Agency":
            weights = [0.20, 0.30, 0.25, 0.15, 0.10]
        else:
            weights = [0.55, 0.25, 0.12, 0.05, 0.03]

        stage_idx = rng.choice([0, 1, 2, 3, 4], p=weights)
        stage_name = funnel_stages[stage_idx]
        stage_indices.append(stage_name)

        # Hired only if stage 5 reached and expectation not wildly over budget
        if stage_idx == 4 and salary_deltas[i] < 20000:
            hired = 1 if rng.random() < 0.78 else 0
        else:
            hired = 0
        is_hired_list.append(hired)

        # Status assignment
        if hired == 1:
            status = "Hired"
        elif stage_idx == 4:
            status = "Offer_Declined" if rng.random() < 0.6 else "Rejected"
        else:
            status = "Rejected" if rng.random() < 0.88 else "Withdrawn"
        app_statuses.append(status)

        # Pipeline duration (days)
        base_days = (stage_idx + 1) * 7
        noise_days = rng.integers(1, 14)
        days_in_pipeline_list.append(int(base_days + noise_days))

    # 6. Dates across cohorts in 2024
    base_timestamp = pd.Timestamp("2024-01-01")
    random_days = rng.integers(0, 360, size=num_records)
    application_dates = [
        (base_timestamp + pd.Timedelta(days=int(d))).strftime("%Y-%m-%d")
        for d in random_days
    ]

    df = pd.DataFrame({
        "application_hash": app_hashes,
        "application_id": app_ids,
        "candidate_id": cand_ids,
        "candidate_age": candidate_ages,
        "candidate_gender": genders,
        "department": dept_choices,
        "target_role": target_roles,
        "seniority_level": seniority_choices,
        "sourcing_channel": channel_choices,
        "sourcing_cost_usd": sourcing_costs,
        "budget_min_usd": budget_mins,
        "budget_max_usd": budget_maxs,
        "candidate_expectation_usd": candidate_expectations,
        "salary_delta_usd": salary_deltas,
        "highest_funnel_stage": stage_indices,
        "days_in_pipeline": days_in_pipeline_list,
        "application_status": app_statuses,
        "application_date": application_dates,
        "is_hired": is_hired_list
    })

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_parquet(output_path, index=False)
        elapsed = time.perf_counter() - start_time
        print(f"[+] Dataset saved to {output_path} in {elapsed:.2f}s ({len(df):,} rows)")

    return df

# Backward-compatibility alias
def generate_synthetic_dataset(num_records: int = 50000, output_path: str = "data/raw_recruitment_applications.parquet"):
    return generate_recruitment_dataset(num_records=num_records, output_path=output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate recruitment funnel applications dataset")
    parser.add_argument("--records", type=int, default=50000, help="Number of records to generate")
    parser.add_argument("--output", type=str, default="data/raw_recruitment_applications.parquet", help="Target Parquet path")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()
    generate_recruitment_dataset(args.records, args.output, args.seed)
