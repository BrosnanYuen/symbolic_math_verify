"""Run the symbolic_math_mcp test modules one at a time."""

from __future__ import annotations

import subprocess
import sys
import os
from pathlib import Path


TEST_MODULES = [
    "tests.test_config",
    "tests.test_service",
    "tests.test_integration",
]


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    env = dict(os.environ)
    src_dir = str(project_root / "src")
    env["PYTHONPATH"] = src_dir if not env.get("PYTHONPATH") else f"{src_dir}:{env['PYTHONPATH']}"
    for module_name in TEST_MODULES:
        completed = subprocess.run(
            [sys.executable, "-m", "unittest", module_name],
            cwd=project_root,
            text=True,
            env=env,
        )
        if completed.returncode != 0:
            return completed.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
