# Symbolic Math Verify

Utilities for checking symbolic equation equivalence and symbolic substitution correctness using SymPy.

The main APIs are:

```python
from src.check_util import is_equation_equal
from src.check_substitution import is_substitution_correct
from src.check_calculation import is_calculation_correct
```

## Setup

Create and activate the project virtual environment:

```bash
python3 -m venv .venv
. .venv/bin/activate
```

Install SymPy:

```bash
pip install sympy
```

If the virtual environment already exists, use the project interpreter directly:

```bash
.venv/bin/python -m pip install sympy
```

## Run Tests

```bash
.venv/bin/python -m unittest discover -s tests -p 'tests_*.py'
```

Run tests in parallel across CPU cores:

```bash
.venv/bin/python tests/run_parallel_unittest.py
```

## Public API

### `is_equation_equal(symbol_list: list[str], lhs_equation: str, rhs_equation: str) -> bool`

Returns `True` when SymPy can prove that `lhs_equation` and `rhs_equation` define the same zero relation.

Returns `False` when the equations are different, cannot be parsed, use undeclared symbols, or cannot be proven equivalent by the implemented SymPy checks.

Import it with:

```python
from src.check_util import is_equation_equal
```

Basic usage:

```python
from src.check_util import is_equation_equal

result = is_equation_equal(["x"], "x + 2 = 5", "x = 3")

print(result)  # True
```

RC charging equation example:

```python
from src.check_util import is_equation_equal

result = is_equation_equal(
    ["Vc", "Vsource", "t", "R", "C"],
    "Vc=Vsource*(1−e^(−t/(R*C)))",
    "t/R = -C*ln(1- (Vc/Vsource))",
)

print(result)  # True
```

Non-equivalent example:

```python
from src.check_util import is_equation_equal

result = is_equation_equal(["x"], "x^2 = 4", "x = 2")

print(result)  # False
```

`x^2 = 4` has two solutions, `x = 2` and `x = -2`, so it is not the same equation as `x = 2`.

### `is_substitution_correct(symbol_list: list[str], equation_before: str, substitute_equation: str, equation_after: str) -> bool`

Returns `True` when SymPy can prove that `equation_after` is a valid result of applying `substitute_equation` to `equation_before`.

Returns `False` when the substitution is wrong, cannot be parsed, uses undeclared symbols, is ambiguous, or cannot be proven by the implemented checks.

Import it with:

```python
from src.check_substitution import is_substitution_correct
```

Basic usage:

```python
from src.check_substitution import is_substitution_correct

result = is_substitution_correct(
    ["x", "y", "z"],
    "y = 1/x  + 5*z",
    "x  =  z^3",
    "y = 1/(z^3)  + 5*z",
)

print(result)  # True
```

Wrong substitution example:

```python
from src.check_substitution import is_substitution_correct

result = is_substitution_correct(
    ["x", "y", "z"],
    "y = 2*x + 5*z",
    "x  =  z^3",
    "y = z^3 + 5*z",
)

print(result)  # False
```

The second example is false because substituting `x = z^3` into `y = 2*x + 5*z` gives `y = 2*z^3 + 5*z`, not `y = z^3 + 5*z`.

### `is_calculation_correct(symbol_list: list[str], symbol_val: list[float], equation: str, expected_value: float, tolerance: float) -> bool`

Returns `True` when substituting `symbol_val` into `equation` and evaluating it produces an `actual` value that satisfies:

```text
abs((actual - expected_value) / actual) < tolerance
```

Returns `False` when the relative-error condition is not met, or when input is invalid or unsupported.

Import it with:

```python
from src.check_calculation import is_calculation_correct
```

Basic usage:

```python
from src.check_calculation import is_calculation_correct

result = is_calculation_correct(
    ["x", "y", "z"],
    [0.5, -0.2, 14.0],
    "x + y^2 + 1/z",
    0.61142,
    0.001,
)

print(result)  # True
```

Incorrect expected-value example:

```python
from src.check_calculation import is_calculation_correct

result = is_calculation_correct(
    ["x", "y", "z"],
    [0.5, -0.2, 14.0],
    "x + y^2 + 1/z",
    1.511,
    0.001,
)

print(result)  # False
```

## Arguments

`symbol_list` must be a list of strings containing every symbol used by both equations.

Valid symbol names must be parser-friendly Python identifiers such as:

```python
["x", "y", "R", "C", "Vsource", "Vc"]
```

Invalid or unsupported symbol names return `False` through the public API:

```python
["1x", "R-C", ""]
```

`lhs_equation`, `rhs_equation`, `equation_before`, `substitute_equation`, and `equation_after` must be strings. They may be ordinary equations:

```python
"x + y = 10"
"y = 10 - x"
```

They may also be zero expressions without an equals sign:

```python
"x^2 - 1"
"(x - 1)*(x + 1)"
```

In that form, the expression is treated as:

```text
expression = 0
```

For `is_calculation_correct`, `symbol_val` must be a list of finite numeric values with the same length and order as `symbol_list`, and `equation` must be a SymPy-compatible expression string (or a single equation interpreted as a residual).

## Supported Syntax

The parser supports common SymPy-compatible math syntax:

```text
x^2
2x
sin(x)^2
cos(x)^2
sqrt(x)
exp(x)
ln(x)
log(x)
Abs(x)
pi
E
oo
Eq(lhs, rhs)
```

The parser also normalizes common Unicode math characters:

```text
− to -
– to -
— to -
× to *
⋅ to *
÷ to /
π to pi
```

## How Equivalence Is Checked

The public function:

1. Builds SymPy symbols from `symbol_list`.
2. Parses each equation string.
3. Converts each equation into a residual form, `left - right`.
4. Checks that both equations use only declared symbols.
5. Tries direct symbolic residual equivalence.
6. Tries solved-form equivalence for declared symbols.
7. Returns `True` only when one of those checks proves equivalence.

This design avoids known false positives such as:

```python
is_equation_equal(["x", "y"], "x*y = 0", "x = 0")  # False
```

`x*y = 0` is not equivalent to `x = 0` because `y = 0` is also allowed.

## How Substitution Is Checked

The public substitution function:

1. Builds SymPy symbols from `symbol_list`.
2. Parses `equation_before`, `substitute_equation`, and `equation_after`.
3. Converts equations into residual form, `left - right`.
4. Checks that all equations use only declared symbols.
5. Builds direct substitution candidates from both sides of `substitute_equation`.
6. If direct replacement cannot change the before equation, tries safe linear solved substitutions.
7. Compares each substituted candidate to `equation_after` using the equation-equivalence checker.
8. Returns `True` only when one candidate proves the claimed substitution result.

This design avoids unsafe substitutions such as:

```python
is_substitution_correct(["x", "y", "z"], "y = x", "x^2 = z", "y = sqrt(z)")  # False
```

`x^2 = z` does not prove `x = sqrt(z)` because `x = -sqrt(z)` is also possible.

## Limitations

Symbolic equation equivalence is not generally decidable for every possible equation. This function is intentionally conservative:

```text
proven equivalent -> True
different or not proven -> False
```

That means `False` can mean either:

```text
the equations are truly different
```

or:

```text
SymPy and this checker could not prove they are the same
```

The substitution checker follows the same conservative rule:

```text
proven correct -> True
wrong, ambiguous, invalid, or not proven -> False
```

## Internal Helpers

The following functions are implementation details in `src/check_util.py`. They are underscore-prefixed and should not be treated as stable public API.

`src/check_substitution.py` also contains underscore-prefixed helper functions for parsing substitution sides, building replacement candidates, and comparing substituted residuals. Those helpers are implementation details as well.

### `_build_symbol_map(symbol_list)`

Validates `symbol_list` and builds a mapping from each symbol name to a SymPy `Symbol`.

### `_build_parse_locals(symbol_map)`

Builds the parser namespace by combining known math constants/functions with caller-declared symbols.

### `_normalize_equation_text(equation)`

Normalizes whitespace, Python-style equality, and common Unicode math characters before parsing.

### `_parse_equation(equation, parse_locals)`

Parses an equation string into a residual expression where the equation is represented as `left - right = 0`.

### `_parse_expression(expression, parse_locals)`

Parses one expression string with SymPy's parser and the configured transformations.

### `_canonical_residual(expression)`

Simplifies, combines, cancels, and factors a residual expression into a more stable comparison form.

### `_uses_only_requested_symbols(lhs_residual, rhs_residual, allowed_symbol_names)`

Checks that both parsed equations only use symbols declared in `symbol_list`.

### `_same_zero_residual(lhs_residual, rhs_residual)`

Checks whether two residual expressions define the same zero equation directly.

### `_zero_numerator(expression)`

Extracts the numerator that determines when a rational expression is zero.

### `_same_solved_relation(lhs_residual, rhs_residual, symbols)`

Solves both residual equations for declared symbols and compares the solved forms.

### `_has_possible_extra_zero_factor(residual, solve_symbol)`

Detects multiplicative factors that could make solved-form comparison unsafe.

### `_solve_for_symbol(residual, symbol)`

Uses SymPy to solve one residual equation for one symbol and returns a normalized solution list.

### `_solution_lists_equal(lhs_solutions, rhs_solutions)`

Compares two finite solution lists with one-to-one matching.

### `_find_matching_solution(lhs_solution, rhs_solutions, used_indexes)`

Finds an unused equivalent solution in a list of right-side solutions.

### `_expressions_equal(lhs_expression, rhs_expression)`

Checks whether two expressions are equivalent by proving their difference is zero.

### `_proves_zero(expression)`

Runs several SymPy zero checks and simplifiers to prove an expression is zero.

### `_zero_proof_candidates(expression)`

Generates simplified candidate expressions for zero-proof checks.

### `_safe_simplify(expression)`

Runs `sympy.simplify()` while safely falling back to the original expression on failure.

### `_is_nonzero_constant(expression)`

Checks whether an expression is a finite, nonzero constant multiplier.

### `_can_prove_nonzero(expression)`

Uses SymPy assumptions and zero checks to determine whether a factor is definitely nonzero.
