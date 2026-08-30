"""
Apply on Job - Executive C-Level Excel Scorecard Generator
Generates a formatted corporate Excel Workbook (.xlsx) with KPI scorecards,
waterfall funnels, channel ROI benchmarks, and conditional alerts.
"""
import os
import duckdb
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

class ExecutiveExcelReporter:
    def __init__(self, parquet_path: str = "data/curated_recruitment_funnel.parquet"):
        self.parquet_path = parquet_path
        self.con = duckdb.connect(":memory:")

    def generate_executive_workbook(self, output_path: str = "reports/Executive_Hiring_Scorecard.xlsx") -> str:
        print(f"[*] Building C-Suite Executive Excel Scorecard from {self.parquet_path}...")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        wb = openpyxl.Workbook()
        ws_kpis = wb.active
        ws_kpis.title = "Executive Summary"
        ws_kpis.views.sheetView[0].showGridLines = True

        # Palettes
        navy_header_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
        sky_subhead_fill = PatternFill(start_color="0284C7", end_color="0284C7", fill_type="solid")
        zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        alert_red_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
        success_green_fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")

        white_title_font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
        white_header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        bold_font = Font(name="Calibri", size=11, bold=True)
        regular_font = Font(name="Calibri", size=11)
        kpi_big_font = Font(name="Calibri", size=18, bold=True, color="0284C7")

        thin_border = Border(
            left=Side(style='thin', color='CBD5E1'),
            right=Side(style='thin', color='CBD5E1'),
            top=Side(style='thin', color='CBD5E1'),
            bottom=Side(style='thin', color='CBD5E1')
        )

        # 1. Main Title Block
        ws_kpis.merge_cells("A1:G1")
        title_cell = ws_kpis["A1"]
        title_cell.value = "APPLY ON JOB — EXECUTIVE TALENT ACQUISITION & HIRING VELOCITY SCORECARD"
        title_cell.font = white_title_font
        title_cell.fill = navy_header_fill
        title_cell.alignment = Alignment(horizontal="center", vertical="center")
        ws_kpis.row_dimensions[1].height = 35

        # 2. Executive KPI Cards (Row 3-5)
        kpi_data = self.con.execute(f"""
            SELECT 
                COUNT(*) as total_apps,
                SUM(is_hired) as total_hires,
                AVG(is_hired) as hiring_rate,
                AVG(days_in_pipeline) as avg_days,
                SUM(sourcing_cost_usd) as total_spend,
                SUM(sourcing_cost_usd) / NULLIF(SUM(is_hired), 0) as cost_per_hire
            FROM read_parquet('{self.parquet_path}');
        """).df().to_dict(orient="records")[0]

        cards = [
            ("Total Pipeline Applicants", f"{kpi_data['total_apps']:,}", "A", "B"),
            ("Successfully Hired", f"{int(kpi_data['total_hires']):,}", "C", "C"),
            ("Hiring Conversion Rate", f"{kpi_data['hiring_rate']:.2%}", "D", "D"),
            ("Avg. Time-to-Fill", f"{kpi_data['avg_days']:.1f} Days", "E", "E"),
            ("Total Sourcing Spend", f"${kpi_data['total_spend']:,.0f}", "F", "F"),
            ("Cost per Hire", f"${kpi_data['cost_per_hire']:,.0f}", "G", "G")
        ]

        for title, val, start_col, end_col in cards:
            c1 = f"{start_col}3"
            c2 = f"{start_col}4"
            if start_col != end_col:
                ws_kpis.merge_cells(f"{start_col}3:{end_col}3")
                ws_kpis.merge_cells(f"{start_col}4:{end_col}4")

            ws_kpis[c1].value = title
            ws_kpis[c1].font = Font(size=9, color="64748B", bold=True)
            ws_kpis[c1].alignment = Alignment(horizontal="center", vertical="center")

            ws_kpis[c2].value = val
            ws_kpis[c2].font = kpi_big_font
            ws_kpis[c2].alignment = Alignment(horizontal="center", vertical="center")
            ws_kpis[c2].fill = zebra_fill

        ws_kpis.row_dimensions[3].height = 18
        ws_kpis.row_dimensions[4].height = 30

        # 3. Funnel Waterfall Table (Row 7)
        ws_kpis.merge_cells("A7:G7")
        ws_kpis["A7"].value = "RECRUITMENT FUNNEL CONVERSION WATERFALL & STAGE VELOCITY"
        ws_kpis["A7"].font = white_header_font
        ws_kpis["A7"].fill = sky_subhead_fill
        ws_kpis["A7"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
        ws_kpis.row_dimensions[7].height = 24

        headers_funnel = ["Funnel Stage", "Candidate Volume", "Share of Total", "Avg. Stage Velocity (Days)", "Drop-off Rate", "Stage Health Status", "C-Level Action Required"]
        for col_idx, h in enumerate(headers_funnel, 1):
            cell = ws_kpis.cell(row=8, column=col_idx, value=h)
            cell.font = white_header_font
            cell.fill = navy_header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
        ws_kpis.row_dimensions[8].height = 22

        funnel_rows = self.con.execute(f"""
            SELECT 
                highest_funnel_stage,
                COUNT(*) as volume,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM read_parquet('{self.parquet_path}')), 2) as share_pct,
                ROUND(AVG(days_in_pipeline), 1) as avg_days
            FROM read_parquet('{self.parquet_path}')
            GROUP BY highest_funnel_stage
            ORDER BY highest_funnel_stage ASC;
        """).df().to_dict(orient="records")

        current_row = 9
        for r in funnel_rows:
            ws_kpis.cell(row=current_row, column=1, value=r["highest_funnel_stage"]).font = bold_font
            ws_kpis.cell(row=current_row, column=2, value=r["volume"]).number_format = "#,##0"
            ws_kpis.cell(row=current_row, column=3, value=r["share_pct"] / 100.0).number_format = "0.00%"
            ws_kpis.cell(row=current_row, column=4, value=f"{r['avg_days']} Days").alignment = Alignment(horizontal="center")
            
            # Status badge
            is_hire_stage = "5_Offer_Accepted" in r["highest_funnel_stage"]
            status_cell = ws_kpis.cell(row=current_row, column=6, value="OPTIMAL" if is_hire_stage else "CONTROLLED")
            status_cell.font = bold_font
            status_cell.fill = success_green_fill if is_hire_stage else zebra_fill
            status_cell.alignment = Alignment(horizontal="center")

            action_cell = ws_kpis.cell(row=current_row, column=7, value="Onboard & Retain" if is_hire_stage else "Automate Screening")
            action_cell.font = regular_font

            current_row += 1

        # 4. Sourcing Channel ROI Matrix (Row 16)
        current_row += 2
        ws_kpis.merge_cells(f"A{current_row}:G{current_row}")
        ws_kpis[f"A{current_row}"].value = "SOURCING CHANNEL EFFICIENCY & COST-PER-HIRE MATRIX"
        ws_kpis[f"A{current_row}"].font = white_header_font
        ws_kpis[f"A{current_row}"].fill = sky_subhead_fill
        ws_kpis.row_dimensions[current_row].height = 24
        
        current_row += 1
        headers_channel = ["Sourcing Channel", "Applicants", "Total Hires", "Conversion Rate", "Total Spend ($)", "Cost per Hire ($)", "ROI Efficiency Tier"]
        for col_idx, h in enumerate(headers_channel, 1):
            cell = ws_kpis.cell(row=current_row, column=col_idx, value=h)
            cell.font = white_header_font
            cell.fill = navy_header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
        ws_kpis.row_dimensions[current_row].height = 22

        channel_rows = self.con.execute(f"""
            SELECT 
                sourcing_channel,
                COUNT(*) as apps,
                SUM(is_hired) as hires,
                AVG(is_hired) as conv_rate,
                SUM(sourcing_cost_usd) as spend,
                SUM(sourcing_cost_usd) / NULLIF(SUM(is_hired), 0) as cph
            FROM read_parquet('{self.parquet_path}')
            GROUP BY sourcing_channel
            ORDER BY hires DESC;
        """).df().to_dict(orient="records")

        current_row += 1
        for cr in channel_rows:
            ws_kpis.cell(row=current_row, column=1, value=cr["sourcing_channel"]).font = bold_font
            ws_kpis.cell(row=current_row, column=2, value=cr["apps"]).number_format = "#,##0"
            ws_kpis.cell(row=current_row, column=3, value=cr["hires"]).number_format = "#,##0"
            ws_kpis.cell(row=current_row, column=4, value=cr["conv_rate"]).number_format = "0.00%"
            ws_kpis.cell(row=current_row, column=5, value=cr["spend"]).number_format = "$#,##0"
            ws_kpis.cell(row=current_row, column=6, value=cr["cph"]).number_format = "$#,##0"

            tier_cell = ws_kpis.cell(row=current_row, column=7)
            if cr["cph"] < 25000:
                tier_cell.value = "HIGH ROI (EXPAND BUDGET)"
                tier_cell.fill = success_green_fill
            else:
                tier_cell.value = "HIGH COST (AUDIT CONTRACT)"
                tier_cell.fill = alert_red_fill
            tier_cell.font = bold_font
            tier_cell.alignment = Alignment(horizontal="center")

            current_row += 1

        # Auto-adjust Column Widths
        for col in ws_kpis.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws_kpis.column_dimensions[col_letter].width = max(max_len + 3, 14)

        wb.save(output_path)
        print(f"[+] Successfully generated Executive Excel Scorecard: {output_path}")
        return output_path

if __name__ == "__main__":
    reporter = ExecutiveExcelReporter()
    reporter.generate_executive_workbook()
