import unittest

from src.check_util import is_equation_equal


class TestIsEquationEqualTrueCases(unittest.TestCase):
    def test_rc_charging_equation_rearrangement(self):
        self.assertTrue(
            is_equation_equal(
                ["Vc", "Vsource", "t", "R", "C"],
                "Vc=Vsource*(1−e^(−t/(R*C)))",
                "t/R = -C*ln(1- (Vc/Vsource))",
            )
        )

    def test_simple_linear_shift(self):
        self.assertTrue(is_equation_equal(["x"], "x + 2 = 5", "x = 3"))

    def test_scaled_linear_equation(self):
        self.assertTrue(is_equation_equal(["x"], "2*x + 4 = 10", "x = 3"))

    def test_quadratic_factored_form(self):
        self.assertTrue(is_equation_equal(["x"], "x^2 - 1 = 0", "(x - 1)*(x + 1) = 0"))

    def test_two_variable_rearrangement(self):
        self.assertTrue(is_equation_equal(["x", "y"], "x + y = 10", "y = 10 - x"))

    def test_trigonometric_identity(self):
        self.assertTrue(is_equation_equal(["x"], "sin(x)^2 + cos(x)^2 = 1", "0 = 0"))

    def test_rational_zero_numerator(self):
        self.assertTrue(is_equation_equal(["x"], "(x^2 - 1)/(x - 1) = 0", "x + 1 = 0"))

    def test_exponential_log_rearrangement(self):
        self.assertTrue(is_equation_equal(["x", "y"], "y = exp(x)", "x = log(y)"))

    def test_circle_equation_rearrangement(self):
        self.assertTrue(is_equation_equal(["x", "y", "r"], "x^2 + y^2 = r^2", "y^2 = r^2 - x^2"))

    def test_implicit_multiplication_rearrangement(self):
        self.assertTrue(is_equation_equal(["x", "y"], "2x + 3y = 12", "x = 6 - 3*y/2"))

    def test_three_var_linear_rearrangement(self):
        self.assertTrue(
            is_equation_equal(["x", "y", "z"], "x + 2*y - z = 7", "z = x + 2*y - 7")
        )

    def test_three_var_scaled_equation(self):
        self.assertTrue(
            is_equation_equal(["a", "b", "c"], "3*a - 6*b + 9*c = 12", "a - 2*b + 3*c = 4")
        )

    def test_three_var_plane_rearrangement(self):
        self.assertTrue(
            is_equation_equal(["x", "y", "z"], "2*x + y + z = 0", "y = -2*x - z")
        )

    def test_three_var_monomial_relation(self):
        self.assertTrue(
            is_equation_equal(["p", "q", "r"], "p*q = r", "p*q - r = 0")
        )

    def test_three_var_fraction_cross_multiply(self):
        self.assertTrue(
            is_equation_equal(["u", "v", "w"], "u/v = w", "u = v*w")
        )

    def test_three_var_log_exp_relation(self):
        self.assertTrue(
            is_equation_equal(["m", "n", "k"], "m = n + log(k)", "k = exp(m - n)")
        )

    def test_three_var_sphere_like_rearrangement(self):
        self.assertTrue(
            is_equation_equal(
                ["x", "y", "z", "R"],
                "x^2 + y^2 + z^2 = R^2",
                "z^2 = R^2 - x^2 - y^2",
            )
        )

    def test_three_var_identity_shifted_zero(self):
        self.assertTrue(
            is_equation_equal(["x", "y", "z"], "x + y = z", "x + y - z = 0")
        )

    def test_three_var_product_equals_zero_factored(self):
        self.assertTrue(
            is_equation_equal(["a", "b", "c"], "(a - b)*(c + 1) = 0", "(c + 1)*(a - b) = 0")
        )

    def test_three_var_unicode_multiplication_rearrangement(self):
        self.assertTrue(
            is_equation_equal(["F", "m", "a"], "F = m×a", "F - m*a = 0")
        )


class TestIsEquationEqualFalseCases(unittest.TestCase):
    def test_linear_wrong_solution(self):
        self.assertFalse(is_equation_equal(["x"], "x + 2 = 5", "x = 4"))

    def test_quadratic_not_same_as_one_root(self):
        self.assertFalse(is_equation_equal(["x"], "x^2 = 4", "x = 2"))

    def test_two_variable_wrong_constant(self):
        self.assertFalse(is_equation_equal(["x", "y"], "x + y = 10", "y = 9 - x"))

    def test_identity_not_same_as_constraint(self):
        self.assertFalse(is_equation_equal(["x"], "sin(x)^2 + cos(x)^2 = 1", "x = 0"))

    def test_exponential_not_same_as_linear(self):
        self.assertFalse(is_equation_equal(["x", "y"], "y = exp(x)", "x = y"))

    def test_symbol_dependent_multiplier_not_equivalent(self):
        self.assertFalse(is_equation_equal(["x", "y"], "x*y = 0", "x = 0"))

    def test_circle_wrong_radius_power(self):
        self.assertFalse(is_equation_equal(["x", "y", "r"], "x^2 + y^2 = r^2", "x^2 + y^2 = r"))

    def test_reciprocal_has_no_zero_solution(self):
        self.assertFalse(is_equation_equal(["x"], "1/(x - 1) = 0", "x = 1"))

    def test_rational_wrong_rearrangement(self):
        self.assertFalse(is_equation_equal(["a", "b", "c"], "a/b = c", "a = b + c"))

    def test_cubic_not_same_as_one_root(self):
        self.assertFalse(is_equation_equal(["x"], "x^3 = 8", "x = 2"))

    def test_three_var_linear_wrong_offset(self):
        self.assertFalse(
            is_equation_equal(["x", "y", "z"], "x + 2*y + 3*z = 6", "x + 2*y + 3*z = 7")
        )

    def test_three_var_wrong_sign_rearrangement(self):
        self.assertFalse(
            is_equation_equal(["a", "b", "c"], "a - b = c", "a + b = c")
        )

    def test_three_var_product_vs_single_factor(self):
        self.assertFalse(
            is_equation_equal(["p", "q", "r"], "p*q*r = 0", "p = 0")
        )

    def test_three_var_fraction_wrong_cross_multiply(self):
        self.assertFalse(
            is_equation_equal(["u", "v", "w"], "u/v = w", "u = v + w")
        )

    def test_three_var_log_relation_wrong_base_form(self):
        self.assertFalse(
            is_equation_equal(["m", "n", "k"], "m = n + log(k)", "k = m - n")
        )

    def test_three_var_norm_wrong_expression(self):
        self.assertFalse(
            is_equation_equal(["x", "y", "z"], "x^2 + y^2 + z^2 = 1", "x + y + z = 1")
        )

    def test_three_var_trig_identity_wrong_constraint(self):
        self.assertFalse(
            is_equation_equal(["x", "y", "z"], "sin(x)^2 + cos(x)^2 + y = z", "y = z + 1")
        )

    def test_three_var_exponential_wrong_rearrangement(self):
        self.assertFalse(
            is_equation_equal(["A", "B", "C"], "A = B*exp(C)", "C = log(A) - B")
        )

    def test_three_var_unicode_operator_wrong_relation(self):
        self.assertFalse(
            is_equation_equal(["F", "m", "a"], "F = m×a", "F = m+a")
        )

    def test_three_var_quadratic_surface_vs_plane(self):
        self.assertFalse(
            is_equation_equal(["x", "y", "z"], "z = x^2 + y^2", "z = x + y")
        )


if __name__ == "__main__":
    unittest.main()
