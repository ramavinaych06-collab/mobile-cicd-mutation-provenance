"""
main.py
Main entry point demonstrating the entire mobile app release engineering pipeline.
"""

import hashlib
from benchmark_harness import BenchmarkValidationHarness
from pipeline_optimizer import CICDMutationOptimizer
from provenance_blockchain import SoftwareProvenanceBlockchain


def main():
    print("=" * 75)
    print("CI/CD Pipeline Optimization & Blockchain Provenance - Mobile Release")
    print("=" * 75)

    # Simulated Mobile Logic (e.g., In-App Checkout / Pricing Engine)
    mobile_source = """
def calculate_discount(price, quantity, is_premium):
    total = price * quantity
    if total > 100 and is_premium:
        discount = total * 0.20
    elif total > 50:
        discount = total * 0.10
    else:
        discount = 0.0
    return total - discount
"""

    # Mobile Unit Test Suite
    test_suite = [
        {"name": "test_premium_large", "func": "calculate_discount", "args": (50, 3, True), "expected": 120.0},
        {"name": "test_regular_medium", "func": "calculate_discount", "args": (20, 3, False), "expected": 54.0},
        {"name": "test_small_order", "func": "calculate_discount", "args": (10, 2, False), "expected": 20.0},
        {"name": "test_boundary_value", "func": "calculate_discount", "args": (50, 1, False), "expected": 50.0},
    ]

    # Ground-truth Benchmark Defects (Defects4J style bugs)
    known_defects = [
        {
            "id": "DEF-001",
            "description": "Boundary operator error (>= instead of >)",
            "defective_code": """
def calculate_discount(price, quantity, is_premium):
    total = price * quantity
    if total >= 100 and is_premium:
        discount = total * 0.20
    elif total >= 50:
        discount = total * 0.10
    else:
        discount = 0.0
    return total - discount
""",
        },
        {
            "id": "DEF-002",
            "description": "Arithmetic calculation error (+ instead of *)",
            "defective_code": """
def calculate_discount(price, quantity, is_premium):
    total = price + quantity
    if total > 100 and is_premium:
        discount = total * 0.20
    elif total > 50:
        discount = total * 0.10
    else:
        discount = 0.0
    return total - discount
""",
        },
    ]

    # --- Phase 1: Optimized Mutation Quality Gate ---
    print("\n[Phase 1] Executing Selective Mutation Testing in CI/CD...")
    optimizer = CICDMutationOptimizer(sampling_rate=0.5, quality_threshold=0.75)
    mutants = optimizer.generate_mutants(mobile_source)
    report = optimizer.evaluate_test_suite(mobile_source, test_suite, mutants)

    print(f"  - Total Mutants Generated & Evaluated: {report['total_mutants_evaluated']}")
    print(f"  - Mutants Killed:                      {report['killed_mutants']}")
    print(f"  - Mutants Survived:                    {report['survived_mutants']}")
    print(f"  - Mutation Score Indicator (MSI):      {report['mutation_score_percent']}")
    print(f"  - CI/CD Quality Gate Status:           {'PASSED' if report['passed_gate'] else 'FAILED'}")

    # --- Phase 2: Blockchain Software Provenance Tracking ---
    print("\n[Phase 2] Logging Release Provenance to Cryptographic Ledger...")
    ledger = SoftwareProvenanceBlockchain()
    simulated_apk_hash = hashlib.sha256(b"com.example.mobileapp-v1.4.2-release.apk").hexdigest()

    block = ledger.record_release(
        app_id="com.example.mobileapp",
        version="v1.4.2",
        git_commit="a4c7e8293bd82c9e7829aefb28481bc9204918ef",
        artifact_hash=simulated_apk_hash,
        mutation_report=report,
        release_gate_passed=report["passed_gate"],
    )

    print(f"  - Block Index:         {block.index}")
    print(f"  - Current Block Hash:  {block.block_hash}")
    print(f"  - Previous Block Hash: {block.previous_hash}")
    print(f"  - Artifact Digest:     {block.release_data['artifact_sha256']}")
    print(f"  - Ledger Integrity:    {'VALID' if ledger.verify_integrity() else 'CORRUPT'}")

    # --- Phase 3: Benchmark Validation Harness ---
    print("\n[Phase 3] Benchmarking against Defect Dataset (Defects4J / PROMISE)...")
    bench = BenchmarkValidationHarness.run_benchmark(mobile_source, test_suite, known_defects)
    print(f"  - Baseline Mutants (Exhaustive): {bench['baseline_mutants_evaluated']}")
    print(f"  - Optimized Mutants (Sampled):    {bench['optimized_mutants_evaluated']}")
    print(f"  - Pipeline Speedup Factor:        {bench['speedup_ratio']}")
    print(f"  - Fault Detection Rate (FDR):     {bench['fault_detection_rate']} "
          f"({bench['real_defects_detected']}/{bench['real_defects_tested']} defects detected)")

    print("\n" + "=" * 75)
    print("Pipeline Execution Completed Successfully.")
    print("=" * 75)


if __name__ == "__main__":
    main()
    