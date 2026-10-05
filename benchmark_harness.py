"""
benchmark_harness.py
Validation harness benchmarked against real defect suites (Defects4J / PROMISE style).
"""

from typing import Any, Dict, List
from pipeline_optimizer import CICDMutationOptimizer


class BenchmarkValidationHarness:
    @staticmethod
    def run_benchmark(
        source_code: str,
        test_suite: List[Dict[str, Any]],
        known_defects: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        # Baseline: Full mutation testing (sampling_rate = 1.0)
        full_optimizer = CICDMutationOptimizer(sampling_rate=1.0, quality_threshold=0.7)
        full_mutants = full_optimizer.generate_mutants(source_code)
        full_eval = full_optimizer.evaluate_test_suite(source_code, test_suite, full_mutants)

        # Optimized: Selective sampling mutation testing (sampling_rate = 0.5)
        opt_optimizer = CICDMutationOptimizer(sampling_rate=0.5, quality_threshold=0.7)
        opt_mutants = opt_optimizer.generate_mutants(source_code)
        opt_eval = opt_optimizer.evaluate_test_suite(source_code, test_suite, opt_mutants)

        # Fault Detection Rate (FDR) on benchmark ground-truth defects
        defects_caught = 0
        for defect in known_defects:
            def_scope: Dict[str, Any] = {}
            exec(defect["defective_code"], def_scope)
            detected = False
            for t in test_suite:
                try:
                    if def_scope[t["func"]](*t["args"]) != t["expected"]:
                        detected = True
                        break
                except Exception:
                    detected = True
                    break
            if detected:
                defects_caught += 1

        fdr = defects_caught / len(known_defects) if known_defects else 1.0
        speedup = (
            full_eval["total_mutants_evaluated"] / opt_eval["total_mutants_evaluated"]
            if opt_eval["total_mutants_evaluated"] > 0
            else 1.0
        )

        return {
            "baseline_mutants_evaluated": full_eval["total_mutants_evaluated"],
            "optimized_mutants_evaluated": opt_eval["total_mutants_evaluated"],
            "speedup_ratio": f"{round(speedup, 2)}x",
            "mutation_score_optimized": opt_eval["mutation_score_percent"],
            "fault_detection_rate": f"{round(fdr * 100, 2)}%",
            "real_defects_tested": len(known_defects),
            "real_defects_detected": defects_caught,
        }
    