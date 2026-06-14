"""Utility function for checking symbolic subscript substitutions."""  # Describe this module.

from __future__ import annotations  # Keep type annotations from being evaluated at import time.

import re  # Provide regular-expression helpers for safe symbol-name replacement.

from .check_substitution import is_substitution_correct  # Reuse the existing symbolic substitution proof function.
from .check_util import _build_symbol_map  # Reuse existing symbol-name validation for parser-friendly identifiers.
from .check_util import is_equation_equal  # Reuse the existing symbolic equation-equivalence proof function.

_SUBSCRIPT_PATTERN = re.compile(r"^_\w+$")  # Accept subscripts such as _i, _1, and _f2.


def _replace_symbol_name(equation_text: str, symbol_name: str, replacement_name: str) -> str:  # Replace one standalone symbol name in equation text.
    pattern = re.compile(rf"(?<!\w){re.escape(symbol_name)}(?!\w)")  # Match only whole identifier occurrences so overlapping names stay intact.
    return pattern.sub(replacement_name, equation_text)  # Return the equation text with the requested symbol renamed everywhere it stands alone.


def is_subscript_substitution_correct(symbol_list: list[str], equation_before: str, subscript: str, equation_after: str) -> bool:  # Define the public subscript-substitution checker.
    """Return True when equation_after is provably equation_before with the same subscript applied to every declared symbol."""  # Document the public function contract.
    try:  # Convert invalid inputs and unprovable cases into a False result.
        if not isinstance(symbol_list, list):  # Require the caller to provide the declared symbols as a list.
            return False  # Reject non-list symbol containers.
        if not isinstance(equation_before, str):  # Require the original equation input to be text.
            return False  # Reject non-string before-equation inputs.
        if not isinstance(subscript, str):  # Require the requested subscript to be text.
            return False  # Reject non-string subscript inputs.
        if not isinstance(equation_after, str):  # Require the final equation input to be text.
            return False  # Reject non-string after-equation inputs.
        if not equation_before.strip():  # Require a non-empty original equation string after trimming whitespace.
            return False  # Reject empty before-equation inputs.
        if not equation_after.strip():  # Require a non-empty final equation string after trimming whitespace.
            return False  # Reject empty after-equation inputs.
        if not _SUBSCRIPT_PATTERN.fullmatch(subscript):  # Require a parser-friendly suffix that starts with an underscore.
            return False  # Reject empty or malformed subscripts such as i, -, or whitespace.

        original_symbol_map = _build_symbol_map(symbol_list)  # Validate the original symbol names and preserve the caller's symbol order.
        original_symbol_names = list(original_symbol_map)  # Keep the validated symbol names in a stable ordered list.
        subscripted_symbol_names = [f"{symbol_name}{subscript}" for symbol_name in original_symbol_names]  # Build the subscripted symbol names that should appear after substitution.
        if len(set(subscripted_symbol_names)) != len(subscripted_symbol_names):  # Detect ambiguous cases where two different symbols collapse to the same subscripted name.
            return False  # Reject non-injective renamings because they cannot prove a safe symbol-by-symbol substitution.

        combined_symbol_names = original_symbol_names + subscripted_symbol_names  # Allow both original and subscripted names while proving intermediate substitution steps.
        _build_symbol_map(combined_symbol_names)  # Validate that every generated subscripted symbol is still parser-friendly and not duplicated.

        current_equation = equation_before  # Start from the original caller-provided equation text.
        for symbol_name in original_symbol_names:  # Apply the requested subscript to each declared symbol one symbol at a time.
            subscripted_symbol_name = f"{symbol_name}{subscript}"  # Build the new name for the current symbol.
            substitution_equation = f"{symbol_name} = {subscripted_symbol_name}"  # Express the current rename as an ordinary substitution equation.
            next_equation = _replace_symbol_name(current_equation, symbol_name, subscripted_symbol_name)  # Build the exact intermediate equation produced by renaming this one symbol everywhere.
            if not is_substitution_correct(combined_symbol_names, current_equation, substitution_equation, next_equation):  # Ask the existing substitution checker to prove this one-symbol rename is valid.
                return False  # Reject the overall subscript substitution when any intermediate rename is not provably correct.
            current_equation = next_equation  # Advance to the newly renamed equation before processing the next symbol.

        return is_equation_equal(combined_symbol_names, current_equation, equation_after)  # Accept the final answer only when it is symbolically equivalent to the fully subscripted equation.
    except Exception:  # Keep parser, substitution, and validation errors from escaping the public API.
        return False  # Report unsupported or invalid input as not proven correct.
