import unittest

from symbolic_math_verify.extract_variables import extract_variables


class TestExtractVariables(unittest.TestCase):
    def test_extracts_symbols_while_skipping_function_names_and_constants(self):
        self.assertCountEqual(
            extract_variables("sin(x) = c*exp(y) + g_i + 4"),
            ["x", "c", "y", "g_i"],
        )

    def test_skips_e_constant_in_exponential_expression(self):
        self.assertCountEqual(
            extract_variables("e^(w) + h_delta2 - 5"),
            ["w", "h_delta2"],
        )

    def test_extracts_nested_function_arguments(self):
        self.assertCountEqual(
            extract_variables("cos(sin(x+ 5*log(z)))"),
            ["x", "z"],
        )

    def test_extracts_uppercase_symbol_while_skipping_tan_and_ln(self):
        self.assertCountEqual(
            extract_variables("tan(x) = c*ln(y) + E + 4"),
            ["x", "c", "y", "E"],
        )

    def test_extracts_uppercase_i_symbol_while_skipping_e_constant(self):
        self.assertCountEqual(
            extract_variables("e^(n) + h_laser5 - I"),
            ["n", "h_laser5", "I"],
        )

    def test_extracts_variables_from_arrow_equation(self):
        self.assertCountEqual(
            extract_variables(" q_1 = abs(h)/w -> w * q_1 = abs(h) "),
            ["q_1", "h", "w"],
        )

    def test_extracts_variables_from_substitution_step(self):
        self.assertCountEqual(
            extract_variables(" P = I*V ; V = I*R -> P = R*I^2 "),
            ["P", "V", "I", "R"],
        )

    def test_extracts_variables_from_subscript_step(self):
        self.assertCountEqual(
            extract_variables(" U = m*g*h : _i -> U_i = m_i*g_i*h_i "),
            ["U", "m", "g", "h", "U_i", "m_i", "g_i", "h_i"],
        )

    def test_extracts_variables_from_alphanumeric_subscript_step(self):
        self.assertCountEqual(
            extract_variables(" U = m*g*h : _alpha -> U_alpha = m_alpha*g_alpha*h_alpha "),
            ["U", "m", "g", "h", "U_alpha", "m_alpha", "g_alpha", "h_alpha"],
        )


if __name__ == "__main__":
    unittest.main()
