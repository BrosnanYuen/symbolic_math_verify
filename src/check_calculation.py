"""Utility function for checking substituted numeric calculations against an expected value."""  # Describe this module.

from __future__ import annotations  # Keep type annotations from being evaluated at import time.

import math  # Provide finite-value checks and absolute value utilities.

import sympy as sp  # Use SymPy for symbolic parsing and evaluation.

from .check_util import _build_parse_locals  # Reuse parser-local construction from the existing utilities.
from .check_util import _build_symbol_map  # Reuse symbol-list validation from the existing utilities.
from .check_util import _normalize_equation_text  # Reuse equation-text normalization from the existing utilities.
from .check_util import _parse_equation  # Reuse equation parsing to residual form when an equals sign is present.
from .check_util import _parse_expression  # Reuse expression parsing when no equals sign is present.


def is_calculation_correct(symbol_list: list[str], symbol_val: list[float], equation: str, expected_value: float, tolerance: float) -> bool:  # Define the public calculation-checking API.
    """Return True when substituted evaluation is within the requested relative tolerance."""  # Document the function contract.
    try:  # Convert malformed input and unsupported expressions into a False result.
        symbol_map = _build_symbol_map(symbol_list)  # Validate symbol names and build Symbol objects.
        if not isinstance(symbol_val, list):  # Require a list of values to match the symbol list.
            return False  # Reject non-list value containers.
        if len(symbol_map) != len(symbol_val):  # Require one numeric value per declared symbol.
            return False  # Reject mismatched symbol/value lengths.
        if not isinstance(equation, str):  # Require the equation/expression input to be text.
            return False  # Reject non-string equation inputs.
        if not isinstance(expected_value, (int, float)):  # Require a real numeric expected value.
            return False  # Reject non-numeric expected values.
        if not isinstance(tolerance, (int, float)):  # Require a real numeric tolerance.
            return False  # Reject non-numeric tolerances.
        if tolerance < 0:  # Require a non-negative tolerance.
            return False  # Reject negative tolerances.

        parse_locals = _build_parse_locals(symbol_map)  # Build parser namespace with math names and declared symbols.
        normalized = _normalize_equation_text(equation)  # Normalize Unicode operators and whitespace.
        if not normalized:  # Reject empty equation strings after normalization.
            return False  # Report that empty input cannot be evaluated.

        if normalized.count("=") == 1:  # Handle equation strings by evaluating their residual form.
            parsed = _parse_equation(normalized, parse_locals)  # Parse as left-minus-right residual.
            if parsed is None:  # Reject equations that cannot be parsed.
                return False  # Report that parsing failed.
            expression = parsed  # Use the parsed residual as the expression to evaluate.
        elif normalized.count("=") > 1:  # Reject malformed equations with multiple equals signs.
            return False  # Report malformed equation input.
        else:  # Handle plain expression strings without an equals sign.
            expression = _parse_expression(normalized, parse_locals)  # Parse a single expression.

        substitution_map: dict[sp.Symbol, float] = {}  # Prepare a Symbol-to-float substitution mapping.
        for symbol_name, numeric_value in zip(symbol_list, symbol_val):  # Pair each declared symbol with its numeric value.
            if not isinstance(numeric_value, (int, float)):  # Require every substitution value to be numeric.
                return False  # Reject non-numeric substitution values.
            if not math.isfinite(float(numeric_value)):  # Require each substitution value to be finite.
                return False  # Reject inf and nan substitution values.
            substitution_map[symbol_map[symbol_name.strip()]] = float(numeric_value)  # Store the numeric substitution.

        substituted_expression = expression.subs(substitution_map)  # Apply numeric substitutions to the expression.
        evaluated_expression = sp.N(substituted_expression)  # Ask SymPy for a numeric evaluation.
        if getattr(evaluated_expression, "is_real", None) is False:  # Reject non-real evaluated results.
            return False  # Report that complex values are not supported by this checker.
        actual_value = float(evaluated_expression)  # Convert the evaluated SymPy number into a Python float.

        if not math.isfinite(actual_value):  # Require a finite computed actual value.
            return False  # Reject inf and nan computed results.
        if actual_value == 0.0:  # Guard against division by zero in relative-error calculation.
            return False  # Return False because the required relative-error formula is undefined at zero.
        if not math.isfinite(float(expected_value)):  # Require a finite expected value.
            return False  # Reject inf and nan expected results.

        relative_error = abs((actual_value - float(expected_value)) / actual_value)  # Compute the required absolute relative error.
        return relative_error < float(tolerance)  # Return True exactly when the required strict inequality holds.
    except Exception:  # Keep parser, substitution, and numeric errors from escaping the public API.
        return False  # Report unsupported or invalid input as not proven correct.
