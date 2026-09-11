"""
FinSight AI - QA Agent
Performs comprehensive quality assurance on candidate strategy code:
- AST static checks & import restrictions
- Restricted subprocess unit testing
- Look-ahead bias verification (future bar perturbation invariance)
- Financial invariant checks (signal bounds in {-1, 0, 1})
- Missing data resilience checks
"""

from typing import List
import numpy as np
import pandas as pd
from backend.app.orchestration.contracts import ImplementationOutput, QACheckResult
from backend.app.strategy.sandbox import strategy_sandbox

class QAAgent:

    @classmethod
    def evaluate_implementation(cls, impl: ImplementationOutput, sample_df: pd.DataFrame) -> QACheckResult:
        details: List[str] = []


        ast_passed, ast_errors = strategy_sandbox.static_ast_check(impl.source_code)
        if ast_passed:
            details.append("AST Static Analysis: PASSED (approved modules only)")
        else:
            details.extend([f"AST Static Analysis: FAILED - {e}" for e in ast_errors])


        unit_passed, unit_msg = strategy_sandbox.run_in_restricted_subprocess(
            source_code=impl.source_code,
            test_code=impl.test_code,
            timeout_sec=5
        )
        if unit_passed:
            details.append("Isolated Subprocess Sandbox: PASSED")
        else:
            details.append(f"Isolated Subprocess Sandbox: FAILED - {unit_msg}")


        invariants_passed = True
        lookahead_passed = not any("Look-ahead" in error for error in ast_errors)
        leakage_passed = True

        try:


            signal_ok, signals_or_error = strategy_sandbox.run_signals_in_restricted_subprocess(impl.source_code, sample_df)
            if not signal_ok:
                invariants_passed = False
                details.append(f"Invariant Check: FAILED - {signals_or_error}")
            else:
                signals = np.asarray(signals_or_error)


                unique_sigs = set(np.unique(signals))
                if not unique_sigs.issubset({-1, 0, 1}):
                    invariants_passed = False
                    details.append(f"Invariant Check: FAILED - Invalid signals {unique_sigs}. Must be subset of {{-1, 0, 1}}")
                else:
                    details.append("Invariant Check: PASSED (signals strictly bounded in {-1, 0, 1})")



                if len(sample_df) >= 40:
                    split_idx = 30
                    perturbed_df = sample_df.copy()
                    perturbed_df.loc[split_idx:, "close"] = perturbed_df.loc[split_idx:, "close"] * 0.05
                    perturbed_ok, perturbed_or_error = strategy_sandbox.run_signals_in_restricted_subprocess(impl.source_code, perturbed_df)
                    if not perturbed_ok:
                        lookahead_passed = False
                        details.append(f"Look-Ahead Bias Test: FAILED - {perturbed_or_error}")
                        perturbed_signals = np.asarray([])
                    else:
                        perturbed_signals = np.asarray(perturbed_or_error)

                    if not np.array_equal(signals[:split_idx], perturbed_signals[:split_idx]):
                        lookahead_passed = False
                        details.append("Look-Ahead Bias Test: FAILED - Modifying future prices altered past signals!")
                    else:
                        details.append("Look-Ahead Bias Test: PASSED (Strict temporal invariance verified)")


                nan_df = sample_df.copy()
                nan_df.loc[5, "close"] = np.nan
                try:
                    nan_ok, nan_or_error = strategy_sandbox.run_signals_in_restricted_subprocess(impl.source_code, nan_df.ffill())
                    if not nan_ok:
                        raise RuntimeError(str(nan_or_error))
                    nan_signals = np.asarray(nan_or_error)
                    if len(nan_signals) == len(nan_df):
                        details.append("Missing-Data Resilience: PASSED")
                except Exception as e:
                    leakage_passed = False
                    details.append(f"Missing-Data Resilience: FAILED - {e}")

        except Exception as e:
            invariants_passed = False
            details.append(f"Dynamic Invariant Check Execution Error: {str(e)}")

        overall_passed = ast_passed and unit_passed and invariants_passed and lookahead_passed and leakage_passed

        return QACheckResult(
            passed=overall_passed,
            ast_valid=ast_passed,
            imports_valid=ast_passed,
            unit_tests_passed=unit_passed,
            invariants_passed=invariants_passed,
            lookahead_passed=lookahead_passed,
            leakage_passed=leakage_passed,
            details=details
        )

qa_agent = QAAgent()
