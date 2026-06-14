"""Utility functions for checking symbolic substitution correctness."""  # Describe this module.

from __future__ import annotations  # Keep type annotations from being evaluated at import time.

import sympy as sp  # Import SymPy as the symbolic algebra engine.
from sympy.core.relational import Equality  # Import SymPy's equality relation type.

from .check_util import _build_parse_locals  # Reuse the equation checker's parser namespace builder.
from .check_util import _build_symbol_map  # Reuse the equation checker's symbol validation.
from .check_util import _canonical_residual  # Reuse the equation checker's residual normalization.
from .check_util import _normalize_equation_text  # Reuse the equation checker's Unicode and equality normalization.
from .check_util import _parse_equation  # Reuse the equation checker's equation-to-residual parser.
from .check_util import _parse_expression  # Reuse the equation checker's expression parser.
from .check_util import _same_zero_residual  # Reuse the equation checker's fast residual equivalence check.
from .check_util import _uses_only_requested_symbols  # Reuse the equation checker's declared-symbol guard.
from .check_util import is_equation_equal  # Reuse the public equation equivalence proof function.


def is_substitution_correct(symbol_list: list[str], equation_before: str, substitute_equation: str, equation_after: str) -> bool:  # Define the public substitution checker.
    """Return True when equation_after is provably equation_before after applying substitute_equation."""  # Document the public function contract.
    try:  # Convert invalid inputs and unprovable cases into a False result.
        symbol_map = _build_symbol_map(symbol_list)  # Build SymPy Symbol objects from the caller's declared symbols.
        parse_locals = _build_parse_locals(symbol_map)  # Build the same parser namespace used by is_equation_equal.
        before_residual = _parse_equation_preserving_structure(equation_before, parse_locals)  # Parse before-equation without expanding away substitution targets.
        after_residual = _parse_equation(equation_after, parse_locals)  # Parse the claimed final equation as a zero residual.
        substitution_sides = _parse_substitution_sides(substitute_equation, parse_locals)  # Parse the substitution equation into replaceable sides.
        if before_residual is None or after_residual is None or substitution_sides is None:  # Reject malformed equations.
            return False  # Report that invalid input cannot prove a correct substitution.
        substitution_left, substitution_right = substitution_sides  # Unpack the two sides of the substitution equation.
        substitution_residual = _canonical_residual(substitution_left - substitution_right)  # Convert the substitution equation to a zero residual.
        allowed_symbol_names = set(symbol_map)  # Build the allowed symbol-name set from the declared symbols.
        if not _uses_only_requested_symbols(before_residual, after_residual, allowed_symbol_names):  # Reject undeclared symbols in before or after equations.
            return False  # Report that equations outside the declared symbol list are not accepted.
        if not _uses_only_requested_symbols(substitution_residual, substitution_residual, allowed_symbol_names):  # Reject undeclared symbols in the substitution equation.
            return False  # Report that substitution equations outside the declared symbol list are not accepted.
        candidate_residuals = _candidate_substituted_residuals(before_residual, substitution_left, substitution_right, substitution_residual, list(symbol_map.values()), symbol_list, substitute_equation)  # Build possible results of applying the substitution.
        for candidate_residual in candidate_residuals:  # Check every plausible substituted equation.
            if _residual_matches_equation(symbol_list, candidate_residual, after_residual, equation_after):  # Ask is_equation_equal to prove the candidate equals the claimed result.
                return True  # Report that one substitution candidate proves the claimed result.
        return False  # Report that no candidate proved the substitution correct.
    except Exception:  # Keep malformed strings, unsupported equations, and SymPy failures from escaping.
        return False  # Report unsupported or invalid input as not proven correct.


def _parse_substitution_sides(substitute_equation: str, parse_locals: dict[str, object]) -> tuple[sp.Expr, sp.Expr] | None:  # Parse a substitution equation into two sides.
    normalized = _normalize_equation_text(substitute_equation)  # Normalize Unicode operators and Python-style equality before parsing.
    if not normalized:  # Reject empty substitution strings.
        return None  # Signal that parsing failed.
    if normalized.count("=") == 1:  # Handle ordinary substitution equations such as x = z^3.
        left_text, right_text = normalized.split("=", 1)  # Split the substitution equation into left and right text.
        if not left_text.strip() or not right_text.strip():  # Reject substitutions missing either side of the equals sign.
            return None  # Signal that parsing failed.
        return _parse_expression(left_text, parse_locals, evaluate=False), _parse_expression(right_text, parse_locals, evaluate=False)  # Return the parsed substitution sides.
    if normalized.count("=") > 1:  # Reject chained or malformed equality strings.
        return None  # Signal that parsing failed.
    parsed_expr = _parse_expression(normalized, parse_locals, evaluate=False)  # Parse strings without equals signs as expressions or Eq calls.
    if isinstance(parsed_expr, Equality):  # Handle explicit Eq(lhs, rhs) substitution strings.
        return parsed_expr.lhs, parsed_expr.rhs  # Return the two sides of the Eq object.
    return parsed_expr, sp.Integer(0)  # Treat a plain expression as expression equals zero.


def _parse_equation_preserving_structure(equation: str, parse_locals: dict[str, object]) -> sp.Expr | None:  # Parse an equation while preserving nested substitution targets.
    normalized = _normalize_equation_text(equation)  # Normalize Unicode operators and Python-style equality before parsing.
    if not normalized:  # Reject empty equation strings.
        return None  # Signal that parsing failed.
    if normalized.count("=") == 1:  # Handle ordinary equation strings such as x + 1 = 2.
        left_text, right_text = normalized.split("=", 1)  # Split the equation into left and right expressions.
        if not left_text.strip() or not right_text.strip():  # Reject equations missing either side of the equals sign.
            return None  # Signal that parsing failed.
        left_expr = _parse_expression(left_text, parse_locals, evaluate=False)  # Parse the left side as a SymPy expression.
        right_expr = _parse_expression(right_text, parse_locals, evaluate=False)  # Parse the right side as a SymPy expression.
        return left_expr - right_expr  # Avoid canonical expansion until after substitution matching.
    if normalized.count("=") > 1:  # Reject chained or malformed equality strings.
        return None  # Signal that parsing failed.
    parsed_expr = _parse_expression(normalized, parse_locals, evaluate=False)  # Parse strings without equals signs as expressions or Eq calls.
    if isinstance(parsed_expr, Equality):  # Handle explicit Eq(lhs, rhs) expressions.
        return parsed_expr.lhs - parsed_expr.rhs  # Avoid canonical expansion until after substitution matching.
    return parsed_expr  # Treat a plain expression as expression equals zero.


def _candidate_substituted_residuals(before_residual: sp.Expr, substitution_left: sp.Expr, substitution_right: sp.Expr, substitution_residual: sp.Expr, symbols: list[sp.Symbol], symbol_list: list[str], substitute_equation: str) -> list[sp.Expr]:  # Build substituted residual candidates.
    direct_replacements = _direct_replacements(substitution_left, substitution_right)  # Build exact side-to-side replacement pairs first.
    direct_changed, direct_unchanged = _partition_replacement_candidates(before_residual, direct_replacements)  # Apply exact replacements to the before residual.
    if direct_changed:  # If an exact substitution changed the equation, avoid slower solved inverse substitutions.
        return direct_changed  # Return only real direct substitution candidates.
    solved_replacements = _solved_replacements(substitution_residual, symbols, symbol_list, substitute_equation)  # Build solved replacements only as a fallback.
    solved_changed, solved_unchanged = _partition_replacement_candidates(before_residual, solved_replacements)  # Apply safe solved replacements to the before residual.
    if solved_changed:  # If a solved substitution changed the equation, skipped substitutions should not count as correct.
        return solved_changed  # Return only real solved substitution candidates.
    return direct_unchanged + solved_unchanged  # Return no-op candidates only when no replacement could change the before equation.


def _direct_replacements(substitution_left: sp.Expr, substitution_right: sp.Expr) -> list[tuple[sp.Expr, sp.Expr]]:  # Build exact replacement pairs from the substitution sides.
    replacements: list[tuple[sp.Expr, sp.Expr]] = []  # Start with an empty replacement list.
    _append_replacement(replacements, substitution_left, substitution_right)  # Allow replacing the left side with the right side when safe.
    _append_replacement(replacements, substitution_right, substitution_left)  # Allow replacing the right side with the left side when safe.
    return _unique_replacements(replacements)  # Return direct replacements with duplicates removed.


def _solved_replacements(substitution_residual: sp.Expr, symbols: list[sp.Symbol], symbol_list: list[str], substitute_equation: str) -> list[tuple[sp.Expr, sp.Expr]]:  # Build solved replacement pairs from the substitution equation.
    replacements: list[tuple[sp.Expr, sp.Expr]] = []  # Start with an empty solved replacement list.
    for symbol in symbols:  # Try to derive explicit one-symbol substitutions from rearranged equations.
        solved_replacement = _solve_replacement_for_symbol(substitution_residual, symbol, symbol_list, substitute_equation)  # Solve the substitution equation for this symbol when safe.
        if solved_replacement is not None:  # Check whether a safe solved replacement was found.
            _append_replacement(replacements, solved_replacement[0], solved_replacement[1])  # Add the solved replacement candidate when safe.
    return _unique_replacements(replacements)  # Return replacements with duplicates removed.


def _partition_replacement_candidates(before_residual: sp.Expr, replacements: list[tuple[sp.Expr, sp.Expr]]) -> tuple[list[sp.Expr], list[sp.Expr]]:  # Split replacement results into changed and unchanged candidates.
    changed_candidates: list[sp.Expr] = []  # Store candidates where at least one replacement changed the before equation.
    unchanged_candidates: list[sp.Expr] = []  # Store no-op candidates for substitutions that do not occur in the before equation.
    for old_expression, new_expression in replacements:  # Try every possible replacement direction.
        raw_candidate = _apply_replacement(before_residual, old_expression, new_expression)  # Apply the replacement before canonicalizing.
        candidate = _canonical_residual(raw_candidate)  # Normalize the substituted residual before comparison.
        if _same_structure(raw_candidate, before_residual):  # Check whether the replacement had no structural effect.
            unchanged_candidates.append(candidate)  # Keep the no-op candidate only as a fallback.
        else:  # Handle replacements that actually changed the before residual.
            changed_candidates.append(candidate)  # Prefer changed candidates over no-op candidates.
    return changed_candidates, unchanged_candidates  # Return both candidate groups.


def _append_replacement(replacements: list[tuple[sp.Expr, sp.Expr]], old_expression: sp.Expr, new_expression: sp.Expr) -> None:  # Append a replacement when its target is safe.
    if not _is_safe_replacement_target(old_expression):  # Reject replacement targets that are too broad or expensive.
        return  # Skip unsafe replacement targets.
    replacements.append((old_expression, new_expression))  # Store the safe replacement pair.


def _is_safe_replacement_target(expression: sp.Expr) -> bool:  # Decide whether an expression is safe to use as the old side of subs().
    if expression.is_number:  # Avoid replacing bare constants such as 0 or 1 throughout an expression tree.
        return False  # Report that numeric replacement targets are unsafe.
    return True  # Report that non-numeric symbolic replacement targets are safe.


def _solve_replacement_for_symbol(substitution_residual: sp.Expr, symbol: sp.Symbol, symbol_list: list[str], substitute_equation: str) -> tuple[sp.Expr, sp.Expr] | None:  # Try to solve the substitution equation for one symbol.
    if not substitution_residual.has(symbol):  # Skip symbols that do not occur in the substitution equation.
        return None  # Signal that no replacement is available for this symbol.
    if not _is_linear_in_symbol(substitution_residual, symbol):  # Avoid ambiguous or expensive nonlinear inverse substitutions.
        return None  # Signal that no safe solved replacement is available.
    try:  # SymPy may raise when an equation is unsupported by solve().
        raw_solutions = sp.solve(sp.Eq(substitution_residual, 0), symbol, dict=False, simplify=True)  # Ask SymPy for explicit solutions for the symbol.
    except Exception:  # Treat solver failures as unsupported substitutions.
        return None  # Signal that no reliable solved replacement is available.
    if not isinstance(raw_solutions, (list, tuple, set)):  # Reject unexpected solve() return shapes.
        return None  # Signal that no reliable solved replacement is available.
    solutions = list(raw_solutions)  # Normalize tuples and sets into a list.
    if len(solutions) != 1:  # Reject ambiguous substitutions such as x^2 = z solved for x.
        return None  # Signal that no single safe replacement is available.
    solution = solutions[0]  # Extract the only solution.
    if isinstance(solution, dict):  # Reject dictionary solutions because this function solves one symbol at a time.
        return None  # Signal that no reliable solved replacement is available.
    if not isinstance(solution, sp.Expr):  # Reject non-expression solver outputs.
        return None  # Signal that no reliable solved replacement is available.
    if solution.has(symbol):  # Reject recursive replacements such as x = 1/x.
        return None  # Signal that no safe replacement is available.
    solved_equation = f"{sp.sstr(symbol)} = ({sp.sstr(solution)})"  # Build an equation string for the solved substitution candidate.
    if not is_equation_equal(symbol_list, substitute_equation, solved_equation):  # Require the solved form to be equivalent to the original substitution equation.
        return None  # Reject solved forms that would narrow or broaden the substitution relation.
    return symbol, solution  # Return the safe symbol-to-expression replacement.


def _is_linear_in_symbol(expression: sp.Expr, symbol: sp.Symbol) -> bool:  # Decide whether solving for a symbol is likely safe and cheap.
    try:  # SymPy polynomial conversion can fail for non-polynomial expressions.
        numerator = sp.together(expression).as_numer_denom()[0]  # Use the numerator so rational linear equations can still be solved.
        polynomial = sp.Poly(numerator, symbol)  # Interpret the numerator as a polynomial in the selected symbol.
    except Exception:  # Treat non-polynomial expressions as unsafe for solved substitutions.
        return False  # Report that the expression should not be solved for this symbol.
    return polynomial.degree() == 1  # Allow only linear solved substitutions.


def _unique_replacements(replacements: list[tuple[sp.Expr, sp.Expr]]) -> list[tuple[sp.Expr, sp.Expr]]:  # Remove duplicate replacement pairs while preserving order.
    unique_replacements: list[tuple[sp.Expr, sp.Expr]] = []  # Store the first copy of each replacement.
    seen_keys: set[tuple[str, str]] = set()  # Track structural keys that have already been emitted.
    for old_expression, new_expression in replacements:  # Inspect every proposed replacement.
        key = (sp.srepr(old_expression), sp.srepr(new_expression))  # Build a structural key for the replacement pair.
        if key in seen_keys:  # Skip replacements already seen.
            continue  # Continue with the next proposed replacement.
        seen_keys.add(key)  # Mark this replacement as seen.
        unique_replacements.append((old_expression, new_expression))  # Preserve this replacement.
    return unique_replacements  # Return the de-duplicated replacements.


def _apply_replacement(before_residual: sp.Expr, old_expression: sp.Expr, new_expression: sp.Expr) -> sp.Expr:  # Apply one replacement to a residual.
    return before_residual.subs(old_expression, new_expression)  # Ask SymPy to replace matching subexpressions.


def _same_structure(lhs_expression: sp.Expr, rhs_expression: sp.Expr) -> bool:  # Compare two expressions by structural representation.
    return sp.srepr(lhs_expression) == sp.srepr(rhs_expression)  # Return True when SymPy represents both expressions identically.


def _residual_matches_equation(symbol_list: list[str], candidate_residual: sp.Expr, after_residual: sp.Expr, equation_after: str) -> bool:  # Compare one candidate residual to the claimed final equation.
    if not _same_zero_residual(candidate_residual, after_residual):  # Use a fast residual check before invoking the slower public proof function.
        return False  # Report non-equivalence without triggering solved-form proof attempts.
    candidate_equation = f"({sp.sstr(candidate_residual)}) = 0"  # Convert the residual back to an equation string.
    return is_equation_equal(symbol_list, candidate_equation, equation_after)  # Use the public equation checker as the final proof step.
