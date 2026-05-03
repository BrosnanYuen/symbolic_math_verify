import unittest

from src.check_calculation import is_calculation_correct


class TestIsCalculationCorrectTrueCases(unittest.TestCase):
    def test_true_example_from_prompt(self):
        self.assertTrue(
            is_calculation_correct(
                ["x", "y", "z"],
                [0.5, -0.2, 14.0],
                "x + y^2 + 1/z",
                0.61142,
                0.001,
            )
        )

    def test_true_linear_combination(self):
        self.assertTrue(
            is_calculation_correct(
                ["a", "b", "c"],
                [1.5, -2.0, 0.25],
                "2*a + 3*b - c",
                -3.249,
                0.001,
            )
        )

    def test_true_trigonometric(self):
        self.assertTrue(
            is_calculation_correct(
                ["x"],
                [0.7],
                "sin(x)^2 + cos(x)^2",
                1.0001,
                0.001,
            )
        )

    def test_true_exponential_log_mix(self):
        self.assertTrue(
            is_calculation_correct(
                ["u", "v"],
                [1.2, 0.8],
                "exp(u) + log(v)",
                3.099,
                0.001,
            )
        )

    def test_true_sqrt_fraction(self):
        self.assertTrue(
            is_calculation_correct(
                ["m", "n"],
                [9.0, 5.0],
                "sqrt(m) + 1/n",
                3.199,
                0.001,
            )
        )

    def test_true_power_expression(self):
        self.assertTrue(
            is_calculation_correct(
                ["p", "q"],
                [2.0, 3.0],
                "p^q + q^p",
                17.001,
                0.001,
            )
        )

    def test_true_nested_parentheses(self):
        self.assertTrue(
            is_calculation_correct(
                ["x", "y", "z"],
                [1.1, 2.2, 3.3],
                "(x + y)/(z - x)",
                1.499,
                0.001,
            )
        )

    def test_true_abs_and_polynomial(self):
        self.assertTrue(
            is_calculation_correct(
                ["x", "y"],
                [-3.5, 1.2],
                "Abs(x) + y^3",
                5.229,
                0.001,
            )
        )

    def test_true_hyperbolic(self):
        self.assertTrue(
            is_calculation_correct(
                ["t"],
                [0.4],
                "cosh(t) - sinh(t)",
                0.6704,
                0.001,
            )
        )

    def test_true_rational_expression(self):
        self.assertTrue(
            is_calculation_correct(
                ["a", "b", "c"],
                [4.0, 1.5, 2.0],
                "a/(b + c)",
                1.142,
                0.001,
            )
        )


class TestIsCalculationCorrectFalseCases(unittest.TestCase):
    def test_false_example_from_prompt(self):
        self.assertFalse(
            is_calculation_correct(
                ["x", "y", "z"],
                [0.5, -0.2, 14.0],
                "x + y^2 + 1/z",
                1.511,
                0.001,
            )
        )

    def test_false_linear_combination(self):
        self.assertFalse(
            is_calculation_correct(
                ["a", "b", "c"],
                [1.5, -2.0, 0.25],
                "2*a + 3*b - c",
                -3.0,
                0.001,
            )
        )

    def test_false_trigonometric(self):
        self.assertFalse(
            is_calculation_correct(
                ["x"],
                [0.7],
                "sin(x)^2 + cos(x)^2",
                1.05,
                0.001,
            )
        )

    def test_false_exponential_log_mix(self):
        self.assertFalse(
            is_calculation_correct(
                ["u", "v"],
                [1.2, 0.8],
                "exp(u) + log(v)",
                3.5,
                0.001,
            )
        )

    def test_false_sqrt_fraction(self):
        self.assertFalse(
            is_calculation_correct(
                ["m", "n"],
                [9.0, 5.0],
                "sqrt(m) + 1/n",
                3.0,
                0.001,
            )
        )

    def test_false_power_expression(self):
        self.assertFalse(
            is_calculation_correct(
                ["p", "q"],
                [2.0, 3.0],
                "p^q + q^p",
                18.5,
                0.001,
            )
        )

    def test_false_nested_parentheses(self):
        self.assertFalse(
            is_calculation_correct(
                ["x", "y", "z"],
                [1.1, 2.2, 3.3],
                "(x + y)/(z - x)",
                1.2,
                0.001,
            )
        )

    def test_false_abs_and_polynomial(self):
        self.assertFalse(
            is_calculation_correct(
                ["x", "y"],
                [-3.5, 1.2],
                "Abs(x) + y^3",
                4.9,
                0.001,
            )
        )

    def test_false_hyperbolic(self):
        self.assertFalse(
            is_calculation_correct(
                ["t"],
                [0.4],
                "cosh(t) - sinh(t)",
                0.75,
                0.001,
            )
        )

    def test_false_tolerance_too_strict(self):
        self.assertFalse(
            is_calculation_correct(
                ["x", "y", "z"],
                [0.5, -0.2, 14.0],
                "x + y^2 + 1/z",
                0.61142,
                0.000000001,
            )
        )


if __name__ == "__main__":
    unittest.main()
