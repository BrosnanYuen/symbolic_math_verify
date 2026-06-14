"""Extract variable names from math-like strings without returning functions or constants."""

from __future__ import annotations

import re

_IDENTIFIER_PATTERN = re.compile(r"(?<!\w)([A-Za-z]\w*)")
_FUNCTION_CALL_PATTERN = re.compile(r"(?<!\w)([A-Za-z]\w*)\s*\(")
_CONSTANT_NAMES = {
    "e",
    "oo",
    "pi",
}
_FUNCTION_NAMES = {
    "abs",
    "acos",
    "asin",
    "atan",
    "cos",
    "cosh",
    "derivative",
    "diff",
    "eq",
    "exp",
    "factorial",
    "fourier_transform",
    "gamma",
    "integral",
    "integrate",
    "laplace_transform",
    "ln",
    "log",
    "sin",
    "sinh",
    "sqrt",
    "sum",
    "tan",
    "tanh",
}


def extract_variables(math_expression: str) -> list[str]:
    """Return variable names found in a math-like string, excluding functions and constants."""
    if not isinstance(math_expression, str):
        raise TypeError("math_expression must be a string")
    if not math_expression.strip():
        return []

    called_names = {
        match.group(1)
        for match in _FUNCTION_CALL_PATTERN.finditer(math_expression)
        if match.group(1).lower() in _FUNCTION_NAMES
    }

    variables: list[str] = []
    seen: set[str] = set()
    for match in _IDENTIFIER_PATTERN.finditer(math_expression):
        token = match.group(1)
        if token in _CONSTANT_NAMES:
            continue
        if token in called_names:
            continue
        if token in seen:
            continue
        seen.add(token)
        variables.append(token)
    return variables
