# Symbolic Math Verify

Symbolic math verification utilities built on SymPy.

This project checks whether equations are equivalent, whether a substitution step is valid, whether a uniform subscript rename is valid, whether a numeric calculation matches an expected value, and whether a YAML proof file is valid.

PyPI package: `symbolic-math-verify`

## Install

```bash
pip install symbolic-math-verify
```

Import it as `symbolic_math_verify`.

## Public API

```python
from symbolic_math_verify import extract_variables
from symbolic_math_verify import is_calculation_correct
from symbolic_math_verify import is_equation_equal
from symbolic_math_verify import is_subscript_substitution_correct
from symbolic_math_verify import is_substitution_correct
from symbolic_math_verify import verify_yaml_file
```

## What It Does

- `is_equation_equal(symbol_list, lhs_equation, rhs_equation) -> bool`
  Proves whether two equations define the same zero relation.
- `is_substitution_correct(symbol_list, equation_before, substitute_equation, equation_after) -> bool`
  Proves whether `equation_after` is a valid substitution result.
- `is_subscript_substitution_correct(symbol_list, equation_before, subscript, equation_after) -> bool`
  Proves whether the same suffix such as `_i` was applied consistently to every declared symbol.
- `is_calculation_correct(symbol_list, symbol_val, equation, expected_value, tolerance) -> bool`
  Evaluates an expression or equation residual numerically and compares it to an expected value.
- `extract_variables(math_expression) -> list[str]`
  Extracts variable names from math-like text while skipping known functions and constants.
- `verify_yaml_file(file_path) -> str`
  Validates YAML axioms, proof chains, substitution steps, subscript-substitution steps, and calculations.

## Examples

Equation equivalence:

```python
from symbolic_math_verify import is_equation_equal

is_equation_equal(["x"], "x + 2 = 5", "x = 3")
# True
```

Substitution:

```python
from symbolic_math_verify import is_substitution_correct

is_substitution_correct(
    ["x", "y", "z"],
    "y = 1/x + 5*z",
    "x = z^3",
    "y = 1/(z^3) + 5*z",
)
# True
```

Subscript substitution:

```python
from symbolic_math_verify import is_subscript_substitution_correct

is_subscript_substitution_correct(
    ["E", "m", "v"],
    "E = (1/2)*m*(v^2)",
    "_i",
    "E_i = (1/2)*m_i*(v_i^2)",
)
# True
```

Calculation:

```python
from symbolic_math_verify import is_calculation_correct

is_calculation_correct(
    ["x", "y", "z"],
    [0.5, -0.2, 14.0],
    "x + y^2 + 1/z",
    0.61142,
    0.001,
)
# True
```

Variable extraction:

```python
from symbolic_math_verify import extract_variables

extract_variables("P = I*V ; V = I*R -> P = R*I^2")
# ['P', 'I', 'V', 'R']
```

YAML verification:

```python
from symbolic_math_verify import verify_yaml_file

verify_yaml_file("test_yaml/valid_11_prompt_with_calculation.yaml")
# "Math proofs are valid"
```

## YAML Support

`verify_yaml_file()` validates YAML files containing:

- `axioms`
- theorem/proof sections with `->`, `;`, and `:` proof steps
- optional `calculations`

For axioms and theorem sections, `vars` may be omitted and will be auto-detected from the math text. For `calculations`, `vars` is required.

See [YAML_tutorial.md](/home/brosnan/symbolic_math_verify/symbolic_math_verify/YAML_tutorial.md) for a full YAML proof example and validation rules.

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Run the full test suite in parallel:

```bash
python tests/run_parallel_unittest.py
```

Run individual test files:

```bash
python -m unittest tests/tests_check_calculation.py
python -m unittest tests/tests_check_substitution.py
python -m unittest tests/tests_check_util.py
python -m unittest tests/tests_extract_variables.py
python -m unittest tests/tests_subscript_substitution.py
python -m unittest tests/tests_verify_yaml.py
```

## Notes

- The checker is conservative: `True` means proven, while `False` means wrong, invalid, ambiguous, or not proven.
- Equations may be written as `lhs = rhs` or as zero expressions such as `x^2 - 1`.
- Common Unicode math characters such as `−`, `×`, `÷`, and `π` are normalized before parsing.
