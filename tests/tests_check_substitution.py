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

    def test_true_four_var_quadratic_group_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["x", "y", "z", "w"],
                "y = (x + z) + w",
                "x + z = w",
                "y = w + w",
            )
        )

    def test_true_four_var_fraction_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["a", "b", "c", "d"],
                "a = b/c + d",
                "c = 1/d",
                "a = b*d + d",
            )
        )

    def test_true_four_var_exp_shift_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["m", "n", "p", "q"],
                "m = exp(n) + p + q",
                "exp(n) = q",
                "m = q + p + q",
            )
        )

    def test_true_four_var_log_scale_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["u", "v", "w", "k"],
                "u = 3*log(v*w) + k",
                "log(v*w) = k",
                "u = 3*k + k",
            )
        )

    def test_true_four_var_trig_difference_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["r", "s", "t", "q"],
                "r = sin(s) - t + q",
                "sin(s) = t",
                "r = t - t + q",
            )
        )

    def test_true_four_var_abs_scaled_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["x", "y", "z", "u"],
                "y = 2*Abs(x - z) + u",
                "x - z = u",
                "y = 2*Abs(u) + u",
            )
        )

    def test_true_four_var_linear_combination_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["a", "b", "c", "d"],
                "d = 5*a - 2*b + c",
                "5*a - 2*b = c",
                "d = c + c",
            )
        )

    def test_true_four_var_sqrt_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["p", "q", "r", "s"],
                "p = sqrt(q + r) + s",
                "q + r = s^2",
                "p = sqrt(s^2) + s",
            )
        )

    def test_true_four_var_hyperbolic_product_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["x", "y", "z", "h"],
                "y = z*cosh(x) + h",
                "cosh(x) = h",
                "y = z*h + h",
            )
        )

    def test_true_four_var_reciprocal_shift_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["f", "g", "h", "k"],
                "f = g + 1/h + k",
                "h = 1/k",
                "f = g + k + k",
            )
        )

    def test_true_four_var_quadratic_group_substitution2(self):
        self.assertTrue(
            is_substitution_correct(
                ["x", "y", "z", "w"],
                "y = (x + z)^2 + w",
                "x + z = w",
                "y = w^2 + w",
            )
        )

    def test_true_four_var_quadratic_group_substitution3(self):
        self.assertTrue(
            is_substitution_correct(
                ["m", "n", "p", "q"],
                "m = exp(n - p) + q",
                "n - p = q",
                "m = exp(q) + q",
            )
        )

    def test_true_four_var_reciprocal_shift_substitution4(self):
        self.assertTrue(
            is_substitution_correct(
                ["f", "g", "h", "k"],
                "f = g + 1/(h + k)",
                "h + k = g",
                "f = g + 1/g",
            )
        )

    def test_true_five_var_affine_group_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["a", "b", "c", "d", "k"],
                "k = 2*a + 3*b + c - d",
                "2*a + 3*b = c",
                "k = c + c - d",
            )
        )

    def test_true_five_var_fractional_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["p", "q", "r", "s", "t"],
                "t = p/q + r - s",
                "q = 1/s",
                "t = p*s + r - s",
            )
        )

    def test_true_five_var_exponential_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["m", "n", "u", "v", "w"],
                "w = 2*exp(m - n) + u - v",
                "exp(m - n) = v",
                "w = 2*v + u - v",
            )
        )

    def test_true_five_var_trig_product_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["x", "y", "z", "u", "v"],
                "v = z*sin(x + y) + u",
                "sin(x + y) = u",
                "v = z*u + u",
            )
        )

    def test_true_five_var_log_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["a", "b", "c", "d", "k"],
                "k = log(a*b) + c - d",
                "log(a*b) = d",
                "k = d + c - d",
            )
        )

    def test_true_five_var_abs_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["x", "y", "z", "p", "q"],
                "q = 3*Abs(x - y) + z - p",
                "x - y = p",
                "q = 3*Abs(p) + z - p",
            )
        )

    def test_true_five_var_sqrt_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["r", "s", "t", "u", "v"],
                "v = sqrt(r + s) + t - u",
                "r + s = u^2",
                "v = sqrt(u^2) + t - u",
            )
        )

    def test_true_five_var_polynomial_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["f", "g", "h", "k", "m"],
                "m = f^2 + 2*f*g + h - k",
                "f^2 + 2*f*g = k",
                "m = k + h - k",
            )
        )

    def test_true_five_var_hyperbolic_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["a", "b", "c", "d", "e"],
                "e = c*cosh(a - b) + d",
                "cosh(a - b) = b",
                "e = c*b + d",
            )
        )

    def test_true_five_var_reciprocal_shift_substitution(self):
        self.assertTrue(
            is_substitution_correct(
                ["i", "j", "k", "l", "m"],
                "m = i + 1/(j + k) + l",
                "j + k = i",
                "m = i + 1/i + l",
            )
        )

    def test_true_five_var_affine_group_substitution2(self):
        self.assertTrue(
            is_substitution_correct(
                ["a", "b", "c", "d", "q"],
                "q = 4*(a + b) - c + d",
                "a + b = c",
                "q = 4*c - c + d",
            )
        )

    def test_true_five_var_affine_group_substitution3(self):
        self.assertTrue(
            is_substitution_correct(
                ["a", "b", "c", "d", "q", "g"],
                "q = 7*(a + b + c) - g + d",
                "a + b + c = g",
                "q = 7*g - g + d",
            )
        )

    def test_true_five_var_affine_group_substitution4(self):
        self.assertTrue(
            is_substitution_correct(
                ["a", "b", "c", "d", "z", "g", "f"],
                "f = cos(sin(a + c + b) + d) + z - g",
                "a + c + b = z",
                "f = cos(sin(z) + d) + z - g",
            )
        )

    def test_true_five_var_affine_group_substitution5(self):
        self.assertTrue(
            is_substitution_correct(
                ["a", "b", "c", "d", "z", "g", "f"],
                "f = cos(sin(a + c + b) + d) + z - g",
                "sin(a + c + b) = g",
                "f = cos(g + d) + z - g",
            )
        )

    def test_true_five_var_affine_group_substitution6(self):
        self.assertTrue(
            is_substitution_correct(
                ["a", "b", "c", "d", "q", "g"],
                "q = 6*(a + b + c)^3 - g + d",
                "a + b + c = g",
                "q = 6*(g^3) - g + d",
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

    def test_false_four_var_quadratic_group_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["x", "y", "z", "w"],
                "y = (x + z)^2 + w",
                "x + z = w",
                "y = w + w",
            )
        )

    def test_false_four_var_fraction_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["a", "b", "c", "d"],
                "a = b/c + d",
                "c = 1/d",
                "a = b/d + d",
            )
        )

    def test_false_four_var_exp_shift_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["m", "n", "p", "q"],
                "m = exp(n - p) + q",
                "n - p = q",
                "m = exp(q) - q",
            )
        )

    def test_false_four_var_log_scale_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["u", "v", "w", "k"],
                "u = 3*log(v*w) + k",
                "log(v*w) = k",
                "u = 3*k",
            )
        )

    def test_false_four_var_trig_difference_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["r", "s", "t", "q"],
                "r = sin(s) - t + q",
                "sin(s) = t",
                "r = t + q",
            )
        )

    def test_false_four_var_abs_scaled_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["x", "y", "z", "u"],
                "y = 2*Abs(x - z) + u",
                "x - z = u",
                "y = 2*u + u",
            )
        )

    def test_false_four_var_linear_combination_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["a", "b", "c", "d"],
                "d = 5*a - 2*b + c",
                "5*a - 2*b = c",
                "d = c",
            )
        )

    def test_false_four_var_sqrt_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["p", "q", "r", "s"],
                "p = sqrt(q + r) + s",
                "q + r = s^2",
                "p = s + s",
            )
        )

    def test_false_four_var_hyperbolic_product_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["x", "y", "z", "h"],
                "y = z*cosh(x) + h",
                "cosh(x) = h",
                "y = z*sinh(h) + h",
            )
        )

    def test_false_four_var_reciprocal_shift_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["f", "g", "h", "k"],
                "f = g + 1/(h + k)",
                "h + k = g",
                "f = g + 1/(g + 1)",
            )
        )

    def test_false_five_var_affine_group_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["a", "b", "c", "d", "k"],
                "k = 2*a + 3*b + c - d",
                "2*a + 3*b = c",
                "k = c - d",
            )
        )

    def test_false_five_var_fractional_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["p", "q", "r", "s", "t"],
                "t = p/q + r - s",
                "q = 1/s",
                "t = p/s + r - s",
            )
        )

    def test_false_five_var_exponential_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["m", "n", "u", "v", "w"],
                "w = 2*exp(m - n) + u - v",
                "exp(m - n) = v",
                "w = v + u - v",
            )
        )

    def test_false_five_var_trig_product_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["x", "y", "z", "u", "v"],
                "v = z*sin(x + y) + u",
                "sin(x + y) = u",
                "v = z + u",
            )
        )

    def test_false_five_var_log_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["a", "b", "c", "d", "k"],
                "k = log(a*b) + c - d",
                "log(a*b) = d",
                "k = log(d) + c - d",
            )
        )

    def test_false_five_var_abs_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["x", "y", "z", "p", "q"],
                "q = 3*Abs(x - y) + z - p",
                "x - y = p",
                "q = 3*p + z - p",
            )
        )

    def test_false_five_var_sqrt_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["r", "s", "t", "u", "v"],
                "v = sqrt(r + s) + t - u",
                "r + s = u^2",
                "v = u + t - u",
            )
        )

    def test_false_five_var_polynomial_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["f", "g", "h", "k", "m"],
                "m = f^2 + 2*f*g + h - k",
                "f^2 + 2*f*g = k",
                "m = h - k",
            )
        )

    def test_false_five_var_hyperbolic_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["a", "b", "c", "d", "e"],
                "e = c*cosh(a - b) + d",
                "cosh(a - b) = b",
                "e = c*sinh(b) + d",
            )
        )

    def test_false_five_var_reciprocal_shift_substitution(self):
        self.assertFalse(
            is_substitution_correct(
                ["i", "j", "k", "l", "m"],
                "m = i + 1/(j + k) + l",
                "j + k = i",
                "m = i + 1/(i + 1) + l",
            )
        )


if __name__ == "__main__":
    unittest.main()
