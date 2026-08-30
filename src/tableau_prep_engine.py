"""
Apply on Job - Tableau Prep & DuckDB Dimensional Modeling Engine
Materializes a Kimball Star Schema with advanced Tableau Level-of-Detail (LOD) SQL calculations.
"""
import os
import json
import duckdb
import pandas as pd
from typing import Dict, Any

class TableauPrepEngine:
    def __init__(self, db_path: str = ":memory:"):
        self.con = duckdb.connect(db_path)

    def execute_star_schema(self, raw_parquet_path: str = "data/raw_recruitment_applications.parquet") -> pd.DataFrame:
        print(f"[*] Executing Kimball Star Schema & Tableau LOD Engine in DuckDB...")

        # 1. Staging View
        self.con.execute(f"""
            CREATE OR REPLACE VIEW stg_applications AS
            SELECT 
                application_hash,
                application_id,
                candidate_id,
                CAST(candidate_age AS INTEGER) as candidate_age,
                TRIM(candidate_gender) as candidate_gender,
                TRIM(department) as department,
                TRIM(target_role) as target_role,
                TRIM(seniority_level) as seniority_level,
                TRIM(sourcing_channel) as sourcing_channel,
                CAST(sourcing_cost_usd AS DECIMAL(10, 2)) as sourcing_cost_usd,
                CAST(budget_min_usd AS DECIMAL(12, 2)) as budget_min_usd,
                CAST(budget_max_usd AS DECIMAL(12, 2)) as budget_max_usd,
                CAST(candidate_expectation_usd AS DECIMAL(12, 2)) as candidate_expectation_usd,
                CAST(salary_delta_usd AS DECIMAL(12, 2)) as salary_delta_usd,
                TRIM(highest_funnel_stage) as highest_funnel_stage,
                CAST(days_in_pipeline AS INTEGER) as days_in_pipeline,
                TRIM(application_status) as application_status,
                CAST(application_date AS DATE) as application_date,
                CAST(is_hired AS INTEGER) as is_hired
            FROM read_parquet('{raw_parquet_path}');
        """)

        # 2. Dimension Tables
        self.con.execute("""
            CREATE OR REPLACE TABLE dim_candidates AS
            SELECT DISTINCT
                candidate_id,
                candidate_age,
                candidate_gender,
                seniority_level,
                CASE
                    WHEN candidate_age >= 45 THEN 'Veteran (45+)'
                    WHEN candidate_age >= 30 THEN 'Prime (30-44)'
                    ELSE 'Early Career (<30)'
                END as age_bracket
            FROM stg_applications;
        """)

        self.con.execute("""
            CREATE OR REPLACE TABLE dim_job_requisitions AS
            SELECT DISTINCT
                department,
                target_role,
                seniority_level,
                AVG(budget_min_usd) as benchmark_budget_min,
                AVG(budget_max_usd) as benchmark_budget_max
            FROM stg_applications
            GROUP BY department, target_role, seniority_level;
        """)

        self.con.execute("""
            CREATE OR REPLACE TABLE dim_recruitment_channels AS
            SELECT DISTINCT
                sourcing_channel,
                AVG(sourcing_cost_usd) as avg_cost_per_applicant_usd,
                CASE 
                    WHEN sourcing_channel IN ('Employee Referral', 'Direct Sourcing Outreach') THEN 'High_Touch_Internal'
                    WHEN sourcing_channel = 'External Headhunting Agency' THEN 'High_Cost_External'
                    ELSE 'Digital_Ambulatory'
                END as channel_tier
            FROM stg_applications
            GROUP BY sourcing_channel;
        """)

        # 3. Fact Table with Emulated Tableau Level-of-Detail (LOD) Calculations
        # LOD 1: {FIXED [Department], [Seniority]: AVG([Candidate Expectation])}
        # LOD 2: {FIXED [Sourcing Channel]: AVG([Days in Pipeline])}
        self.con.execute("""
            CREATE OR REPLACE TABLE fct_recruitment_funnel AS
            SELECT
                a.application_hash,
                a.application_id,
                a.candidate_id,
                a.application_date,
                DATE_TRUNC('month', a.application_date) as application_cohort_month,
                a.department,
                a.target_role,
                a.seniority_level,
                a.sourcing_channel,
                a.sourcing_cost_usd,
                a.budget_max_usd,
                a.candidate_expectation_usd,
                a.salary_delta_usd,
                a.highest_funnel_stage,
                a.days_in_pipeline,
                a.application_status,
                a.is_hired,
                
                -- Tableau LOD Emulation: Fixed Department & Seniority Benchmark
                ROUND(AVG(a.candidate_expectation_usd) OVER (
                    PARTITION BY a.department, a.seniority_level
                ), 2) as lod_fixed_dept_seniority_avg_salary,
                
                -- Tableau LOD Emulation: Fixed Channel Velocity Benchmark
                ROUND(AVG(a.days_in_pipeline) OVER (
                    PARTITION BY a.sourcing_channel
                ), 1) as lod_fixed_channel_avg_days_to_close,
                
                -- Compensation Disparity Risk Category
                CASE
                    WHEN a.salary_delta_usd > 15000 THEN 'HIGH_BUDGET_OVERRUN_RISK'
                    WHEN a.salary_delta_usd > 0 THEN 'MODERATE_OVERRUN'
                    ELSE 'WITHIN_BUDGET'
                END as budget_compliance_status
            FROM stg_applications a;
        """)

        df_fact = self.con.execute("SELECT * FROM fct_recruitment_funnel").df()
        out_path = "data/curated_recruitment_funnel.parquet"
        df_fact.to_parquet(out_path, index=False)
        print(f"[+] Materialized Fact Table with {len(df_fact):,} rows in {out_path}")

        # Compute Executive Aggregates for Dashboard JSON
        self._export_tableau_metrics()
        return df_fact

    def _export_tableau_metrics(self) -> Dict[str, Any]:
        """Calculates executive metrics and funnel conversion waterfalls."""
        summary = self.con.execute("""
            SELECT 
                COUNT(*) as total_applications,
                SUM(is_hired) as total_hires,
                ROUND(AVG(is_hired) * 100, 2) as overall_hiring_rate_pct,
                ROUND(AVG(days_in_pipeline), 1) as avg_days_in_pipeline,
                ROUND(SUM(sourcing_cost_usd), 2) as total_sourcing_spend_usd,
                ROUND(SUM(sourcing_cost_usd) / NULLIF(SUM(is_hired), 0), 2) as cost_per_hire_usd
            FROM fct_recruitment_funnel;
        """).df().to_dict(orient="records")[0]

        funnel_waterfall = self.con.execute("""
            SELECT 
                highest_funnel_stage as stage_name,
                COUNT(*) as candidate_count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fct_recruitment_funnel), 2) as pct_of_total,
                ROUND(AVG(days_in_pipeline), 1) as avg_stage_days
            FROM fct_recruitment_funnel
            GROUP BY highest_funnel_stage
            ORDER BY stage_name ASC;
        """).df().to_dict(orient="records")

        channel_roi = self.con.execute("""
            SELECT 
                sourcing_channel,
                COUNT(*) as total_candidates,
                SUM(is_hired) as total_hires,
                ROUND(AVG(is_hired) * 100, 2) as conversion_rate_pct,
                ROUND(SUM(sourcing_cost_usd) / NULLIF(SUM(is_hired), 0), 2) as cost_per_hire_usd,
                ROUND(AVG(days_in_pipeline), 1) as avg_time_to_fill_days
            FROM fct_recruitment_funnel
            GROUP BY sourcing_channel
            ORDER BY total_hires DESC;
        """).df().to_dict(orient="records")

        dept_salary_matrix = self.con.execute("""
            SELECT 
                department,
                seniority_level,
                ROUND(AVG(candidate_expectation_usd), 2) as avg_candidate_ask_usd,
                ROUND(AVG(budget_max_usd), 2) as avg_budget_max_usd,
                ROUND(AVG(salary_delta_usd), 2) as avg_salary_gap_usd
            FROM fct_recruitment_funnel
            GROUP BY department, seniority_level
            ORDER BY department, avg_candidate_ask_usd DESC;
        """).df().to_dict(orient="records")

        payload = {
            "executive_summary": summary,
            "funnel_waterfall": funnel_waterfall,
            "channel_performance": channel_roi,
            "department_salary_matrix": dept_salary_matrix
        }

        os.makedirs("web/data", exist_ok=True)
        with open("web/data/tableau_metrics.json", "w") as f:
            json.dump(payload, f, indent=2)

        print(f"[+] Exported Tableau analytics JSON to web/data/tableau_metrics.json")
        return payload

if __name__ == "__main__":
    engine = TableauPrepEngine()
    engine.execute_star_schema()
