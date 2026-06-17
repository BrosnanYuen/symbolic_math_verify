from __future__ import annotations

import os
import tempfile
import threading
import time
import unittest
from pathlib import Path

from symbolic_math_mcp.service import SymbolicMathService


class TestSymbolicMathService(unittest.TestCase):
    def test_success_response_uses_verifier_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            yaml_path = Path(tmpdir) / "valid.yaml"
            yaml_path.write_text("axioms:\n  a:\n    vars: [x]\n    equation: \"x = x + 1\"\n", encoding="utf-8")
            service = SymbolicMathService(1, 5, ("axioms:",), verifier=lambda _: "Math proofs are valid")
            self.addCleanup(service.shutdown)

            response = service.check_symbolic_math(str(yaml_path))

        self.assertEqual("Tool call completed!", response["status"])
        self.assertEqual("Math proofs are valid", response["result"])

    def test_file_not_found_response(self) -> None:
        service = SymbolicMathService(1, 5, verifier=lambda _: "unused")
        self.addCleanup(service.shutdown)
        response = service.check_symbolic_math("missing.yaml")
        self.assertEqual("FILE NOT FOUND!", response["result"])

    def test_non_yaml_filename_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "input.txt"
            path.write_text("content", encoding="utf-8")
            service = SymbolicMathService(1, 5, verifier=lambda _: "unused")
            self.addCleanup(service.shutdown)
            response = service.check_symbolic_math(str(path))
        self.assertEqual("FILE NOT FOUND!", response["result"])

    def test_missing_required_yaml_string_returns_sync_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            yaml_path = Path(tmpdir) / "missing.yaml"
            yaml_path.write_text("theorem:\n  vars: [x]\n", encoding="utf-8")
            service = SymbolicMathService(1, 5, ("axioms:", "equation:"), verifier=lambda _: "unused")
            self.addCleanup(service.shutdown)

            response = service.check_symbolic_math(str(yaml_path))

        self.assertEqual("Missing a string from the .yaml file!", response["status"])
        self.assertEqual("axioms:, equation:", response["result"])

    def test_file_read_error_response(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            yaml_path = Path(tmpdir) / "blocked.yaml"
            yaml_path.write_text("axioms: {}\n", encoding="utf-8")
            os.chmod(yaml_path, 0)
            service = SymbolicMathService(1, 5, verifier=lambda _: "unused")
            self.addCleanup(service.shutdown)
            try:
                response = service.check_symbolic_math(str(yaml_path))
            finally:
                os.chmod(yaml_path, 0o644)
        self.assertEqual("FILE CANNOT BE READ!", response["result"])

    def test_timeout_response(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            yaml_path = Path(tmpdir) / "slow.yaml"
            yaml_path.write_text("axioms: {}\n", encoding="utf-8")

            def slow_verifier(_: str) -> str:
                time.sleep(0.3)
                return "Math proofs are valid"

            service = SymbolicMathService(1, 0.1, verifier=slow_verifier)
            self.addCleanup(service.shutdown)
            response = service.check_symbolic_math(str(yaml_path))
        self.assertEqual("TIMEOUT ERROR!", response["result"])

    def test_parallel_success_response_uses_verifier_results(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            first_path = Path(tmpdir) / "first.yaml"
            second_path = Path(tmpdir) / "second.yaml"
            first_path.write_text("axioms: {}\n", encoding="utf-8")
            second_path.write_text("axioms: {}\n", encoding="utf-8")

            def verifier(filename: str) -> str:
                return f"verified:{Path(filename).name}"

            service = SymbolicMathService(2, 5, ("axioms:",), verifier=verifier)
            self.addCleanup(service.shutdown)

            response = service.check_symbolic_math_parallel(tmpdir)

        self.assertEqual("Parallel Tool call completed!", response["status"])
        self.assertEqual(tmpdir, response["dir_path"])
        self.assertEqual(
            {
                str(first_path): "verified:first.yaml",
                str(second_path): "verified:second.yaml",
            },
            response["result"],
        )

    def test_parallel_requires_absolute_directory(self) -> None:
        service = SymbolicMathService(1, 5, verifier=lambda _: "unused")
        self.addCleanup(service.shutdown)
        response = service.check_symbolic_math_parallel("tests_yaml")
        self.assertEqual("FILE NOT FOUND!", response["result"])

    def test_parallel_returns_missing_string_error_before_verifier(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "missing.yaml").write_text("theorem:\n  vars: [x]\n", encoding="utf-8")
            service = SymbolicMathService(1, 5, ("axioms:",), verifier=lambda _: "unused")
            self.addCleanup(service.shutdown)

            response = service.check_symbolic_math_parallel(tmpdir)

        self.assertEqual("Missing a string from the .yaml file!", response["status"])
        self.assertEqual("axioms:", response["result"])

    def test_parallel_timeout_response(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            for index in range(2):
                (Path(tmpdir) / f"slow_{index}.yaml").write_text("axioms: {}\n", encoding="utf-8")

            def slow_verifier(_: str) -> str:
                time.sleep(0.3)
                return "Math proofs are valid"

            service = SymbolicMathService(2, 0.1, ("axioms:",), verifier=slow_verifier)
            self.addCleanup(service.shutdown)

            response = service.check_symbolic_math_parallel(tmpdir)

        self.assertEqual("TIMEOUT ERROR!", response["result"])

    def test_parallel_max_requests_bounds_worker_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            for index in range(3):
                (Path(tmpdir) / f"proof_{index}.yaml").write_text("axioms: {}\n", encoding="utf-8")

            active = 0
            max_active = 0
            lock = threading.Lock()

            def verifier(_: str) -> str:
                nonlocal active, max_active
                with lock:
                    active += 1
                    max_active = max(max_active, active)
                time.sleep(0.2)
                with lock:
                    active -= 1
                return "Math proofs are valid"

            service = SymbolicMathService(2, 2, ("axioms:",), verifier=verifier)
            self.addCleanup(service.shutdown)

            response = service.check_symbolic_math_parallel(tmpdir)

        self.assertEqual("Parallel Tool call completed!", response["status"])
        self.assertEqual(2, max_active)

    def test_max_requests_queues_work(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            yaml_one = Path(tmpdir) / "one.yaml"
            yaml_two = Path(tmpdir) / "two.yaml"
            yaml_one.write_text("axioms: {}\n", encoding="utf-8")
            yaml_two.write_text("axioms: {}\n", encoding="utf-8")

            active = 0
            max_active = 0
            lock = threading.Lock()

            def verifier(_: str) -> str:
                nonlocal active, max_active
                with lock:
                    active += 1
                    max_active = max(max_active, active)
                time.sleep(0.2)
                with lock:
                    active -= 1
                return "Math proofs are valid"

            service = SymbolicMathService(1, 2, ("axioms:",), verifier=verifier)
            self.addCleanup(service.shutdown)
            results: list[dict[str, str]] = []

            def run_check(path: Path) -> None:
                results.append(service.check_symbolic_math(str(path)))

            thread_one = threading.Thread(target=run_check, args=(yaml_one,))
            thread_two = threading.Thread(target=run_check, args=(yaml_two,))
            started = time.monotonic()
            thread_one.start()
            thread_two.start()
            thread_one.join()
            thread_two.join()
            elapsed = time.monotonic() - started

        self.assertEqual(2, len(results))
        self.assertEqual(1, max_active)
        self.assertGreaterEqual(elapsed, 0.35)
        self.assertTrue(all(result["status"] == "Tool call completed!" for result in results))
