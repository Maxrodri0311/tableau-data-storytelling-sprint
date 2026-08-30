"""
Apply on Job - Talent Acquisition & Recruitment Funnel Data Generator
Generates 50,000+ realistic candidate application events with compensation parity,
time-to-fill velocity decay, and multi-channel sourcing attribution.
"""
import os
import hashlib
import random
import datetime
import numpy as np
import pandas as pd

def generate_recruitment_dataset(num_records: int = 50000, random_seed: int = 42) -> pd.DataFrame:
    print(f"[*] Generating {num_records:,} Talent Application Events for Apply on Job...")
    np.random.seed(random_seed)
    random.seed(random_seed)

    start_date = datetime.datetime(2025, 1, 1)

    roles_by_dept = {
        "Data & AI": [
            ("Data Scientist", 65000, 145000),
            ("Machine Learning Engineer", 75000, 165000),
            ("Data Architect", 90000, 185000),
            ("BI & Tableau Developer", 55000, 120000)
        ],
        "Engineering": [
            ("Backend Engineer", 60000, 140000),
            ("Cloud & DevOps Specialist", 70000, 155000),
            ("Frontend Engineer", 55000, 125000),
            ("Fullstack Engineer", 62000, 138000)
        ],
        "Product & Design": [
            ("Product Manager", 70000, 150000),
            ("UI/UX Designer", 48000, 110000)
        ]
    }

    seniority_levels = ["Junior", "Mid-Level", "Senior", "Lead / Staff"]
    seniority_multipliers = {"Junior": 0.70, "Mid-Level": 1.0, "Senior": 1.45, "Lead / Staff": 1.90}
    seniority_weights = [0.25, 0.40, 0.25, 0.10]

    channels = [
        ("LinkedIn Recruiter", 450.0, 0.38),
        ("Employee Referral", 1200.0, 0.18),
        ("Inbound Careers Portal", 50.0, 0.24),
        ("External Headhunting Agency", 5500.0, 0.12),
        ("Direct Sourcing Outreach", 280.0, 0.08)
    ]
    channel_names = [c[0] for c in channels]
    channel_costs = {c[0]: c[1] for c in channels}
    channel_probs = [c[2] for c in channels]

    # Pre-allocate arrays
    app_ids = [f"APP-2026-{i:06d}" for i in range(1, num_records + 1)]
    candidate_ids = [f"CAND-{i:06d}" for i in range(1, num_records + 1)]
    genders = np.random.choice(["Female", "Male", "Non-Binary"], size=num_records, p=[0.46, 0.50, 0.04])
    ages = np.random.normal(loc=32, scale=7, size=num_records).clip(21, 65).astype(int)

    selected_depts = np.random.choice(list(roles_by_dept.keys()), size=num_records, p=[0.45, 0.40, 0.15])
    selected_roles = []
    base_salaries_min = []
    base_salaries_max = []

    for dept in selected_depts:
        role_info = random.choice(roles_by_dept[dept])
        selected_roles.append(role_info[0])
        base_salaries_min.append(role_info[1])
        base_salaries_max.append(role_info[2])

    selected_seniority = np.random.choice(seniority_levels, size=num_records, p=seniority_weights)
    selected_channels = np.random.choice(channel_names, size=num_records, p=channel_probs)
    sourcing_cost_usd = [channel_costs[ch] for ch in selected_channels]

    # Calculate Budget Bands ($ USD)
    mults = np.array([seniority_multipliers[s] for s in selected_seniority])
    budget_min_usd = (np.array(base_salaries_min) * mults).round(0)
    budget_max_usd = (np.array(base_salaries_max) * mults).round(0)

    # Candidate Salary Expectations (with realistic variance and market expectations)
    market_factor = np.random.normal(loc=0.98, scale=0.14, size=num_records)
    candidate_expectation_usd = (budget_max_usd * market_factor).round(0)
    salary_delta_usd = candidate_expectation_usd - budget_max_usd

    # Funnel Progression & Decay Simulation
    # 100% Applied -> ~36% Screened -> ~16% Tech -> ~6.5% Executive -> ~2.8% Hired
    funnel_stages = []
    days_in_pipeline = []
    final_status = []

    for i in range(num_records):
        ch = selected_channels[i]
        exp_delta = salary_delta_usd[i]

        # Referrals and Direct Outreach have higher pass rates
        boost = 0.15 if ch in ["Employee Referral", "Direct Sourcing Outreach"] else 0.0

        p_screen = 0.35 + boost
        p_tech = 0.45 + boost
        p_exec = 0.42 + boost
        p_offer = 0.48 - (0.25 if exp_delta > 10000 else 0.0)

        # Stage 1: Applied
        if np.random.rand() > p_screen:
            funnel_stages.append("1_Applied")
            days_in_pipeline.append(np.random.randint(1, 5))
            final_status.append("Rejected_Screening")
            continue

        # Stage 2: Screening
        if np.random.rand() > p_tech:
            funnel_stages.append("2_Screening_Passed")
            days_in_pipeline.append(np.random.randint(6, 14))
            final_status.append("Failed_Technical")
            continue

        # Stage 3: Technical Challenge
        if np.random.rand() > p_exec:
            funnel_stages.append("3_Technical_Passed")
            days_in_pipeline.append(np.random.randint(15, 25))
            final_status.append("Rejected_Executive")
            continue

        # Stage 4: Executive Interview
        if np.random.rand() > p_offer:
            funnel_stages.append("4_Executive_Passed")
            days_in_pipeline.append(np.random.randint(26, 38))
            final_status.append("Offer_Declined_Comp" if exp_delta > 0 else "Candidate_Withdrew")
            continue

        # Stage 5: Offer Accepted
        funnel_stages.append("5_Offer_Accepted")
        days_in_pipeline.append(np.random.randint(35, 54))
        final_status.append("Hired_Successfully")

    # Application Dates across 2025-2026
    random_days = np.random.randint(0, 480, size=num_records)
    applied_dates = [start_date + datetime.timedelta(days=int(d)) for d in random_days]

    # Cryptographic Hash for Idempotence
    application_hashes = [
        hashlib.sha256(f"{cid}_{r}_{dt.strftime('%Y%m%d')}".encode()).hexdigest()[:16]
        for cid, r, dt in zip(candidate_ids, selected_roles, applied_dates)
    ]

    df = pd.DataFrame({
        "application_hash": application_hashes,
        "application_id": app_ids,
        "candidate_id": candidate_ids,
        "candidate_age": ages,
        "candidate_gender": genders,
        "department": selected_depts,
        "target_role": selected_roles,
        "seniority_level": selected_seniority,
        "sourcing_channel": selected_channels,
        "sourcing_cost_usd": sourcing_cost_usd,
        "budget_min_usd": budget_min_usd,
        "budget_max_usd": budget_max_usd,
        "candidate_expectation_usd": candidate_expectation_usd,
        "salary_delta_usd": salary_delta_usd,
        "highest_funnel_stage": funnel_stages,
        "days_in_pipeline": days_in_pipeline,
        "application_status": final_status,
        "application_date": [dt.strftime("%Y-%m-%d") for dt in applied_dates],
        "is_hired": [1 if s == "5_Offer_Accepted" else 0 for s in funnel_stages]
    })

    os.makedirs("data", exist_ok=True)
    csv_path = "data/raw_recruitment_applications.csv"
    parquet_path = "data/raw_recruitment_applications.parquet"
    
    df.to_csv(csv_path, index=False)
    df.to_parquet(parquet_path, index=False)

    print(f"[+] Exported {len(df):,} records successfully:")
    print(f" -> Parquet: {parquet_path} ({os.path.getsize(parquet_path) / 1024 / 1024:.2f} MB)")
    print(f" -> Overall Hiring Rate: {df['is_hired'].mean():.2%}")
    print(f" -> Total Sourcing Spend: ${df['sourcing_cost_usd'].sum():,.2f} USD")
    return df

if __name__ == "__main__":
    generate_recruitment_dataset(50000)