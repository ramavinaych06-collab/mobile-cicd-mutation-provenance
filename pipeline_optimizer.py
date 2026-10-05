"""
pipeline_optimizer.py
Optimizes mutation evaluation for CI/CD via selective sampling and fail-fast test execution.
"""

import ast
import copy
import time
from typing import Any, Dict, List
from mutation_engine import ASTMutationEngine


class CICDMutationOptimizer:
    def __init__(self, sampling_rate: float = 0.5, quality_threshold: float = 0.75):
        self.sampling_rate = sampling_rate
        self.quality_threshold = quality_threshold

    def generate_mutants(self, source_code: str) -> List[Dict[str, Any]]:
        counter = ASTMutationEngine(-1)
        counter.visit(ast.parse(source_code))
        total_mutants = counter.mutations_found

        mutants = []
        step = max(1, int(1 / self.sampling_rate))
        for i in range(0, total_mutants, step):
            mutator = ASTMutationEngine(i)
            mutated_ast = mutator.visit(copy.deepcopy(ast.parse(source_code)))
            ast.fix_missing_locations(mutated_ast)
            mutants.append({
                "id": i,
                "description": mutator.mutation_desc,
                "code": ast.unparse(mutated_ast),
            })
        return mutants

    def evaluate_test_suite(
        self,
        source_code: str,
        test_suite: List[Dict[str, Any]],
        mutants: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        start_time = time.time()
        killed = 0
        survived = 0
        details = []

        # Baseline check: verify original clean code passes all tests
        orig_scope: Dict[str, Any] = {}
        exec(source_code, orig_scope)
        for t in test_suite:
            try:
                assert orig_scope[t["func"]](*t["args"]) == t["expected"]
            except Exception as e:
                raise RuntimeError(f"Base test suite failed on clean code: {t['name']}") from e

        # Evaluate against each mutant with fail-fast execution
        for m in mutants:
            mut_scope: Dict[str, Any] = {}
            try:
                exec(m["code"], mut_scope)
            except Exception:
                killed += 1
                details.append({
                    "mutant_id": m["id"],
                    "status": "KILLED",
                    "reason": "CompilationError",
                })
                continue

            mutant_killed = False
            for t in test_suite:
                try:
                    result = mut_scope[t["func"]](*t["args"])
                    if result != t["expected"]:
                        mutant_killed = True
                        break
                except Exception:
                    mutant_killed = True
                    break

            if mutant_killed:
                killed += 1
                details.append({
                    "mutant_id": m["id"],
                    "status": "KILLED",
                    "desc": m["description"],
                })
            else:
                survived += 1
                details.append({
                    "mutant_id": m["id"],
                    "status": "SURVIVED",
                    "desc": m["description"],
                })

        total = len(mutants)
        msi = (killed / total) if total > 0 else 1.0
        elapsed_sec = time.time() - start_time
        passed_gate = msi >= self.quality_threshold

        return {
            "total_mutants_evaluated": total,
            "killed_mutants": killed,
            "survived_mutants": survived,
            "mutation_score": round(msi, 4),
            "mutation_score_percent": f"{round(msi * 100, 2)}%",
            "passed_gate": passed_gate,
            "execution_time_sec": round(elapsed_sec, 4),
            "mutant_details": details,
        }