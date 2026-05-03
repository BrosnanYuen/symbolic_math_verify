import unittest

from src.check_substitution import is_substitution_correct


class TestIsSubstitutionCorrectTrueCases(unittest.TestCase):
    def test_reciprocal_power_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["x", "y", "z"],
                "y = 1/x  + 5*z",
                "x  =  z^3",
                "y = 1/(z^3)  + 5*z",
            )
        )

    def test_scaled_power_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["x", "y", "z"],
                "y = 2*x + 5*z",
                "x = z^3",
                "y = 2*z^3 + 5*z",
            )
        )

    def test_rearranged_linear_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["x", "y", "z"],
                "y = 2*x + 1",
                "2*x = z",
                "y = z + 1",
            )
        )

    def test_reverse_side_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["x", "y", "z"],
                "y = z^3 + 1",
                "x = z^3",
                "y = x + 1",
            )
        )

    def test_grouped_expression_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["x", "y", "z", "a"],
                "y = (x + 1)^2 + z",
                "x + 1 = a",
                "y = a^2 + z",
            )
        )

    def test_trigonometric_identity_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["x", "y", "z"],
                "y = sin(x)^2 + cos(x)^2 + z",
                "sin(x)^2 + cos(x)^2 = 1",
                "y = 1 + z",
            )
        )

    def test_exponential_expression_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["x", "y", "z", "a"],
                "y = exp(x) + z",
                "a = exp(x)",
                "y = a + z",
            )
        )

    def test_log_expression_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["x", "y", "z", "a"],
                "y = log(x) + z",
                "log(x) = a",
                "y = a + z",
            )
        )

    def test_zero_product_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["a", "b", "c", "z"],
                "c = a*b + z",
                "a*b = 0",
                "c = z",
            )
        )

    def test_power_expression_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["x", "y", "z", "w"],
                "y = x^2 + z",
                "x^2 = w",
                "y = w + z",
            )
        )


class TestIsSubstitutionCorrectFalseCases(unittest.TestCase):
    def test_missing_multiplier_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["x", "y", "z"],
                "y = 2*x + 5*z",
                "x  =  z^3",
                "y = z^3 + 5*z",
            )
        )

    def test_wrong_reciprocal_power_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["x", "y", "z"],
                "y = 1/x + 5*z",
                "x = z^3",
                "y = 1/z + 5*z",
            )
        )

    def test_skipped_available_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["x", "y", "z"],
                "y = x + 1",
                "x = z",
                "y = x + 1",
            )
        )

    def test_ambiguous_root_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["x", "y", "z"],
                "y = x",
                "x^2 = z",
                "y = sqrt(z)",
            )
        )

    def test_wrong_rearranged_linear_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["x", "y", "z"],
                "y = 2*x + 1",
                "2*x = z",
                "y = 2*z + 1",
            )
        )

    def test_wrong_grouped_expression_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["x", "y", "z", "a"],
                "y = (x + 1)^2 + z",
                "x + 1 = a",
                "y = a + z",
            )
        )

    def test_wrong_zero_product_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["a", "b", "c", "z"],
                "c = a*b + z",
                "a*b = 0",
                "c = z + 1",
            )
        )

    def test_missing_constant_after_reverse_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["x", "y", "z"],
                "y = z^3 + 1",
                "x = z^3",
                "y = x",
            )
        )

    def test_wrong_compound_expression_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["x", "y", "z", "a"],
                "y = x + z",
                "x + z = a",
                "y = a + z",
            )
        )

    def test_wrong_trigonometric_identity_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["x", "y", "z"],
                "y = sin(x)^2 + cos(x)^2 + z",
                "sin(x)^2 + cos(x)^2 = 1",
                "y = z",
            )
        )


if __name__ == "__main__":
    unittest.main()
