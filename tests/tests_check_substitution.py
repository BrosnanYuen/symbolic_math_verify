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

    def test_fractional_linear_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["x", "y", "z", "a"],
                "y = x/2 + z",
                "x = 2*a",
                "y = a + z",
            )
        )

    def test_binomial_cube_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["x", "y", "z", "a"],
                "y = x^3 + z",
                "x = a + 1",
                "y = (a + 1)^3 + z",
            )
        )

    def test_shifted_difference_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["u", "v", "w", "k"],
                "u = v - w + 2",
                "v - w = k",
                "u = k + 2",
            )
        )

    def test_nested_trig_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["x", "y", "z", "t"],
                "y = sin(x) + z*t",
                "sin(x) = t",
                "y = t + z*t",
            )
        )

    def test_log_argument_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["x", "y", "z", "k"],
                "y = log(x + z) + 1",
                "x + z = k",
                "y = log(k) + 1",
            )
        )

    def test_exponential_factor_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["x", "y", "z", "a"],
                "y = z*exp(x) + 4",
                "exp(x) = a",
                "y = z*a + 4",
            )
        )

    def test_absolute_value_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["x", "y", "z", "u"],
                "y = Abs(x - z) + 3",
                "x - z = u",
                "y = Abs(u) + 3",
            )
        )

    def test_reciprocal_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["p", "q", "r", "s"],
                "p = q + 1/r",
                "r = 1/s",
                "p = q + s",
            )
        )

    def test_scaled_group_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["a", "b", "c", "m"],
                "c = 3*(a + b) - 7",
                "a + b = m",
                "c = 3*m - 7",
            )
        )

    def test_hyperbolic_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["x", "y", "z", "h"],
                "y = cosh(x) + z",
                "cosh(x) = h",
                "y = h + z",
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

    def test_fractional_linear_wrong_coefficient(self):
        self.assertFalse(
            is_substitution_correct(
                ["x", "y", "z", "a"],
                "y = x/2 + z",
                "x = 2*a",
                "y = 2*a + z",
            )
        )

    def test_binomial_cube_missing_power(self):
        self.assertFalse(
            is_substitution_correct(
                ["x", "y", "z", "a"],
                "y = x^3 + z",
                "x = a + 1",
                "y = a + 1 + z",
            )
        )

    def test_shifted_difference_wrong_constant(self):
        self.assertFalse(
            is_substitution_correct(
                ["u", "v", "w", "k"],
                "u = v - w + 2",
                "v - w = k",
                "u = k + 1",
            )
        )

    def test_nested_trig_wrong_sign(self):
        self.assertFalse(
            is_substitution_correct(
                ["x", "y", "z", "t"],
                "y = sin(x) + z*t",
                "sin(x) = t",
                "y = t - z*t",
            )
        )

    def test_log_argument_wrong_target(self):
        self.assertFalse(
            is_substitution_correct(
                ["x", "y", "z", "k"],
                "y = log(x + z) + 1",
                "x + z = k",
                "y = k + 1",
            )
        )

    def test_exponential_factor_missing_multiplier(self):
        self.assertFalse(
            is_substitution_correct(
                ["x", "y", "z", "a"],
                "y = z*exp(x) + 4",
                "exp(x) = a",
                "y = a + 4",
            )
        )

    def test_absolute_value_dropped_abs(self):
        self.assertFalse(
            is_substitution_correct(
                ["x", "y", "z", "u"],
                "y = Abs(x - z) + 3",
                "x - z = u",
                "y = u + 3",
            )
        )

    def test_reciprocal_substitution_wrong_inverse(self):
        self.assertFalse(
            is_substitution_correct(
                ["p", "q", "r", "s"],
                "p = q + 1/r",
                "r = 1/s",
                "p = q + 1/s",
            )
        )

    def test_scaled_group_wrong_scale(self):
        self.assertFalse(
            is_substitution_correct(
                ["a", "b", "c", "m"],
                "c = 3*(a + b) - 7",
                "a + b = m",
                "c = m - 7",
            )
        )

    def test_hyperbolic_substitution_wrong_function(self):
        self.assertFalse(
            is_substitution_correct(
                ["x", "y", "z", "h"],
                "y = cosh(x) + z",
                "cosh(x) = h",
                "y = sinh(h) + z",
            )
        )


if __name__ == "__main__":
    unittest.main()
