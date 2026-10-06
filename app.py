import hashlib
import streamlit as st
from benchmark_harness import BenchmarkValidationHarness
from pipeline_optimizer import CICDMutationOptimizer
from provenance_blockchain import SoftwareProvenanceBlockchain

st.set_page_config(page_title="Mobile CI/CD Mutation & Provenance", layout="wide")
st.title("📱 Mobile CI/CD Pipeline Optimization & Blockchain Provenance")

st.sidebar.header("Pipeline Configurations")
sampling_rate = st.sidebar.slider("Mutant Sampling Rate", 0.1, 1.0, 0.5, 0.1)
quality_threshold = st.sidebar.slider("Quality Gate Threshold", 0.5, 1.0, 0.75, 0.05)

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

test_suite = [
    {"name": "test_premium_large", "func": "calculate_discount", "args": (50, 3, True), "expected": 120.0},
    {"name": "test_regular_medium", "func": "calculate_discount", "args": (20, 3, False), "expected": 54.0},
    {"name": "test_small_order", "func": "calculate_discount", "args": (10, 2, False), "expected": 20.0},
    {"name": "test_boundary_value", "func": "calculate_discount", "args": (50, 1, False), "expected": 50.0},
]

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

if st.button("🚀 Run CI/CD Pipeline & Log Provenance"):
    # 1. Mutation Testing
    optimizer = CICDMutationOptimizer(sampling_rate=sampling_rate, quality_threshold=quality_threshold)
    mutants = optimizer.generate_mutants(mobile_source)
    report = optimizer.evaluate_test_suite(mobile_source, test_suite, mutants)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Evaluated Mutants", report["total_mutants_evaluated"])
    col2.metric("Mutants Killed", report["killed_mutants"])
    col3.metric("Mutation Score", report["mutation_score_percent"])
    col4.metric("Quality Gate", "PASSED" if report["passed_gate"] else "FAILED")

    # 2. Blockchain Provenance
    st.subheader("🔗 Blockchain Software Provenance Block")
    ledger = SoftwareProvenanceBlockchain()
    simulated_apk = hashlib.sha256(b"mobile-release.apk").hexdigest()
    block = ledger.record_release(
        "com.example.mobileapp", "v1.4.2", "a4c7e8293", simulated_apk, report, report["passed_gate"]
    )
    st.json({
        "Block Index": block.index,
        "Current Hash (SHA-256)": block.block_hash,
        "Previous Hash": block.previous_hash,
        "Artifact SHA-256": block.release_data["artifact_sha256"],
        "Ledger Integrity": "VALID" if ledger.verify_integrity() else "CORRUPT",
    })

    # 3. Benchmark
    st.subheader("📊 Defect Benchmark Results (Defects4J / PROMISE)")
    bench = BenchmarkValidationHarness.run_benchmark(mobile_source, test_suite, known_defects)
    st.write(f"- **Pipeline Speedup Factor:** `{bench['speedup_ratio']}`")
    st.write(f"- **Fault Detection Rate (FDR):** `{bench['fault_detection_rate']}`")
    