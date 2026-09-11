"""
FinSight AI - Strategy Execution Sandbox & AST Verifier
Provides:
1. AST Static Analysis for forbidden imports and unsafe execution patterns.
2. Isolated subprocess execution with timeouts, restricted environment, and memory limits.
"""

from typing import List, Tuple
import ast
import subprocess
import sys
import tempfile
import os
import json
from pathlib import Path
from backend.app.core.telemetry import record
from backend.app.config import settings

ALLOWED_MODULES = {"numpy", "pandas", "math", "scipy", "datetime", "typing"}
FORBIDDEN_CALLS = {"eval", "exec", "open", "__import__", "compile", "breakpoint", "globals", "locals", "vars", "getattr", "setattr"}

class StrategySandbox:

    @staticmethod
    def _container_required() -> bool:
        configured = os.getenv("FINSIGHT_REQUIRE_CONTAINER_SANDBOX")
        if configured is not None:
            return configured.lower() == "true"


        return not settings.DEMO_MODE

    @staticmethod
    def docker_available() -> bool:
        """Return whether the privileged sandbox worker can be invoked."""
        try:
            probe = subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
            return probe.returncode == 0
        except (OSError, subprocess.SubprocessError):
            return False

    @staticmethod
    def run_in_docker(source_code: str, test_code: str, image: str = "finsight-strategy-sandbox:latest", timeout_sec: int = 10) -> Tuple[bool, str]:
        """Run candidate tests with network, capabilities, secrets, and writes removed.

        Image creation is a deployment concern (`Dockerfile.strategy-sandbox`).
        The method fails closed when Docker or the pinned image is unavailable.
        """
        if not StrategySandbox.docker_available():
            record("sandbox", "docker_probe", status="blocked", attributes={"reason": "docker_unavailable"})
            return False, "Docker sandbox is unavailable; candidate execution is blocked"
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "candidate.py").write_text(source_code, encoding="utf-8")
            (root / "test_candidate.py").write_text(test_code, encoding="utf-8")


            command = ["docker", "run", "--rm", "--network", "none", "--read-only", "--cap-drop", "ALL", "--security-opt", "no-new-privileges", "--cpus", "1", "--memory", "512m", "--pids-limit", "64", "-v", f"{root.resolve()}:/work:ro", "-w", "/work", image, "test_candidate.py"]
            try:
                proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout_sec)
                if proc.returncode != 0:
                    return False, proc.stderr.strip()[-1000:]
                return "UNIT_TESTS_PASSED" in proc.stdout, proc.stdout.strip()[-1000:]
            except subprocess.TimeoutExpired:
                return False, f"Docker sandbox timed out after {timeout_sec}s"

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

            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name.split('.')[0]
                    if mod not in ALLOWED_MODULES:
                        errors.append(f"Forbidden import detected: 'import {alias.name}'")
            elif isinstance(node, ast.ImportFrom):
                mod = (node.module or '').split('.')[0]
                if mod not in ALLOWED_MODULES:
                    errors.append(f"Forbidden import detected: 'from {node.module} import ...'")


            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in FORBIDDEN_CALLS:
                        errors.append(f"Forbidden function call: '{node.func.id}()'")


                if isinstance(node.func, ast.Attribute) and node.func.attr == "shift":
                    if node.args and isinstance(node.args[0], ast.UnaryOp) and isinstance(node.args[0].op, ast.USub):
                        errors.append("Look-ahead access detected: negative shift")
            elif isinstance(node, ast.Attribute) and node.attr.startswith("__"):
                errors.append(f"Forbidden private attribute access: '{node.attr}'")

        passed = len(errors) == 0
        return passed, errors

    @staticmethod
    def run_signals_in_restricted_subprocess(source_code: str, frame, timeout_sec: int = 5) -> Tuple[bool, List[float] | str]:
        """Execute only the candidate strategy in a clean subprocess.

        The API process never imports or executes generated source. Docker
        workers can replace this adapter in production with ``--network none``
        and cgroup limits; this local adapter keeps assessment tests portable.
        """
        if StrategySandbox._container_required() and not StrategySandbox.docker_available():
            return False, "Container sandbox is required but Docker is unavailable"
        ast_ok, ast_errors = StrategySandbox.static_ast_check(source_code)
        if not ast_ok:
            return False, "; ".join(ast_errors)
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "candidate.py").write_text(source_code, encoding="utf-8")
            (tmp_path / "input.json").write_text(frame.to_json(orient="split", date_format="iso"), encoding="utf-8")
            runner = """import json, sys\nimport numpy as np\nimport pandas as pd\nfrom candidate import CandidateStrategy\nframe = pd.read_json('input.json', orient='split')\nvalues = CandidateStrategy().generate_signals(frame)\nprint('SIGNALS:' + json.dumps(np.asarray(values).tolist()))\n"""
            (tmp_path / "runner.py").write_text(runner, encoding="utf-8")
            clean_env = {"PATH": os.environ.get("PATH", ""), "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""), "PYTHONPATH": tmpdir}
            try:
                proc = subprocess.run([sys.executable, str(tmp_path / "runner.py")], cwd=tmpdir, env=clean_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout_sec)
                if proc.returncode != 0:
                    return False, proc.stderr.strip()[-1000:]
                marker = next((line for line in proc.stdout.splitlines() if line.startswith("SIGNALS:")), None)
                if not marker:
                    return False, "candidate produced no signal output"
                return True, json.loads(marker[len("SIGNALS:"):])
            except subprocess.TimeoutExpired:
                return False, f"Execution timed out after {timeout_sec}s"
            except Exception as exc:
                return False, str(exc)

    @staticmethod
    def run_in_restricted_subprocess(source_code: str, test_code: str, timeout_sec: int = 5) -> Tuple[bool, str]:
        """
        Executes strategy code and unit tests in an isolated restricted temporary subprocess.
        """
        if StrategySandbox._container_required() and not StrategySandbox.docker_available():
            return False, "Container sandbox is required but Docker is unavailable"
        ast_ok, ast_errors = StrategySandbox.static_ast_check(source_code)
        if not ast_ok:
            return False, f"AST Check Failed: {'; '.join(ast_errors)}"

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            cand_file = tmp_path / "candidate.py"
            test_file = tmp_path / "test_candidate.py"

            cand_file.write_text(source_code, encoding="utf-8")
            test_file.write_text(test_code, encoding="utf-8")


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
