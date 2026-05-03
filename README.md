# Symbolic Math Verify

Utilities for checking whether two equation strings describe the same symbolic equation using SymPy.

The main API is `is_equation_equal(symbol_list, lhs_equation, rhs_equation)` in `src/check_util.py`.

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

`lhs_equation` and `rhs_equation` must be strings. They may be ordinary equations:

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

## Internal Helpers

The following functions are implementation details in `src/check_util.py`. They are underscore-prefixed and should not be treated as stable public API.

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
