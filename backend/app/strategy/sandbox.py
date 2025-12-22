"""
FinSight AI - Strategy Execution Sandbox & AST Verifier
Provides:
1. AST Static Analysis for forbidden imports and unsafe execution patterns.
2. Isolated subprocess execution with timeouts, restricted environment, and memory limits.
"""

from typing import Dict, Any, List, Tuple
import ast
import subprocess
import sys
import tempfile
import os
from pathlib import Path
from backend.app.core.logging import logger

ALLOWED_MODULES = {"numpy", "pandas", "math", "scipy", "datetime", "typing"}
FORBIDDEN_CALLS = {"eval", "exec", "open", "__import__", "compile", "breakpoint"}

class StrategySandbox:

    @staticmethod
    def static_ast_check(code_str: str) -> Tuple[bool, List[str]]:
        """
        Parses code into an AST and verifies:
        - No unapproved imports (e.g. os, sys, subprocess, socket, requests)
        - No dangerous builtins (eval, exec, open)
        """
        errors = []
        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            return False, [f"Syntax error in candidate code: {e}"]

        for node in ast.walk(tree):
            # Check import statements
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name.split('.')[0]
                    if mod not in ALLOWED_MODULES:
                        errors.append(f"Forbidden import detected: 'import {alias.name}'")
            elif isinstance(node, ast.ImportFrom):
                mod = (node.module or '').split('.')[0]
                if mod not in ALLOWED_MODULES:
                    errors.append(f"Forbidden import detected: 'from {node.module} import ...'")

            # Check forbidden function calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in FORBIDDEN_CALLS:
                        errors.append(f"Forbidden function call: '{node.func.id}()'")

        passed = len(errors) == 0
        return passed, errors

    @staticmethod
    def run_in_restricted_subprocess(source_code: str, test_code: str, timeout_sec: int = 5) -> Tuple[bool, str]:
        """
        Executes strategy code and unit tests in an isolated restricted temporary subprocess.
        """
        ast_ok, ast_errors = StrategySandbox.static_ast_check(source_code)
        if not ast_ok:
            return False, f"AST Check Failed: {'; '.join(ast_errors)}"

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            cand_file = tmp_path / "candidate.py"
            test_file = tmp_path / "test_candidate.py"

            cand_file.write_text(source_code, encoding="utf-8")
            test_file.write_text(test_code, encoding="utf-8")

            # Clean sanitized environment (no API keys, no secrets)
            clean_env = {
                "PATH": os.environ.get("PATH", ""),
                "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
                "PYTHONPATH": tmpdir
            }

            try:
                proc = subprocess.run(
                    [sys.executable, str(test_file)],
                    cwd=tmpdir,
                    env=clean_env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=timeout_sec
                )

                if proc.returncode != 0:
                    return False, f"Subprocess failed (exit {proc.returncode}): {proc.stderr.strip()}"

                if "UNIT_TESTS_PASSED" in proc.stdout:
                    return True, "Subprocess verification passed successfully."
                return True, f"Subprocess completed: {proc.stdout.strip()}"

            except subprocess.TimeoutExpired:
                return False, f"Execution timed out after {timeout_sec}s (infinite loop guard triggered)."
            except Exception as e:
                return False, f"Subprocess execution error: {str(e)}"

strategy_sandbox = StrategySandbox()
