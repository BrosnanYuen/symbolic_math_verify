# YAML Math Proof Tutorial

This verifier reads a YAML file with:

- `axioms`
- theorem/proof sections
- optional `calculations`

It accepts small, explicit proof steps. It rejects clever jumps, broken chains, malformed equations, and calculations that are not tied to a known equation side.

## Short Rules

- `axioms` is required and must be a mapping.
- Each axiom needs `equation`.
- Each theorem section needs `equation`.
- `calculations` is optional, but each calculation must include `vars`, `values`, `equation`, `tolerance`, `expected_value`, and `expected_symbol`.
- In axioms and theorem sections, `vars` is optional. If omitted, symbols are auto-detected from the math text.
- In calculations, `vars` is required.
- If you do provide `vars` explicitly, it must include every used symbol and no unused symbols.

## Supported Proof Steps

- Ordinary equivalence: `lhs -> rhs`
- Substitution: `lhs ; known_equation -> rhs`
- Subscript substitution: `lhs : _suffix -> rhs`

Rules:

- The first theorem step must start from an axiom or a previously proven theorem result.
- Every later step must start from the previous step's right-hand side.
- A substitution equation must match an axiom or prior theorem equation.
- A subscript step must apply the same suffix consistently to every symbol from the source equation.
- A proof step may use `;` or `:`, but not both.

## One Complete Example

This example is based directly on the valid and invalid fixtures in `test_yaml/`. The uncommented lines are valid. The commented `INVALID` lines show patterns the verifier rejects.

```yaml
axioms:
  rocket_relation:
    equation: "delta_v = v_e * ln(m_0/m_f)"
  ohms_law:
    equation: "V = I*R"
  power_relation:
    equation: "P = V*I"
  kinetic_energy:
    equation: "K = (1/2)*m*v^2"
  gravitational_potential_energy:
    equation: "U = m*g*h"
  total_energy:
    equation: "E = U + K"
  sinusoid:
    equation: "y = sin(t)"
  trig_identity:
    equation: "sin(x)^2 + cos(x)^2 = 1"
  pi_relation:
    equation: "theta = pi"
  # INVALID: trivial identity axioms are rejected
  # tautology:
  #   equation: "x = x"
  # INVALID: malformed symbol names or malformed equations are rejected
  # bad_axiom:
  #   equation: "1x = y"

rocket_mass:
  # INVALID broken chain:
  # m_0 = m_f -> m_f*exp(delta_v/v_e) = m_0
  # INVALID wrong rearrangement:
  # delta_v = v_e * ln(m_0/m_f) -> delta_v*v_e = ln(m_0/m_f)
  equation: |+
    delta_v = v_e * ln(m_0/m_f) -> delta_v/v_e = ln(m_0/m_f)
    delta_v/v_e = ln(m_0/m_f) -> exp(delta_v/v_e) = m_0/m_f
    exp(delta_v/v_e) = m_0/m_f -> m_0 = m_f*exp(delta_v/v_e)

current_from_ohms_law:
  equation: |+
    V = I*R -> I = V/R

power_in_voltage_form:
  # INVALID missing substitution equation:
  # P = V*I ; -> P = V^2/R
  # INVALID unknown substitution equation:
  # P = V*I ; V = Q/C -> P = (Q/C)*R
  # INVALID substitution not applied:
  # P = V*I ; I = V/R -> P = V*I
  equation: |+
    P = V*I ; I = V/R -> P = V^2/R

kinetic_initial:
  equation: |+
    K = (1/2)*m*v^2 : _i -> K_i = (1/2)*m_i*((v_i)^2)

gravitational_initial:
  equation: |+
    U = m*g*h : _i -> U_i = m_i*g_i*h_i

energy_initial:
  # INVALID missing suffix:
  # E = U + K : -> E_i = U_i + K_i
  # INVALID subscript not applied:
  # E = U + K : _i -> E = U + K
  # INVALID wrong subscript family:
  # E = U + K : _i -> E_j = U_i + K_i
  equation: |+
    E = U + K : _i -> E_i = U_i + K_i

energy_initial_expanded:
  equation: |+
    E_i = U_i + K_i ; U_i = m_i*g_i*h_i -> E_i = K_i + m_i*g_i*h_i
    E_i = K_i + m_i*g_i*h_i ; K_i = (1/2)*m_i*((v_i)^2) -> E_i = (1/2)*m_i*((v_i)^2) + m_i*g_i*h_i

laplace_step:
  # INVALID transform variables must still match the source equation:
  # y = sin(t) -> laplace_transform(y(x), x, s) = laplace_transform(sin(x), x, s)
  equation: |+
    y = sin(t) -> laplace_transform(y(t), t, s) = laplace_transform(sin(t), t, s)

identity_rewrite:
  equation: |+
    sin(x)^2 + cos(x)^2 = 1 -> sin(x)^2 + cos(x)^2 - 1 = 0

half_pi:
  equation: |+
    theta = pi -> theta/2 = pi/2

calculations:
  eval_initial_mass:
    vars: ["delta_v", "v_e", "m_f"]
    values: [200.0, 4.0, 50000.0]
    equation: "m_f*exp(delta_v/v_e)"
    tolerance: 0.001
    expected_value: 2.59235276429e+26
    expected_symbol: "m_0"
    # INVALID: calculation equation must match a known equation side
    # equation: "m_f*exp(delta_v*v_e)"
    # INVALID: expected_symbol must match the symbol implied by the known equation
    # expected_symbol: "banana"

  eval_power:
    vars: ["V", "R"]
    values: [12.0, 3.0]
    equation: "V^2/R"
    tolerance: 0.001
    expected_value: 48.0
    expected_symbol: "P"
    # INVALID: calculations always need vars and values populated
    # INVALID: vars: omitted
```

## Another simple example

```yaml
axioms:
  current_limit_relation:
    equation: "Imax = Vbe/R2"
  base_current_relation:
    equation: "Ib = Ic/beta"
  bias_voltage_relation:
    equation: "Vr1 = Vs - 2*Vbe"
  bias_resistor_relation:
    equation: "R1 = Vr1/Ib"
sense_resistor_solve:
  equation: |+
    Imax = Vbe/R2 -> Imax*R2 = Vbe
    Imax*R2 = Vbe -> R2 = Vbe/Imax
calculations:
  eval_current_limit:
    vars: ["Vbe", "R2"]
    values: [0.6, 30.0]
    equation: "Vbe/R2"
    tolerance: 0.000001
    expected_value: 0.02
    expected_symbol: "Imax"
  eval_sense_resistor:
    vars: ["Vbe", "Imax"]
    values: [0.6, 0.02]
    equation: "Vbe/Imax"
    tolerance: 0.000001
    expected_value: 30.0
    expected_symbol: "R2"
```

## What The Verifier Accepts

- Ordinary equations like `x = y`
- Zero-form expressions like `x - y`
- Unicode math normalization such as `×`, `−`, `÷`, and `π`
- Common SymPy-style functions such as `sin`, `cos`, `exp`, `ln`, `log`, `sqrt`, `diff`, `laplace_transform`, and `fourier_transform`
- Informative identities such as `sin(x)^2 + cos(x)^2 = 1`
- Auto-detected variables for axioms and theorem sections

## What The Verifier Rejects

- Chained or trailing equals, such as `a = b = c` or `x + 1 =`
- First theorem steps that do not start from an axiom or prior theorem
- Later theorem steps that do not continue from the previous result
- Substitutions that are missing the source equation or substitution equation
- Substitutions that do nothing when a relevant substitution target exists
- Subscript substitutions with an empty suffix, empty source, or mixed suffix families
- Trivial identity axioms such as `x = x` or `1 = 1`
- Calculations based on arbitrary expressions not seen as one side of a known equation
- Wrong `expected_symbol` values for calculations
- Explicit `vars` lists with missing or extra symbols

## Practical Advice

- Prefer omitting `vars` in axioms and theorem sections.
- Keep proof steps small and literal.
- Split long proofs into several theorem sections when the chain would otherwise restart from a different known equation.
- Use calculations only after the exact target expression already appears on one side of an axiom or theorem equation.
