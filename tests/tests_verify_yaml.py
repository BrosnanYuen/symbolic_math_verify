import concurrent.futures
import unittest
import hashlib
import os
from pathlib import Path

from src.verify_yaml import verify_yaml_file


def _verify_yaml_fixture(file_path: str) -> tuple[str, str]:
    """Return one fixture name and its verifier result for parallel test execution."""
    path = Path(file_path)
    return path.name, verify_yaml_file(str(path))


class TestVerifyYamlFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = Path(__file__).resolve().parent.parent / "test_yaml"

    def _verify_files_parallel(self, yaml_files: list[Path]) -> dict[str, str]:
        """Verify fixture files concurrently and return results by filename."""
        if not yaml_files:
            return {}
        max_workers = min(len(yaml_files), os.cpu_count() or 1)
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            results = executor.map(_verify_yaml_fixture, (str(path) for path in yaml_files))
            return dict(results)

    def test_valid_yaml_files(self):
        valid_files = sorted(self.base_dir.glob("valid_*.yaml"))
        self.assertTrue(valid_files, "Expected at least one valid YAML test file")
        results_by_name = self._verify_files_parallel(valid_files)
        for yaml_file in valid_files:
            with self.subTest(file=yaml_file.name):
                result_text = results_by_name[yaml_file.name]
                result = result_text == "Math proofs are valid"
                self.assertTrue(result, msg=f"Unexpected result for {yaml_file.name}: {result_text}")

    def test_invalid_yaml_files(self):
        invalid_files = sorted(self.base_dir.glob("invalid_*.yaml"))
        self.assertTrue(invalid_files, "Expected at least one invalid YAML test file")
        results_by_name = self._verify_files_parallel(invalid_files)
        for yaml_file in invalid_files:
            with self.subTest(file=yaml_file.name):
                result_text = results_by_name[yaml_file.name]
                result = result_text == "Math proofs are valid"
                self.assertFalse(result, msg=f"Unexpected result for {yaml_file.name}: {result_text}")

    def test_equal_count_valid_invalid(self):
        valid_count = len(list(self.base_dir.glob("valid_*.yaml")))
        invalid_count = len(list(self.base_dir.glob("invalid_*.yaml")))
        self.assertEqual(valid_count, invalid_count)

    def test_yaml_fixture_contents_are_unique(self):
        by_hash: dict[str, list[str]] = {}
        for yaml_file in sorted(self.base_dir.glob("*.yaml")):
            digest = hashlib.sha256(yaml_file.read_bytes()).hexdigest()
            by_hash.setdefault(digest, []).append(yaml_file.name)
        duplicates = [names for names in by_hash.values() if len(names) > 1]
        self.assertEqual([], duplicates)

    def test_autovars_yaml_files_exist(self):
        valid_autovars = {
            path.name for path in self.base_dir.glob("valid_*.yaml") if "_autovars_" in path.name
        }
        invalid_autovars = {
            path.name for path in self.base_dir.glob("invalid_*.yaml") if "_autovars_" in path.name
        }
        self.assertTrue(len(valid_autovars) > 0)
        self.assertTrue(len(invalid_autovars) > 0)


if __name__ == "__main__":
    unittest.main()
