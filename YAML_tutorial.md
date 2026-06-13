# YAML Math Proof Tutorial for LLMs

This guide explains how to write a valid `.yaml` math proof file for the verifier used in this repository.

The goal is not just to produce YAML that looks right. The goal is to produce YAML that the verifier will accept as:

- valid YAML
- valid symbolic proofs
- valid calculations

This tutorial is based on the examples in `README.md` and the fixtures in `./test_yaml/`.

## What the Verifier Expects

A proof file can contain:

- `axioms`
- one or more theorem/proof sections
- optional `calculations`

At a high level:

1. `axioms` define known equations.
2. Each theorem section proves new equations step by step.
3. Each proof step must use one of the supported step formats.
4. Optional `calculations` must evaluate an expression that came from an axiom or theorem.

If anything is wrong, the verifier returns one of:

- `Error! YAML file is invalid: line <n>: <reason>`
- `Error! Math proofs are invalid: line <n>: <reason>`
- `Error! Calculations are invalid: line <n>: <reason>`

If everything is correct, it returns:

- `Math proofs are valid`

## Minimal Valid File

```yaml
axioms:
  conservation_of_energy:
    vars: ["E_i", "E_f"]
    equation: "E_i = E_f"
```

This is the smallest pattern that works.

## Top-Level Structure

Use this shape:

```yaml
axioms:
  axiom_name:
    vars: ["x", "y"]
    equation: "x = y"

theorem_name:
  vars: ["x", "y"]
  equation: |+
    x = y -> y = x

calculations:
  calc_name:
    vars: ["x"]
    values: [3.0]
    equation: "x + 1"
    tolerance: 0.001
    expected_value: 4.0
    expected_symbol: "result"
```

Rules:

- The top level must be a YAML mapping.
- `axioms` must exist and must be a mapping.
- Each axiom must have `vars` and `equation`.
- Each theorem/proof section must have `vars` and `equation`.
- `calculations` is optional, but if present it must be a mapping.

## Symbol Rules

Symbol names must be SymPy-friendly identifiers.

Good examples:

```python
["x", "y", "R", "C", "m_0", "delta_v", "E_i"]
```

Bad examples:

```python
["1x", "R-C", ""]
```

Important constraints:

- In axioms, `vars` must include every symbol used in the equation.
- In axioms, `vars` must not include extra unused symbols.
- In theorem sections, it is safest to include every symbol that appears anywhere in that section.
- For subscript substitution steps, include both the original symbols and the subscripted symbols that appear on the right-hand side.

## Equation Rules

Equation strings must be valid SymPy-style math.

Good examples:

```text
x + y = 10
y = 10 - x
sin(x)^2 + cos(x)^2 = 1
exp(delta_v/v_e) = m_0/m_f
```

Supported syntax includes common SymPy-style math such as:

- `^` for powers
- implicit multiplication like `2x`
- `sin`, `cos`, `log`, `ln`, `exp`, `sqrt`, `Abs`
- `pi`, `E`

Avoid these common mistakes:

- chained equals like `a = b = c`
- trailing equals like `x + 1 =`
- undeclared variables
- malformed expressions

## The Three Supported Proof Step Types

Inside a theorem section, the `equation` field is a block of one or more proof steps.

Use `|+` and put one proof step on each line.

### 1. Ordinary Equivalence Step

Format:

```text
lhs_equation -> rhs_equation
```

Example:

```yaml
equation: |+
  delta_v = v_e * ln(m_0/m_f) -> delta_v/v_e = ln(m_0/m_f)
```

Use this when the right-hand side is algebraically equivalent to the left-hand side.

### 2. Substitution Step

Format:

```text
lhs_equation ; substitute_equation -> rhs_equation
```

Example:

```yaml
equation: |+
  P = V*I ; V = I*R -> P = (I^2)*R
```

Rules:

- Use exactly one `;`
- The source equation before `;` cannot be empty
- The substitution equation after `;` cannot be empty
- The substitution equation must match an axiom or a previously proven theorem equation
- The substitution must actually be applied

### 3. Subscript Substitution Step

Format:

```text
lhs_equation : _suffix -> rhs_equation
```

Example:

```yaml
equation: |+
  E = U + K : _i -> E_i = U_i + K_i
```

Rules:

- Use exactly one `:`
- The source equation before `:` cannot be empty
- The suffix after `:` cannot be empty
- The suffix should look like `_i`, `_f`, `_1`, `_alpha1`
- The right-hand side must consistently apply that suffix to every symbol from the source equation
- The subscript substitution must actually be applied

Do not mix `;` and `:` in the same proof step.

## Proof Chaining Rules

These rules are critical.

### First Step Rule

The left-hand side of the first proof step in a theorem must match:

- an axiom equation, or
- a previously proven theorem equation

If the first step starts from a brand-new equation that is not already known, the proof fails.

### Later Step Rule

For every later proof step:

- the left-hand side must equal the previous step's right-hand side

This means proof sections are strict chains.

Good:

```yaml
equation: |+
  delta_v = v_e * ln(m_0/m_f) -> delta_v/v_e = ln(m_0/m_f)
  delta_v/v_e = ln(m_0/m_f) -> exp(delta_v/v_e) = m_0/m_f
```

Bad:

```yaml
equation: |+
  delta_v = v_e * ln(m_0/m_f) -> delta_v/v_e = ln(m_0/m_f)
  m_0 = m_f -> m_f*exp(delta_v/v_e) = m_0
```

The second step is invalid because it does not continue from the previous right-hand side.

## How to Build a Valid Theorem Section

When an LLM writes a theorem section, use this process.

1. Choose a known starting equation from `axioms` or an earlier theorem.
2. Decide whether the next move is:
   - algebraic rearrangement
   - substitution using a known equation
   - subscript substitution using a suffix
3. Write exactly one proof step per line.
4. Make sure each next line starts from the previous line's result.
5. Keep all symbols declared in the section's `vars`.

Template:

```yaml
theorem_name:
  vars: ["a", "b", "c"]
  equation: |+
    known_equation -> equivalent_equation
    equivalent_equation ; substitution_equation -> substituted_equation
    substituted_equation : _i -> subscripted_equation
```

## Valid Example: Pure Algebraic Rearrangement

```yaml
axioms:
  tsiolkovsky_rocket_equation:
    vars: ["delta_v", "v_e", "m_0", "m_f"]
    equation: "delta_v = v_e * ln(m_0/m_f)"
equation_propellant_mass:
  vars: ["delta_v", "v_e", "m_0", "m_f"]
  equation: |+
    delta_v = v_e * ln(m_0/m_f) -> delta_v/v_e = ln(m_0/m_f)
    delta_v/v_e = ln(m_0/m_f) -> exp(delta_v/v_e) = m_0/m_f
    exp(delta_v/v_e) = m_0/m_f -> m_0 = m_f*exp(delta_v/v_e)
```

## Valid Example: Known-Equation Substitution

```yaml
axioms:
  voltage_current_resistance_equation:
    vars: ["V", "I", "R"]
    equation: "V = I*R"
  electrical_power_equation:
    vars: ["V", "I", "P"]
    equation: "P = V*I"
rearrange_equation:
  vars: ["V", "I", "R"]
  equation: |+
    V = I*R -> I = V/R
electrical_current_resistance_power_equation:
  vars: ["V", "I", "P", "R"]
  equation: |+
    P = V*I ; I = V/R -> P = (V^2)/R
```

## Valid Example: Subscript Substitution

```yaml
axioms:
  kinetic_energy:
    vars: ["K", "m", "v"]
    equation: "K = (1/2)*m*v^2"
  gravitational_potential_energy:
    vars: ["U", "m", "g", "h"]
    equation: "U = m*g*h"
  kinetic_gravitational_potential_energy:
    vars: ["E", "U", "K"]
    equation: "E = U + K"
kinetic_initial:
  vars: ["K", "m", "v", "K_i", "m_i", "v_i"]
  equation: |+
    K = (1/2)*m*v^2 : _i -> K_i = (1/2)*m_i*((v_i)^2)
energy_initial:
  vars: ["E", "U", "K", "E_i", "U_i", "K_i", "m_i", "v_i", "g_i", "h_i"]
  equation: |+
    E = U + K : _i -> E_i = U_i + K_i
```

## Calculation Rules

`calculations` are optional.

Each calculation must contain:

- `vars`
- `values`
- `equation`
- `tolerance`
- `expected_value`
- `expected_symbol`

Example:

```yaml
calculations:
  calculate_initial_mass:
    vars: ["delta_v", "v_e", "m_f"]
    values: [200.0, 4.0, 50000.0]
    equation: "m_f*exp(delta_v/v_e)"
    tolerance: 0.001
    expected_value: 2.59235e+26
    expected_symbol: "m_0"
```

Important calculation constraints:

- `vars` and `values` must have the same length
- `equation` must match an expression from a known axiom or theorem side
- `expected_value` must be numerically correct within `tolerance`

Bad calculation example:

```yaml
equation: "m_f*exp(delta_v*v_e)"
```

This fails if the known theorem only proved `m_f*exp(delta_v/v_e)`.

## Common Failure Modes

### 1. Missing `vars` or `equation`

Bad:

```yaml
axioms:
  conservation_of_energy:
    equation: "E_i = E_f"
```

### 2. First Proof Step Starts from an Unknown Equation

Bad:

```yaml
equation: |+
  x = y + 1 -> y = x - 1
```

This only works if `x = y + 1` is already an axiom or prior theorem result.

### 3. Broken Proof Chain

Bad:

```yaml
equation: |+
  A -> B
  C -> D
```

The second line must start from `B`, not `C`.

### 4. Substitution Equation Not Known

Bad:

```yaml
equation: |+
  P = V*I ; V = Q/C -> P = (Q/C)*R
```

If `V = Q/C` is not an axiom or prior theorem equation, this fails.

### 5. Substitution Not Actually Applied

Bad:

```yaml
equation: |+
  P = V*I ; V = I*R -> P = V*I
```

### 6. Empty Substitution Part

Bad:

```yaml
equation: |+
  P = V*I ; -> P = (I^2)*R
```

### 7. Empty Subscript Suffix

Bad:

```yaml
equation: |+
  E = U + K : -> E_i = U_i + K_i
```

### 8. Empty Subscript Source

Bad:

```yaml
equation: |+
  : _i -> E_i = U_i + K_i
```

### 9. Wrong Subscript Family

Bad:

```yaml
equation: |+
  K = (1/2)*m*v^2 : _i -> K_j = (1/2)*m_i*((v_i)^2)
```

### 10. Calculation Expression Not Proven Earlier

Bad:

```yaml
equation: "m_f*exp(delta_v*v_e)"
```

if the theorem proved:

```text
m_f*exp(delta_v/v_e)
```

## Best Practices for LLMs

When generating a proof file, follow this checklist.

### Axiom Checklist

- Every axiom has `vars`
- Every axiom has `equation`
- Every symbol in the axiom equation appears in `vars`
- No extra unused symbols are listed in axiom `vars`

### Theorem Checklist

- The theorem has `vars`
- The theorem has an `equation` block with `|+`
- The first step starts from a known equation
- Every next step starts from the previous result
- Each step uses exactly one of:
  - `->`
  - `; ... ->`
  - `: ... ->`
- Do not mix `;` and `:` in one line
- Every symbol used anywhere in the theorem appears in `vars`

### Calculation Checklist

- The calculation expression matches a proven expression
- `vars` and `values` lengths match
- The numeric result is actually correct

## Recommended LLM Workflow

If you are an LLM and need to write a valid proof file, do this:

1. Write the axioms first.
2. Decide the exact theorem target equation.
3. Break the proof into tiny verifier-friendly steps.
4. Prefer many small algebraic steps over one large clever jump.
5. Use `;` only when substituting with a known equation.
6. Use `:` only when applying a uniform subscript suffix.
7. After writing each step, check that the next line starts from the previous right-hand side.
8. Only add calculations after the symbolic proof already contains the target expression.

## Safe Template for New Files

```yaml
axioms:
  axiom_one:
    vars: ["a", "b"]
    equation: "a = b"
  axiom_two:
    vars: ["b", "c"]
    equation: "b = c"

theorem_one:
  vars: ["a", "b", "c"]
  equation: |+
    a = b -> b = a
    b = a ; b = c -> c = a

theorem_two:
  vars: ["a", "b", "a_i", "b_i"]
  equation: |+
    a = b : _i -> a_i = b_i

calculations:
  calc_one:
    vars: ["x"]
    values: [2.0]
    equation: "x + 1"
    tolerance: 0.001
    expected_value: 3.0
    expected_symbol: "result"
```

## Final Advice

The verifier is conservative.

That means:

- true statements can still fail if the proof is not written in a form the verifier can check
- shorter is not always better
- explicit step-by-step chaining is safer than skipping steps

If you want the highest success rate, optimize for:

- simple axioms
- small proof steps
- strict chaining
- exact symbol declarations
- exact reuse of known equations
- exact reuse of proven expressions for calculations
