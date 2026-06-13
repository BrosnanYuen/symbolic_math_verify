import unittest
from pathlib import Path

from src.verify_yaml import verify_yaml_file


class TestVerifyYamlFile(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(__file__).resolve().parent.parent / "test_yaml"
        self.new_valid_fixtures = {
            "valid_18_substitution_basic.yaml",
            "valid_19_substitution_then_rearrange.yaml",
            "valid_20_substitution_from_prior_theorem.yaml",
            "valid_21_substitution_equivalent_form.yaml",
        }
        self.new_invalid_fixtures = {
            "invalid_18_substitution_not_applied.yaml",
            "invalid_19_substitution_unknown_equation.yaml",
            "invalid_20_substitution_missing_equation.yaml",
            "invalid_21_substitution_missing_source.yaml",
        }

    def test_valid_yaml_files(self):
        valid_files = sorted(self.base_dir.glob("valid_*.yaml"))
        self.assertTrue(valid_files, "Expected at least one valid YAML test file")
        for yaml_file in valid_files:
            with self.subTest(file=yaml_file.name):
                result = verify_yaml_file(str(yaml_file))
                self.assertEqual("Math proofs are valid", result)

    def test_invalid_yaml_files(self):
        invalid_files = sorted(self.base_dir.glob("invalid_*.yaml"))
        self.assertTrue(invalid_files, "Expected at least one invalid YAML test file")
        for yaml_file in invalid_files:
            with self.subTest(file=yaml_file.name):
                result = verify_yaml_file(str(yaml_file))
                self.assertTrue(result.startswith("Error!"), msg=f"Unexpected result for {yaml_file.name}: {result}")

    def test_equal_count_valid_invalid(self):
        valid_count = len(list(self.base_dir.glob("valid_*.yaml")))
        invalid_count = len(list(self.base_dir.glob("invalid_*.yaml")))
        self.assertEqual(valid_count, invalid_count)

    def test_new_substitution_yaml_files_exist(self):
        valid_files = {path.name for path in self.base_dir.glob("valid_*.yaml")}
        invalid_files = {path.name for path in self.base_dir.glob("invalid_*.yaml")}
        self.assertTrue(self.new_valid_fixtures.issubset(valid_files))
        self.assertTrue(self.new_invalid_fixtures.issubset(invalid_files))


if __name__ == "__main__":
    unittest.main()
