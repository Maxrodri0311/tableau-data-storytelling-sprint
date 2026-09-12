"""
tests/benchmark.py - Medición Cuantitativa Real de Latencias (p50, p95, p99)
Ejecuta iteraciones reales de transformación Kimball Star Schema con DuckDB en memoria.
"""
import os
import sys
import time
import numpy as np

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_generator import generate_recruitment_dataset
from src.tableau_prep_engine import TableauPrepEngine

def run_benchmarks(iterations: int = 15):
    print(f"[*] Running {iterations} iterations of Tableau Prep & DuckDB Star Schema Engine...")
    test_parquet = "data/raw_recruitment_applications.parquet"
    if not os.path.exists(test_parquet):
        generate_recruitment_dataset(num_records=10000, output_path=test_parquet)

    engine = TableauPrepEngine()
    # Warmup
    engine.execute_star_schema(raw_parquet_path=test_parquet)

    latencies = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        engine.execute_star_schema(raw_parquet_path=test_parquet)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        latencies.append(elapsed_ms)

    p50 = np.percentile(latencies, 50)
    p95 = np.percentile(latencies, 95)
    p99 = np.percentile(latencies, 99)

    print("\n" + "="*55)
    print("  QUANTITATIVE LATENCY BENCHMARK (Tableau Prep & DuckDB)")
    print("="*55)
    print(f"  p50 Latency: {p50:.2f} ms")
    print(f"  p95 Latency: {p95:.2f} ms")
    print(f"  p99 Latency: {p99:.2f} ms")
    print("="*55 + "\n")

if __name__ == "__main__":
    run_benchmarks()
