import unittest
from pathlib import Path

from src.verify_yaml import verify_yaml_file


class TestVerifyYamlFile(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(__file__).resolve().parent.parent / "test_yaml"
        self.promoted_valid_fixtures = {
            "invalid_01_axiom_missing_vars.yaml",
            "invalid_07_prompt_axiom_missing_vars.yaml",
        }

    def _expected_valid_files(self) -> list[Path]:
        valid_files = {path.name: path for path in self.base_dir.glob("valid_*.yaml")}
        for fixture_name in self.promoted_valid_fixtures:
            valid_files[fixture_name] = self.base_dir / fixture_name
        return [valid_files[name] for name in sorted(valid_files)]

    def _expected_invalid_files(self) -> list[Path]:
        invalid_files = {
            path.name: path
            for path in self.base_dir.glob("invalid_*.yaml")
            if path.name not in self.promoted_valid_fixtures
        }
        return [invalid_files[name] for name in sorted(invalid_files)]

    def test_valid_yaml_files(self):
        valid_files = self._expected_valid_files()
        self.assertTrue(valid_files, "Expected at least one valid YAML test file")
        for yaml_file in valid_files:
            with self.subTest(file=yaml_file.name):
                result = verify_yaml_file(str(yaml_file))
                self.assertEqual("Math proofs are valid", result)

    def test_invalid_yaml_files(self):
        invalid_files = self._expected_invalid_files()
        self.assertTrue(invalid_files, "Expected at least one invalid YAML test file")
        for yaml_file in invalid_files:
            with self.subTest(file=yaml_file.name):
                result = verify_yaml_file(str(yaml_file))
                self.assertTrue(result.startswith("Error!"), msg=f"Unexpected result for {yaml_file.name}: {result}")

    def test_equal_count_valid_invalid(self):
        valid_count = len(list(self.base_dir.glob("valid_*.yaml")))
        invalid_count = len(list(self.base_dir.glob("invalid_*.yaml")))
        self.assertEqual(valid_count, invalid_count)

    def test_fixture_expectations_cover_all_yaml_files(self):
        expected_valid = {path.name for path in self._expected_valid_files()}
        expected_invalid = {path.name for path in self._expected_invalid_files()}
        all_yaml_files = {path.name for path in self.base_dir.glob("*.yaml")}
        self.assertFalse(expected_valid.intersection(expected_invalid))
        self.assertEqual(all_yaml_files, expected_valid.union(expected_invalid))

    def test_autovars_yaml_files_exist(self):
        valid_autovars = {
            path.name for path in self.base_dir.glob("valid_*.yaml") if "_autovars_" in path.name
        }
        invalid_autovars = {
            path.name for path in self.base_dir.glob("invalid_*.yaml") if "_autovars_" in path.name
        }
        self.assertEqual(25, len(valid_autovars))
        self.assertEqual(25, len(invalid_autovars))


if __name__ == "__main__":
    unittest.main()
