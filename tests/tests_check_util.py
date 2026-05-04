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

    def test_four_var_linear_rearrangement(self):
        self.assertTrue(
            is_equation_equal(
                ["a", "b", "c", "d"],
                "a + 2*b - 3*c + d = 11",
                "d = 11 - a - 2*b + 3*c",
            )
        )

    def test_four_var_scaled_plane_relation(self):
        self.assertTrue(
            is_equation_equal(
                ["w", "x", "y", "z"],
                "4*w - 8*x + 12*y - 16*z = 20",
                "w - 2*x + 3*y - 4*z = 5",
            )
        )

    def test_four_var_fraction_cross_multiply(self):
        self.assertTrue(
            is_equation_equal(
                ["p", "q", "r", "s"],
                "(p + q)/r = s",
                "p + q = r*s",
            )
        )

    def test_four_var_log_exp_rearrangement(self):
        self.assertTrue(
            is_equation_equal(
                ["A", "B", "C", "D"],
                "A = B + C*log(D)",
                "D = exp((A - B)/C)",
            )
        )

    def test_four_var_trig_sum_rearrangement(self):
        self.assertTrue(
            is_equation_equal(
                ["x", "y", "u", "v"],
                "sin(x) + cos(y) = u - v",
                "u = sin(x) + cos(y) + v",
            )
        )

    def test_four_var_difference_of_squares(self):
        self.assertTrue(
            is_equation_equal(
                ["m", "n", "p", "q"],
                "m^2 - n^2 = p - q",
                "(m - n)*(m + n) - p + q = 0",
            )
        )

    def test_four_var_nested_parentheses_rearrangement(self):
        self.assertTrue(
            is_equation_equal(
                ["i", "j", "k", "l"],
                "2*(i - j) + 3*(k + l) = 7",
                "l = (7 - 2*(i - j) - 3*k)/3",
            )
        )

    def test_four_var_exponential_shift_rearrangement(self):
        self.assertTrue(
            is_equation_equal(
                ["P", "Q", "R", "S"],
                "P = Q*exp(R) + S",
                "R = log((P - S)/Q)",
            )
        )

    def test_four_var_reciprocal_relation(self):
        self.assertTrue(
            is_equation_equal(
                ["a", "b", "c", "d"],
                "1/(a + b) = c/d",
                "d = c*(a + b)",
            )
        )

    def test_four_var_polynomial_grouping_equivalence(self):
        self.assertTrue(
            is_equation_equal(
                ["x", "y", "z", "t"],
                "x*y + z = t + 1",
                "z = t + 1 - x*y",
            )
        )

    def test_six_var_linear_balance_rearrangement(self):
        self.assertTrue(
            is_equation_equal(
                ["a", "b", "c", "d", "e", "f"],
                "a + 2*b - c + d - e + f = 0",
                "a = -2*b + c - d + e - f",
            )
        )

    def test_six_var_scaled_linear_relation(self):
        self.assertTrue(
            is_equation_equal(
                ["p", "q", "r", "s", "t", "u"],
                "3*p - 6*q + 9*r - 12*s + 15*t - 18*u = 0",
                "p - 2*q + 3*r - 4*s + 5*t - 6*u = 0",
            )
        )

    def test_six_var_fraction_cross_multiply_sum(self):
        self.assertTrue(
            is_equation_equal(
                ["x", "y", "z", "u", "v", "w"],
                "(x + y + z)/u = v + w",
                "x + y + z = u*(v + w)",
            )
        )

    def test_six_var_bilinear_to_zero_form(self):
        self.assertTrue(
            is_equation_equal(
                ["A", "B", "C", "D", "E", "F"],
                "A*B + C*D = E - F",
                "A*B + C*D - E + F = 0",
            )
        )

    def test_six_var_ratio_of_sums_cross_multiply(self):
        self.assertTrue(
            is_equation_equal(
                ["m", "n", "p", "q", "r", "s"],
                "m/n = (p + q)/(r + s)",
                "m*(r + s) = n*(p + q)",
            )
        )

    def test_six_var_affine_rearrangement(self):
        self.assertTrue(
            is_equation_equal(
                ["h", "i", "j", "k", "l", "m"],
                "2*h + 3*i - 4*j + 5*k - 6*l + 7*m = 8",
                "7*m = 8 - 2*h - 3*i + 4*j - 5*k + 6*l",
            )
        )

    def test_six_var_product_balance_zero_form(self):
        self.assertTrue(
            is_equation_equal(
                ["u1", "u2", "u3", "u4", "u5", "u6"],
                "u1*u2*u3 = u4*u5*u6",
                "u1*u2*u3 - u4*u5*u6 = 0",
            )
        )

    def test_six_var_unicode_multiplication_rearrangement(self):
        self.assertTrue(
            is_equation_equal(
                ["F", "m", "a", "b", "c", "d"],
                "F = m×a + b - c + d",
                "F - m*a - b + c - d = 0",
            )
        )

    def test_six_var_difference_sum_zero_form(self):
        self.assertTrue(
            is_equation_equal(
                ["x1", "x2", "x3", "x4", "x5", "x6"],
                "(x1 - x2) + (x3 - x4) = x5 - x6",
                "x1 - x2 + x3 - x4 - x5 + x6 = 0",
            )
        )

    def test_six_var_total_sum_rearrangement(self):
        self.assertTrue(
            is_equation_equal(
                ["g", "h", "i", "j", "k", "l"],
                "g + h + i + j + k + l = 0",
                "l = -g - h - i - j - k",
            )
        )

    def test_derivative_polynomial_basic_true(self):
        self.assertTrue(
            is_equation_equal(
                ["x"],
                "Derivative(x^2 + 6, x) = 2*x",
                "Derivative(x^2 + 6, x) - 2*x = 0",
            )
        )

    def test_derivative_trig_true(self):
        self.assertTrue(
            is_equation_equal(
                ["x"],
                "Derivative(sin(x), x) = cos(x)",
                "Derivative(sin(x), x) - cos(x) = 0",
            )
        )

    def test_derivative_exponential_true(self):
        self.assertTrue(
            is_equation_equal(
                ["x"],
                "Derivative(exp(3*x), x) = 3*exp(3*x)",
                "Derivative(exp(3*x), x)/(3*exp(3*x)) = 1",
            )
        )

    def test_integral_definite_quadratic_true(self):
        self.assertTrue(
            is_equation_equal(
                ["x"],
                "Integral(2*x, (x, 0, 3)) = 9",
                "Integral(2*x, (x, 0, 3)) - 9 = 0",
            )
        )

    def test_integral_definite_trig_true(self):
        self.assertTrue(
            is_equation_equal(
                ["x"],
                "Integral(cos(x), (x, 0, pi/2)) = 1",
                "Integral(cos(x), (x, 0, pi/2)) - 1 = 0",
            )
        )

    def test_derivative_log_true(self):
        self.assertTrue(
            is_equation_equal(
                ["x"],
                "Derivative(log(x), x) = 1/x",
                "x*Derivative(log(x), x) = 1",
            )
        )

    def test_derivative_cubic_linear_combo_true(self):
        self.assertTrue(
            is_equation_equal(
                ["x"],
                "Derivative(x^3 - 4*x, x) = 3*x^2 - 4",
                "Derivative(x^3 - 4*x, x) - 3*x^2 + 4 = 0",
            )
        )

    def test_integral_definite_exponential_true(self):
        self.assertTrue(
            is_equation_equal(
                ["x"],
                "Integral(exp(x), (x, 0, 1)) = E - 1",
                "Integral(exp(x), (x, 0, 1)) + 1 = E",
            )
        )

    def test_derivative_sqrt_true(self):
        self.assertTrue(
            is_equation_equal(
                ["x"],
                "Derivative(sqrt(x), x) = 1/(2*sqrt(x))",
                "2*sqrt(x)*Derivative(sqrt(x), x) = 1",
            )
        )

    def test_integral_derivative_identity_true(self):
        self.assertTrue(
            is_equation_equal(
                ["x"],
                "Derivative(Integral(x^2, x), x) = x^2",
                "Derivative(Integral(x^2, x), x) - x^2 = 0",
            )
        )

    def test_three_var_derivative_linear_combo_true(self):
        self.assertTrue(
            is_equation_equal(
                ["x", "y", "z"],
                "Derivative(x*y + z, x) = y",
                "Derivative(x*y + z, x) - y = 0",
            )
        )

    def test_three_var_derivative_trig_plus_constant_true(self):
        self.assertTrue(
            is_equation_equal(
                ["x", "y", "z"],
                "Derivative(sin(x) + y + z, x) = cos(x)",
                "Derivative(sin(x) + y + z, x) - cos(x) = 0",
            )
        )

    def test_three_var_definite_integral_scaled_true(self):
        self.assertTrue(
            is_equation_equal(
                ["x", "y", "z"],
                "Integral(y*x, (x, 0, z)) = y*z^2/2",
                "2*Integral(y*x, (x, 0, z)) = y*z^2",
            )
        )

    def test_three_var_definite_integral_polynomial_true(self):
        self.assertTrue(
            is_equation_equal(
                ["x", "a", "b"],
                "Integral(a*x + b, (x, 0, 2)) = 2*a + 2*b",
                "Integral(a*x + b, (x, 0, 2)) - 2*a - 2*b = 0",
            )
        )

    def test_three_var_derivative_exp_linear_true(self):
        self.assertTrue(
            is_equation_equal(
                ["x", "y", "z"],
                "Derivative(exp(y*x + z), x) = y*exp(y*x + z)",
                "Derivative(exp(y*x + z), x)/(exp(y*x + z)) = y",
            )
        )

    def test_three_var_derivative_log_affine_true(self):
        self.assertTrue(
            is_equation_equal(
                ["x", "a", "b"],
                "Derivative(log(a*x + b), x) = a/(a*x + b)",
                "(a*x + b)*Derivative(log(a*x + b), x) = a",
            )
        )

    def test_three_var_integral_derivative_identity_true(self):
        self.assertTrue(
            is_equation_equal(
                ["x", "a", "b"],
                "Derivative(Integral(a*x + b, x), x) = a*x + b",
                "Derivative(Integral(a*x + b, x), x) - a*x - b = 0",
            )
        )

    def test_three_var_second_derivative_quadratic_true(self):
        self.assertTrue(
            is_equation_equal(
                ["x", "a", "b"],
                "Derivative(a*x^2 + b*x, (x, 2)) = 2*a",
                "Derivative(a*x^2 + b*x, (x, 2)) - 2*a = 0",
            )
        )

    def test_three_var_definite_integral_trig_shift_true(self):
        self.assertTrue(
            is_equation_equal(
                ["x", "y", "z"],
                "Integral(y*cos(x + z), (x, 0, pi/2)) = y*(cos(z) - sin(z))",
                "Integral(y*cos(x + z), (x, 0, pi/2)) - y*(cos(z) - sin(z)) = 0",
            )
        )

    def test_three_var_derivative_with_additive_constants_true(self):
        self.assertTrue(
            is_equation_equal(
                ["x", "m", "n"],
                "Derivative((x + m)*(x + n), x) = 2*x + m + n",
                "Derivative((x + m)*(x + n), x) - 2*x - m - n = 0",
            )
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

    def test_four_var_linear_wrong_constant(self):
        self.assertFalse(
            is_equation_equal(
                ["a", "b", "c", "d"],
                "a + 2*b - 3*c + d = 11",
                "d = 10 - a - 2*b + 3*c",
            )
        )

    def test_four_var_scaled_relation_wrong_scale(self):
        self.assertFalse(
            is_equation_equal(
                ["w", "x", "y", "z"],
                "4*w - 8*x + 12*y - 16*z = 20",
                "w - 2*x + 3*y - 4*z = 6",
            )
        )

    def test_four_var_fraction_wrong_rearrangement(self):
        self.assertFalse(
            is_equation_equal(
                ["p", "q", "r", "s"],
                "(p + q)/r = s",
                "p + q = r + s",
            )
        )

    def test_four_var_log_exp_wrong_offset(self):
        self.assertFalse(
            is_equation_equal(
                ["A", "B", "C", "D"],
                "A = B + C*log(D)",
                "D = exp((A - B + 1)/C)",
            )
        )

    def test_four_var_trig_sum_wrong_sign(self):
        self.assertFalse(
            is_equation_equal(
                ["x", "y", "u", "v"],
                "sin(x) + cos(y) = u - v",
                "u = sin(x) - cos(y) + v",
            )
        )

    def test_four_var_difference_of_squares_vs_sum(self):
        self.assertFalse(
            is_equation_equal(
                ["m", "n", "p", "q"],
                "m^2 - n^2 = p - q",
                "(m + n)^2 - p + q = 0",
            )
        )

    def test_four_var_parentheses_wrong_coefficient(self):
        self.assertFalse(
            is_equation_equal(
                ["i", "j", "k", "l"],
                "2*(i - j) + 3*(k + l) = 7",
                "l = (7 - 2*(i - j) - 2*k)/3",
            )
        )

    def test_four_var_exponential_wrong_additive_term(self):
        self.assertFalse(
            is_equation_equal(
                ["P", "Q", "R", "S"],
                "P = Q*exp(R) + S",
                "R = log((P + S)/Q)",
            )
        )

    def test_four_var_reciprocal_wrong_side(self):
        self.assertFalse(
            is_equation_equal(
                ["a", "b", "c", "d"],
                "1/(a + b) = c/d",
                "d = c/(a + b)",
            )
        )

    def test_four_var_polynomial_grouping_not_equivalent(self):
        self.assertFalse(
            is_equation_equal(
                ["x", "y", "z", "t"],
                "x*y + x*z = x*(t + 1)",
                "y + z = x + t + 1",
            )
        )

    def test_six_var_linear_wrong_constant(self):
        self.assertFalse(
            is_equation_equal(
                ["a", "b", "c", "d", "e", "f"],
                "a + b + c + d + e + f = 10",
                "a + b + c + d + e + f = 11",
            )
        )

    def test_six_var_linear_wrong_coefficient(self):
        self.assertFalse(
            is_equation_equal(
                ["p", "q", "r", "s", "t", "u"],
                "2*p - q + r - s + t - u = 0",
                "p - q + r - s + t - u = 0",
            )
        )

    def test_six_var_fraction_wrong_cross_multiply(self):
        self.assertFalse(
            is_equation_equal(
                ["x", "y", "z", "u", "v", "w"],
                "(x + y + z)/u = v + w",
                "x + y + z = u*v + w",
            )
        )

    def test_six_var_bilinear_wrong_sign(self):
        self.assertFalse(
            is_equation_equal(
                ["A", "B", "C", "D", "E", "F"],
                "A*B + C*D = E - F",
                "A*B + C*D = E + F",
            )
        )

    def test_six_var_product_missing_factor(self):
        self.assertFalse(
            is_equation_equal(
                ["m", "n", "p", "q", "r", "s"],
                "m*n*p = q*r*s",
                "m*n = q*r*s",
            )
        )

    def test_six_var_affine_wrong_constant(self):
        self.assertFalse(
            is_equation_equal(
                ["h", "i", "j", "k", "l", "m"],
                "2*h + 3*i - 4*j + 5*k - 6*l + 7*m = 8",
                "2*h + 3*i - 4*j + 5*k - 6*l + 7*m = 9",
            )
        )

    def test_six_var_sum_of_fractions_wrong_product(self):
        self.assertFalse(
            is_equation_equal(
                ["u1", "u2", "u3", "u4", "u5", "u6"],
                "u1/u2 + u3/u4 = u5/u6",
                "u1*u4 + u2*u3 = u5*u6",
            )
        )

    def test_six_var_alternating_sum_wrong_last_sign(self):
        self.assertFalse(
            is_equation_equal(
                ["r1", "r2", "r3", "r4", "r5", "r6"],
                "r1 - r2 + r3 - r4 + r5 - r6 = 0",
                "r1 - r2 + r3 - r4 + r5 + r6 = 0",
            )
        )

    def test_six_var_force_equation_wrong_d_term(self):
        self.assertFalse(
            is_equation_equal(
                ["F", "m", "a", "b", "c", "d"],
                "F = m*a + b - c + d",
                "F = m*a + b - c - d",
            )
        )

    def test_six_var_product_vs_sum_not_equivalent(self):
        self.assertFalse(
            is_equation_equal(
                ["x1", "x2", "x3", "x4", "x5", "x6"],
                "x1*x2 + x3*x4 = x5*x6",
                "x1 + x2 + x3 + x4 = x5*x6",
            )
        )

    def test_derivative_polynomial_basic_false(self):
        self.assertFalse(
            is_equation_equal(
                ["x"],
                "Derivative(x^2 + 6, x) = 2*x",
                "Derivative(x^2 + 6, x) = 2*x + 1",
            )
        )

    def test_derivative_trig_false(self):
        self.assertFalse(
            is_equation_equal(
                ["x"],
                "Derivative(sin(x), x) = cos(x)",
                "Derivative(sin(x), x) = sin(x)",
            )
        )

    def test_integral_definite_quadratic_false(self):
        self.assertFalse(
            is_equation_equal(
                ["x"],
                "Integral(2*x, (x, 0, 3)) = 9",
                "Integral(2*x, (x, 0, 3)) = 8",
            )
        )

    def test_integral_definite_trig_false(self):
        self.assertFalse(
            is_equation_equal(
                ["x"],
                "Integral(cos(x), (x, 0, pi/2)) = 1",
                "Integral(cos(x), (x, 0, pi/2)) = 0",
            )
        )

    def test_derivative_log_false(self):
        self.assertFalse(
            is_equation_equal(
                ["x"],
                "Derivative(log(x), x) = 1/x",
                "Derivative(log(x), x) = x",
            )
        )

    def test_derivative_cubic_linear_combo_false(self):
        self.assertFalse(
            is_equation_equal(
                ["x"],
                "Derivative(x^3 - 4*x, x) = 3*x^2 - 4",
                "Derivative(x^3 - 4*x, x) = 3*x - 4",
            )
        )

    def test_integral_definite_exponential_false(self):
        self.assertFalse(
            is_equation_equal(
                ["x"],
                "Integral(exp(x), (x, 0, 1)) = E - 1",
                "Integral(exp(x), (x, 0, 1)) = E",
            )
        )

    def test_derivative_sqrt_false(self):
        self.assertFalse(
            is_equation_equal(
                ["x"],
                "Derivative(sqrt(x), x) = 1/(2*sqrt(x))",
                "Derivative(sqrt(x), x) = 1/sqrt(x)",
            )
        )

    def test_integral_log_definite_false(self):
        self.assertFalse(
            is_equation_equal(
                ["x"],
                "Integral(1/x, (x, 1, E)) = 1",
                "Integral(1/x, (x, 1, E)) = 2",
            )
        )

    def test_derivative_trig_product_false(self):
        self.assertFalse(
            is_equation_equal(
                ["x"],
                "Derivative(sin(x)^2, x) = 2*sin(x)*cos(x)",
                "Derivative(sin(x)^2, x) = 2*sin(x)",
            )
        )

    def test_three_var_derivative_linear_combo_false(self):
        self.assertFalse(
            is_equation_equal(
                ["x", "y", "z"],
                "Derivative(x*y + z, x) = y",
                "Derivative(x*y + z, x) = x",
            )
        )

    def test_three_var_derivative_trig_plus_constant_false(self):
        self.assertFalse(
            is_equation_equal(
                ["x", "y", "z"],
                "Derivative(sin(x) + y + z, x) = cos(x)",
                "Derivative(sin(x) + y + z, x) = sin(x)",
            )
        )

    def test_three_var_definite_integral_scaled_false(self):
        self.assertFalse(
            is_equation_equal(
                ["x", "y", "z"],
                "Integral(y*x, (x, 0, z)) = y*z^2/2",
                "2*Integral(y*x, (x, 0, z)) = y*z",
            )
        )

    def test_three_var_definite_integral_polynomial_false(self):
        self.assertFalse(
            is_equation_equal(
                ["x", "a", "b"],
                "Integral(a*x + b, (x, 0, 2)) = 2*a + 2*b",
                "Integral(a*x + b, (x, 0, 2)) = 2*a + b",
            )
        )

    def test_three_var_derivative_exp_linear_false(self):
        self.assertFalse(
            is_equation_equal(
                ["x", "y", "z"],
                "Derivative(exp(y*x + z), x) = y*exp(y*x + z)",
                "Derivative(exp(y*x + z), x) = exp(y*x + z)",
            )
        )

    def test_three_var_derivative_log_affine_false(self):
        self.assertFalse(
            is_equation_equal(
                ["x", "a", "b"],
                "Derivative(log(a*x + b), x) = a/(a*x + b)",
                "(a*x + b)*Derivative(log(a*x + b), x) = b",
            )
        )

    def test_three_var_integral_derivative_identity_false(self):
        self.assertFalse(
            is_equation_equal(
                ["x", "a", "b"],
                "Derivative(Integral(a*x + b, x), x) = a*x + b",
                "Derivative(Integral(a*x + b, x), x) = a*x - b",
            )
        )

    def test_three_var_second_derivative_quadratic_false(self):
        self.assertFalse(
            is_equation_equal(
                ["x", "a", "b"],
                "Derivative(a*x^2 + b*x, (x, 2)) = 2*a",
                "Derivative(a*x^2 + b*x, (x, 2)) = a",
            )
        )

    def test_three_var_definite_integral_trig_shift_false(self):
        self.assertFalse(
            is_equation_equal(
                ["x", "y", "z"],
                "Integral(y*cos(x + z), (x, 0, pi/2)) = y*(cos(z) - sin(z))",
                "Integral(y*cos(x + z), (x, 0, pi/2)) = y*(cos(z) + sin(z))",
            )
        )

    def test_three_var_derivative_with_additive_constants_false(self):
        self.assertFalse(
            is_equation_equal(
                ["x", "m", "n"],
                "Derivative((x + m)*(x + n), x) = 2*x + m + n",
                "Derivative((x + m)*(x + n), x) = 2*x + m - n",
            )
        )


if __name__ == "__main__":
    unittest.main()
