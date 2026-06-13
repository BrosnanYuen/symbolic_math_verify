import unittest
import hashlib
from pathlib import Path

from src.verify_yaml import verify_yaml_file


class TestVerifyYamlFile(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(__file__).resolve().parent.parent / "test_yaml"

    def test_valid_yaml_files(self):
        valid_files = sorted(self.base_dir.glob("valid_*.yaml"))
        self.assertTrue(valid_files, "Expected at least one valid YAML test file")
        for yaml_file in valid_files:
            with self.subTest(file=yaml_file.name):
                result = verify_yaml_file(str(yaml_file)) == "Math proofs are valid"
                self.assertTrue(result, msg=f"Unexpected result for {yaml_file.name}: {verify_yaml_file(str(yaml_file))}")

    def test_invalid_yaml_files(self):
        invalid_files = sorted(self.base_dir.glob("invalid_*.yaml"))
        self.assertTrue(invalid_files, "Expected at least one invalid YAML test file")
        for yaml_file in invalid_files:
            with self.subTest(file=yaml_file.name):
                result_text = verify_yaml_file(str(yaml_file))
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
