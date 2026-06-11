import unittest

from src.check_subscript_substitution import is_subscript_substitution_correct


class TestIsSubscriptSubstitutionCorrectTrueCases(unittest.TestCase):
    def test_prompt_valid_energy_basic_subscript(self):
        self.assertTrue(
            is_subscript_substitution_correct(
                ["E", "m", "v"],
                "E = (1/2)*m*(v^2)",
                "_i",
                "E_i = (1/2)*(m_i)*((v_i)^2)",
            )
        )

    def test_prompt_valid_energy_reordered_form_one(self):
        self.assertTrue(
            is_subscript_substitution_correct(
                ["E", "m", "v"],
                "E = (1/2)*m*(v^2)",
                "_i",
                "E_i = (1/2)*((v_i)^2)*(m_i)",
            )
        )

    def test_prompt_valid_energy_reordered_form_two(self):
        self.assertTrue(
            is_subscript_substitution_correct(
                ["E", "m", "v"],
                "E = (1/2)*m*(v^2)",
                "_i",
                "E_i = (m_i)*((v_i)^2)*(1/2)",
            )
        )

    def test_prompt_valid_energy_reordered_form_three(self):
        self.assertTrue(
            is_subscript_substitution_correct(
                ["E", "m", "v"],
                "E = (1/2)*m*(v^2)",
                "_i",
                "E_i = ((v_i)^2)*(1/2)*(m_i)",
            )
        )

    def test_prompt_valid_energy_divided_form(self):
        self.assertTrue(
            is_subscript_substitution_correct(
                ["E", "m", "v"],
                "E = (1/2)*m*(v^2)",
                "_i",
                "(E_i)/(m_i) = (1/2)*((v_i)^2)",
            )
        )

    def test_prompt_valid_potential_energy_basic_subscript(self):
        self.assertTrue(
            is_subscript_substitution_correct(
                ["U", "m", "g", "h"],
                "U = m*g*h",
                "_k",
                "U_k = m_k*g_k*h_k",
            )
        )

    def test_prompt_valid_potential_energy_scaled_both_sides(self):
        self.assertTrue(
            is_subscript_substitution_correct(
                ["U", "m", "g", "h"],
                "U = m*g*h",
                "_k",
                "2*U_k = 2*m_k*g_k*h_k",
            )
        )

    def test_prompt_valid_numeric_subscript_suffix(self):
        self.assertTrue(
            is_subscript_substitution_correct(
                ["E", "m", "v"],
                "E = (1/2)*m*(v^2)",
                "_1",
                "E_1 = (1/2)*(m_1)*((v_1)^2)",
            )
        )

    def test_prompt_valid_alphanumeric_subscript_suffix(self):
        self.assertTrue(
            is_subscript_substitution_correct(
                ["U", "m", "g", "h"],
                "U = m*g*h",
                "_f2",
                "U_f2 = m_f2*g_f2*h_f2",
            )
        )

    def test_force_relation_basic_subscript(self):
        self.assertTrue(
            is_subscript_substitution_correct(
                ["F", "m", "a"],
                "F = m*a",
                "_n",
                "F_n = m_n*a_n",
            )
        )

    def test_power_relation_rearranged_after_subscript(self):
        self.assertTrue(
            is_subscript_substitution_correct(
                ["P", "I", "V"],
                "P = I*V",
                "_t2",
                "P_t2/V_t2 = I_t2",
            )
        )

    def test_area_relation_scaled_both_sides(self):
        self.assertTrue(
            is_subscript_substitution_correct(
                ["A", "l", "w"],
                "A = l*w",
                "_3",
                "2*A_3 = 2*l_3*w_3",
            )
        )

    def test_additive_relation_rearranged_after_subscript(self):
        self.assertTrue(
            is_subscript_substitution_correct(
                ["p", "q", "r"],
                "p = q + r",
                "_x",
                "p_x - r_x = q_x",
            )
        )

    def test_kinetic_energy_reordered_after_subscript(self):
        self.assertTrue(
            is_subscript_substitution_correct(
                ["K", "m", "v"],
                "K = (1/2)*m*(v^2)",
                "_b",
                "K_b = (v_b^2)*(m_b)*(1/2)",
            )
        )

    def test_heat_relation_divided_by_one_subscripted_factor(self):
        self.assertTrue(
            is_subscript_substitution_correct(
                ["Q", "m", "c", "T"],
                "Q = m*c*T",
                "_ref",
                "Q_ref/(c_ref) = m_ref*T_ref",
            )
        )

    def test_linear_relation_shifted_after_subscript(self):
        self.assertTrue(
            is_subscript_substitution_correct(
                ["y", "x", "b"],
                "y = x + b",
                "_1",
                "y_1 - x_1 = b_1",
            )
        )

    def test_resistance_relation_cross_multiplied_after_subscript(self):
        self.assertTrue(
            is_subscript_substitution_correct(
                ["R", "V", "I"],
                "R = V/I",
                "_k9",
                "R_k9*I_k9 = V_k9",
            )
        )

    def test_motion_relation_scaled_after_subscript(self):
        self.assertTrue(
            is_subscript_substitution_correct(
                ["s", "u", "t", "a"],
                "s = u*t + (1/2)*a*(t^2)",
                "_f",
                "2*s_f = 2*u_f*t_f + a_f*(t_f^2)",
            )
        )

    def test_repeated_symbol_occurrences_all_get_subscripted(self):
        self.assertTrue(
            is_subscript_substitution_correct(
                ["M", "x"],
                "M = x + x^2",
                "_r",
                "M_r = x_r + x_r^2",
            )
        )

    def test_repeated_symbol_occurrences_all_get_subscripted2(self):
        self.assertTrue(
            is_subscript_substitution_correct(
                ["M", "x"],
                "M = x + x^2",
                "_delta",
                "M_delta = x_delta + x_delta^2",
            )
        )

    def test_linear_relation_shifted_after_subscript2(self):
        self.assertTrue(
            is_subscript_substitution_correct(
                ["y", "x", "b"],
                "y = x + b",
                "_alpha1",
                "y_alpha1 - x_alpha1 = b_alpha1",
            )
        )

class TestIsSubscriptSubstitutionCorrectFalseCases(unittest.TestCase):
    def test_prompt_invalid_energy_missing_one_half_factor(self):
        self.assertFalse(
            is_subscript_substitution_correct(
                ["E", "m", "v"],
                "E = (1/2)*m*(v^2)",
                "_i",
                "E_i = (m_i)*((v_i)^2)",
            )
        )

    def test_prompt_invalid_energy_missing_mass_factor(self):
        self.assertFalse(
            is_subscript_substitution_correct(
                ["E", "m", "v"],
                "E = (1/2)*m*(v^2)",
                "_i",
                "E_i = (1/2)*((v_i)^2)",
            )
        )

    def test_prompt_invalid_energy_wrong_subscript_family(self):
        self.assertFalse(
            is_subscript_substitution_correct(
                ["E", "m", "v"],
                "E = (1/2)*m*(v^2)",
                "_i",
                "E_j = (1/2)*(m_j)*((v_j)^2)",
            )
        )

    def test_prompt_invalid_energy_extra_added_term(self):
        self.assertFalse(
            is_subscript_substitution_correct(
                ["E", "m", "v"],
                "E = (1/2)*m*(v^2)",
                "_i",
                "E_i = (1/2)*(m_i + v_i)*((v_i)^2)",
            )
        )

    def test_prompt_invalid_potential_energy_missing_one_subscript(self):
        self.assertFalse(
            is_subscript_substitution_correct(
                ["U", "m", "g", "h"],
                "U = m*g*h",
                "_k",
                "U_k = m_k*g_k*h",
            )
        )

    def test_prompt_invalid_potential_energy_wrong_scaling(self):
        self.assertFalse(
            is_subscript_substitution_correct(
                ["U", "m", "g", "h"],
                "U = m*g*h",
                "_k",
                "2*U_k = m_k*g_k*h_k",
            )
        )

    def test_prompt_invalid_potential_energy_wrong_symbol_subscript(self):
        self.assertFalse(
            is_subscript_substitution_correct(
                ["U", "m", "g", "h"],
                "U = m*g*h",
                "_k",
                "U_k = m_k*g_k*h_i",
            )
        )

    def test_prompt_invalid_potential_energy_mixed_numeric_subscript(self):
        self.assertFalse(
            is_subscript_substitution_correct(
                ["U", "m", "g", "h"],
                "U = m*g*h",
                "_k",
                "U_k = m_1*g_k*h_k",
            )
        )

    def test_invalid_entirely_unsubscripted_result(self):
        self.assertFalse(
            is_subscript_substitution_correct(
                ["E", "m", "v"],
                "E = (1/2)*m*(v^2)",
                "_i",
                "E = (1/2)*m*(v^2)",
            )
        )

    def test_force_relation_missing_factor(self):
        self.assertFalse(
            is_subscript_substitution_correct(
                ["F", "m", "a"],
                "F = m*a",
                "_n",
                "F_n = a_n",
            )
        )

    def test_power_relation_wrong_rearranged_result(self):
        self.assertFalse(
            is_subscript_substitution_correct(
                ["P", "I", "V"],
                "P = I*V",
                "_t2",
                "P_t2/V_t2 = V_t2",
            )
        )

    def test_area_relation_scaled_only_on_left(self):
        self.assertFalse(
            is_subscript_substitution_correct(
                ["A", "l", "w"],
                "A = l*w",
                "_3",
                "2*A_3 = l_3*w_3",
            )
        )

    def test_additive_relation_wrong_sign(self):
        self.assertFalse(
            is_subscript_substitution_correct(
                ["p", "q", "r"],
                "p = q + r",
                "_x",
                "p_x + r_x = q_x",
            )
        )

    def test_kinetic_energy_missing_one_half_factor(self):
        self.assertFalse(
            is_subscript_substitution_correct(
                ["K", "m", "v"],
                "K = (1/2)*m*(v^2)",
                "_b",
                "K_b = (v_b^2)*(m_b)",
            )
        )

    def test_heat_relation_leaves_one_symbol_unsubscripted(self):
        self.assertFalse(
            is_subscript_substitution_correct(
                ["Q", "m", "c", "T"],
                "Q = m*c*T",
                "_ref",
                "Q_ref/(c_ref) = m_ref*T",
            )
        )

    def test_linear_relation_wrong_constant_side(self):
        self.assertFalse(
            is_subscript_substitution_correct(
                ["y", "x", "b"],
                "y = x + b",
                "_1",
                "y_1 = x_1 - b_1",
            )
        )

    def test_resistance_relation_wrong_cross_multiplication(self):
        self.assertFalse(
            is_subscript_substitution_correct(
                ["R", "V", "I"],
                "R = V/I",
                "_k9",
                "R_k9 = V_k9*I_k9",
            )
        )

    def test_motion_relation_uses_mixed_subscripts(self):
        self.assertFalse(
            is_subscript_substitution_correct(
                ["s", "u", "t", "a"],
                "s = u*t + (1/2)*a*(t^2)",
                "_f",
                "2*s_f = 2*u_f*t_f + a_1*(t_f^2)",
            )
        )

    def test_repeated_symbol_occurrences_not_fully_subscripted(self):
        self.assertFalse(
            is_subscript_substitution_correct(
                ["M", "x"],
                "M = x + x^2",
                "_r",
                "M_r = x_r + x^2",
            )
        )


if __name__ == "__main__":
    unittest.main()
