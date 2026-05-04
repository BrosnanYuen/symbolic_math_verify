"""Run unittest discovery patterns in parallel across test files."""

from __future__ import annotations

import concurrent.futures
import importlib.util
import os
import subprocess
import sys
import unittest
from pathlib import Path


def _iter_test_cases(suite: unittest.TestSuite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from _iter_test_cases(item)
        else:
            yield item


def _discover_test_ids() -> list[str]:
    project_root = str(Path(".").resolve())
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    loader = unittest.defaultTestLoader
    test_ids: list[str] = []
    for test_file in sorted(Path("tests").glob("tests_*.py")):
        module_name = test_file.stem
        spec = importlib.util.spec_from_file_location(module_name, test_file)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        suite = loader.loadTestsFromModule(module)
        test_ids.extend(case.id() for case in _iter_test_cases(suite))
    return test_ids


def _run_test_id(test_id: str) -> tuple[str, int, str]:
    command = [
        sys.executable,
        "-m",
        "unittest",
        test_id,
    ]
    env = dict(os.environ)
    tests_path = str(Path("tests").resolve())
    env["PYTHONPATH"] = tests_path if not env.get("PYTHONPATH") else f"{tests_path}:{env['PYTHONPATH']}"
    completed = subprocess.run(command, capture_output=True, text=True, env=env)
    output = (completed.stdout or "") + (completed.stderr or "")
    return test_id, completed.returncode, output


def main() -> int:
    test_ids = _discover_test_ids()
    if not test_ids:
        print("No tests matched tests/tests_*.py")
        return 1

    workers = os.cpu_count() or 1
    print(f"Detected CPU cores: {workers}")
    print(f"Running {len(test_ids)} tests in parallel")

    failed = False
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(_run_test_id, test_id) for test_id in test_ids]
        for future in concurrent.futures.as_completed(futures):
            test_id, returncode, output = future.result()
            status = "PASS" if returncode == 0 else "FAIL"
            print(f"[{status}] {test_id}")
            if returncode != 0:
                failed = True
                print(output.rstrip())

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
