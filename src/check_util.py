"""Utility functions for checking symbolic equation equivalence."""  # Describe this module.

from __future__ import annotations  # Keep type annotations from being evaluated at import time.

import re  # Provide a small validator for parser-friendly symbol names.

import sympy as sp  # Import SymPy as the symbolic algebra engine.
from sympy.core.function import AppliedUndef  # Identify caller-declared undefined function calls.
from sympy.core.relational import Equality  # Import SymPy's equality relation type.
from sympy.parsing.sympy_parser import convert_xor, function_exponentiation, implicit_multiplication_application, parse_expr, standard_transformations  # Import SymPy string parsing helpers.

_TRANSFORMATIONS = standard_transformations + (implicit_multiplication_application, convert_xor, function_exponentiation)  # Enable common math syntax such as 2x, x^2, and sin^2(x).
_SYMBOL_NAME_PATTERN = re.compile(r"^[A-Za-z_]\w*$")  # Accept symbol names that SymPy's expression parser can read directly.
_CALLABLE_NAME_PATTERN = re.compile(r"\b([A-Za-z_]\w*)\s*\(")  # Find names used with function-call syntax.
_TRANSFORM_PLACEHOLDER = sp.Dummy("_transform_arg")  # Stand in for the equation side inside a transformation template.
_UNICODE_REPLACEMENTS = {  # Normalize common Unicode math characters before parsing.
    "\u2212": "-",  # Convert the Unicode minus sign to an ASCII hyphen-minus.
    "\u2013": "-",  # Convert an en dash to an ASCII hyphen-minus.
    "\u2014": "-",  # Convert an em dash to an ASCII hyphen-minus.
    "\u00d7": "*",  # Convert the multiplication sign to an ASCII asterisk.
    "\u22c5": "*",  # Convert the dot operator to an ASCII asterisk.
    "\u00f7": "/",  # Convert the division sign to an ASCII slash.
    "\u03c0": "pi",  # Convert the lowercase Greek pi character to SymPy's pi name.
}  # Finish the Unicode normalization table.
_DEFAULT_PARSE_LOCALS = {  # Define constants and functions that should parse as mathematical objects.
    "E": sp.E,  # Treat capital E as Euler's number unless the caller declares E as a symbol.
    "e": sp.E,  # Treat lowercase e as Euler's number unless the caller declares e as a symbol.
    "I": sp.I,  # Treat I as the imaginary unit unless the caller declares I as a symbol.
    "pi": sp.pi,  # Treat pi as the mathematical constant pi unless the caller declares pi as a symbol.
    "oo": sp.oo,  # Treat oo as symbolic infinity unless the caller declares oo as a symbol.
    "Eq": sp.Eq,  # Allow users to write Eq(lhs, rhs) as an equation string.
    "Abs": sp.Abs,  # Allow absolute-value expressions.
    "sqrt": sp.sqrt,  # Allow square-root expressions.
    "exp": sp.exp,  # Allow explicit exponential expressions.
    "ln": sp.log,  # Allow ln(x) as an alias for the natural logarithm.
    "log": sp.log,  # Allow log(x) as SymPy's natural logarithm.
    "sin": sp.sin,  # Allow sine expressions.
    "cos": sp.cos,  # Allow cosine expressions.
    "tan": sp.tan,  # Allow tangent expressions.
    "asin": sp.asin,  # Allow inverse sine expressions.
    "acos": sp.acos,  # Allow inverse cosine expressions.
    "atan": sp.atan,  # Allow inverse tangent expressions.
    "sinh": sp.sinh,  # Allow hyperbolic sine expressions.
    "cosh": sp.cosh,  # Allow hyperbolic cosine expressions.
    "tanh": sp.tanh,  # Allow hyperbolic tangent expressions.
}  # Finish the default parser locals table.


def is_equation_equal(symbol_list: list[str], lhs_equation: str, rhs_equation: str) -> bool:  # Define the public equation-equivalence checker.
    """Return True when SymPy can prove two equation strings have the same zero relation."""  # Document the function contract.
    try:  # Convert invalid inputs and unprovable cases into a False result.
        symbol_map = _build_symbol_map(symbol_list)  # Build SymPy Symbol objects from the caller's declared symbols.
        parse_locals = _build_parse_locals(symbol_map)  # Combine declared symbols with known math functions and constants.
        lhs_residual = _parse_equation(lhs_equation, parse_locals)  # Convert the left equation string into lhs minus rhs.
        rhs_residual = _parse_equation(rhs_equation, parse_locals)  # Convert the right equation string into lhs minus rhs.
        if lhs_residual is None or rhs_residual is None:  # Reject strings that could not be parsed as expressions or equations.
            return False  # Report that unparsable input cannot be proven equivalent.
        if not _uses_only_requested_symbols(lhs_residual, rhs_residual, set(symbol_map)):  # Reject undeclared symbols in either parsed equation.
            return False  # Report that equations outside the declared symbol list are not accepted.
        if _same_zero_residual(lhs_residual, rhs_residual):  # Try direct algebraic equivalence of the normalized residual equations.
            return True  # Report proven equivalence when the residuals differ only by a nonzero constant factor.
        if _same_solved_relation(lhs_residual, rhs_residual, list(symbol_map.values())):  # Try equivalence after solving both equations for a declared symbol.
            return True  # Report proven equivalence for rearranged equations with the same solved form.
        if _same_transformed_relation(symbol_map, lhs_equation, rhs_equation):  # Try proof by same transformation applied to both equation sides.
            return True  # Report proven correctness for equations such as h(f(x)) = h(g(x)).
        return False  # Report non-equivalence when all proof attempts fail.
    except Exception:  # Keep malformed strings, unsupported equations, and SymPy failures from escaping.
        return False  # Report unsupported or invalid input as not proven equivalent.


def _build_symbol_map(symbol_list: list[str]) -> dict[str, sp.Symbol]:  # Convert a list of names into SymPy symbols.
    if not isinstance(symbol_list, list):  # Require the API shape requested by the caller.
        raise TypeError("symbol_list must be a list of strings")  # Raise an internal error that the public function converts to False.
    symbol_map: dict[str, sp.Symbol] = {}  # Create an ordered mapping so solve attempts follow the caller's symbol order.
    for symbol_name in symbol_list:  # Visit every declared symbol name.
        if not isinstance(symbol_name, str):  # Reject non-string symbol declarations.
            raise TypeError("every symbol must be a string")  # Raise an internal error that the public function converts to False.
        clean_name = symbol_name.strip()  # Ignore accidental leading or trailing whitespace in symbol names.
        if not clean_name:  # Reject empty symbol names.
            raise ValueError("symbol names cannot be empty")  # Raise an internal error that the public function converts to False.
        if clean_name in symbol_map:  # Reject duplicated symbols because they are ambiguous input.
            raise ValueError(f"duplicate symbol: {clean_name}")  # Raise an internal error that the public function converts to False.
        if not _SYMBOL_NAME_PATTERN.fullmatch(clean_name):  # Reject names that cannot be referenced directly in parse_expr strings.
            raise ValueError(f"unsupported symbol name: {clean_name}")  # Raise an internal error that the public function converts to False.
        symbol_map[clean_name] = sp.Symbol(clean_name)  # Store the declared symbol for parser and solver use.
    return symbol_map  # Return the completed symbol mapping.


def _build_parse_locals(symbol_map: dict[str, sp.Symbol]) -> dict[str, object]:  # Build the parser namespace for one comparison.
    parse_locals = dict(_DEFAULT_PARSE_LOCALS)  # Start with supported constants and functions.
    parse_locals.update(symbol_map)  # Let caller-declared symbols override constants or function names when necessary.
    return parse_locals  # Return the namespace passed to SymPy's parser.


def _normalize_equation_text(equation: str) -> str:  # Normalize equation text before parsing.
    if not isinstance(equation, str):  # Require equation input to be text.
        raise TypeError("equation must be a string")  # Raise an internal error that the public function converts to False.
    normalized = equation.strip()  # Remove leading and trailing whitespace.
    for unicode_value, ascii_value in _UNICODE_REPLACEMENTS.items():  # Apply every supported Unicode-to-ASCII replacement.
        normalized = normalized.replace(unicode_value, ascii_value)  # Replace one Unicode math character everywhere in the string.
    normalized = normalized.replace("==", "=")  # Treat Python-style equality as equation equality.
    return normalized  # Return text that is easier for SymPy to parse.


def _parse_equation(equation: str, parse_locals: dict[str, object]) -> sp.Expr | None:  # Parse one equation string into a zero residual.
    normalized = _normalize_equation_text(equation)  # Normalize Unicode operators and whitespace before parsing.
    if not normalized:  # Reject empty equation strings.
        return None  # Signal that parsing failed.
    if normalized.count("=") == 1:  # Handle ordinary equation strings such as x + 1 = 2.
        left_text, right_text = normalized.split("=", 1)  # Split the equation into left and right expressions.
        if not left_text.strip() or not right_text.strip():  # Reject equations missing either side of the equals sign.
            return None  # Signal that parsing failed.
        left_expr = _parse_expression(left_text, parse_locals)  # Parse the left side as a SymPy expression.
        right_expr = _parse_expression(right_text, parse_locals)  # Parse the right side as a SymPy expression.
        return _canonical_residual(left_expr - right_expr)  # Return the equation as left minus right equals zero.
    if normalized.count("=") > 1:  # Reject chained or malformed equality strings.
        return None  # Signal that parsing failed.
    parsed_expr = _parse_expression(normalized, parse_locals)  # Parse strings without an equals sign as expressions or Eq calls.
    if isinstance(parsed_expr, Equality):  # Handle explicit Eq(lhs, rhs) expressions.
        return _canonical_residual(parsed_expr.lhs - parsed_expr.rhs)  # Return the Eq object as lhs minus rhs equals zero.
    return _canonical_residual(parsed_expr)  # Treat a plain expression as expression equals zero.


def _parse_expression(expression: str, parse_locals: dict[str, object], evaluate: bool = True) -> sp.Expr:  # Parse one mathematical expression string.
    return parse_expr(expression, local_dict=parse_locals, transformations=_TRANSFORMATIONS, evaluate=evaluate)  # Delegate parsing to SymPy.


def _same_transformed_relation(symbol_map: dict[str, sp.Symbol], lhs_equation: str, rhs_equation: str) -> bool:  # Check whether one equation applies the same expression template to the other's sides.
    lhs_sides = _parse_equation_sides_preserving_functions(lhs_equation, symbol_map)  # Parse the first equation without collapsing function-call notation.
    rhs_sides = _parse_equation_sides_preserving_functions(rhs_equation, symbol_map)  # Parse the second equation without collapsing function-call notation.
    if lhs_sides is None or rhs_sides is None:  # Reject inputs that cannot be structurally parsed.
        return False  # Report that no transformation proof is available.
    allowed_symbol_names = set(symbol_map)  # Use the same declared-name policy as the main residual checker.
    if not _sides_use_only_requested_names(lhs_sides, allowed_symbol_names):  # Reject undeclared names in the first equation.
        return False  # Report that undeclared symbols/functions cannot prove equivalence.
    if not _sides_use_only_requested_names(rhs_sides, allowed_symbol_names):  # Reject undeclared names in the second equation.
        return False  # Report that undeclared symbols/functions cannot prove equivalence.
    symbols = list(symbol_map.values())  # Preserve caller order for dependent-function notation checks.
    return _applies_same_template(lhs_sides, rhs_sides, symbols) or _applies_same_template(rhs_sides, lhs_sides, symbols)  # Allow either equation to be the transformed one.


def _parse_equation_sides_preserving_functions(equation: str, symbol_map: dict[str, sp.Symbol]) -> tuple[sp.Expr, sp.Expr] | None:  # Parse an equation into raw sides for transformation-template matching.
    normalized = _normalize_equation_text(equation)  # Normalize Unicode operators and whitespace before structural parsing.
    if not normalized:  # Reject empty equation strings.
        return None  # Signal that parsing failed.
    if normalized.count("=") == 1:  # Handle ordinary equation strings.
        left_text, right_text = normalized.split("=", 1)  # Split the equation into left and right expressions.
        if not left_text.strip() or not right_text.strip():  # Reject equations missing either side.
            return None  # Signal that parsing failed.
        return (
            _parse_expression_preserving_declared_functions(left_text, symbol_map),
            _parse_expression_preserving_declared_functions(right_text, symbol_map),
        )  # Return raw, unevaluated sides.
    if normalized.count("=") > 1:  # Reject chained or malformed equality strings.
        return None  # Signal that parsing failed.
    parsed_expr = _parse_expression_preserving_declared_functions(normalized, symbol_map)  # Parse expression or Eq(...) form.
    if isinstance(parsed_expr, Equality):  # Handle explicit Eq(lhs, rhs) expressions.
        return parsed_expr.lhs, parsed_expr.rhs  # Return the Eq object's sides.
    return parsed_expr, sp.Integer(0)  # Treat a plain expression as expression equals zero.


def _parse_expression_preserving_declared_functions(expression: str, symbol_map: dict[str, sp.Symbol]) -> sp.Expr:  # Parse one side while treating declared call syntax like y(x) as a function call.
    parse_locals = _build_parse_locals(symbol_map)  # Start with the normal parser namespace.
    for function_name in _declared_callable_names(expression, symbol_map):  # Find caller-declared names used as functions in this expression.
        parse_locals[function_name] = sp.Function(function_name)  # Let y(x), f(x), h(...) parse as undefined function applications.
    return _parse_expression(expression, parse_locals, evaluate=False)  # Preserve outer transformation structure for template matching.


def _declared_callable_names(expression: str, symbol_map: dict[str, sp.Symbol]) -> set[str]:  # Find declared symbol names used with function-call syntax.
    return {
        match.group(1)
        for match in _CALLABLE_NAME_PATTERN.finditer(expression)
        if match.group(1) in symbol_map and match.group(1) not in _DEFAULT_PARSE_LOCALS
    }  # Avoid overriding supported math functions such as sin, log, and exp.


def _sides_use_only_requested_names(sides: tuple[sp.Expr, sp.Expr], allowed_symbol_names: set[str]) -> bool:  # Check symbols and caller-declared undefined functions.
    for side in sides:  # Inspect both sides of the equation.
        used_symbol_names = {symbol.name for symbol in side.free_symbols}  # Collect ordinary symbols.
        used_function_names = {function_call.func.__name__ for function_call in side.atoms(AppliedUndef)}  # Collect undefined function names.
        if not used_symbol_names.issubset(allowed_symbol_names):  # Reject undeclared symbols.
            return False  # Report invalid input.
        if not used_function_names.issubset(allowed_symbol_names):  # Reject undeclared function names.
            return False  # Report invalid input.
    return True  # Report that all names are declared.


def _applies_same_template(base_sides: tuple[sp.Expr, sp.Expr], transformed_sides: tuple[sp.Expr, sp.Expr], symbols: list[sp.Symbol]) -> bool:  # Test whether transformed_sides are T(base_left) = T(base_right).
    base_left, base_right = base_sides  # Unpack the equation being transformed.
    transformed_left, transformed_right = transformed_sides  # Unpack the candidate transformed equation.
    return _templates_match(base_left, base_right, transformed_left, transformed_right, symbols) or _templates_match(base_left, base_right, transformed_right, transformed_left, symbols)  # Equation sides can be swapped.


def _templates_match(base_left: sp.Expr, base_right: sp.Expr, transformed_left: sp.Expr, transformed_right: sp.Expr, symbols: list[sp.Symbol]) -> bool:  # Compare transformation templates for one side ordering.
    left_templates = _templates_for_target(transformed_left, base_left, symbols)  # Replace the base left side inside the transformed left side.
    if not left_templates:  # Require the transformed left side to contain the base left side.
        return False  # Report no match.
    right_templates = _templates_for_target(transformed_right, base_right, symbols)  # Replace the base right side inside the transformed right side.
    if not right_templates:  # Require the transformed right side to contain the base right side.
        return False  # Report no match.
    return bool(left_templates.intersection(right_templates))  # The same template on both sides proves a valid transformation.


def _templates_for_target(expression: sp.Expr, target: sp.Expr, symbols: list[sp.Symbol]) -> set[str]:  # Build structural templates by replacing target occurrences with a placeholder.
    templates: set[str] = set()  # Store templates by structural representation.
    for subexpression in sp.preorder_traversal(expression):  # Consider every nested expression as the transformation argument.
        if _matches_transform_target(subexpression, target, symbols):  # Check whether this subexpression represents the original equation side.
            template = expression.xreplace({subexpression: _TRANSFORM_PLACEHOLDER})  # Replace matching occurrences with a shared placeholder.
            templates.add(sp.srepr(template))  # Store a comparison-stable template key.
    return templates  # Return every possible template for ambiguous nested expressions.


def _matches_transform_target(subexpression: sp.Expr, target: sp.Expr, symbols: list[sp.Symbol]) -> bool:  # Decide whether a subexpression can stand for an original equation side.
    if _same_structure(subexpression, target):  # Prefer exact structural matches.
        return True  # Report a direct match.
    if isinstance(target, sp.Symbol) and _is_applied_form_of_symbol(subexpression, target):  # Treat y(x) as dependent-function notation for y.
        return True  # Report a dependent-function match.
    return False  # Report no match.


def _is_applied_form_of_symbol(expression: sp.Expr, symbol: sp.Symbol) -> bool:  # Recognize y(x) as a callable rendering of the symbol y.
    return isinstance(expression, AppliedUndef) and expression.func.__name__ == symbol.name  # Match by declared function name.


def _same_structure(lhs_expression: sp.Expr, rhs_expression: sp.Expr) -> bool:  # Compare two expressions by structural representation.
    return sp.srepr(lhs_expression) == sp.srepr(rhs_expression)  # Return True when SymPy represents both expressions identically.


def _canonical_residual(expression: sp.Expr) -> sp.Expr:  # Put a residual into a simpler standard form.
    return sp.factor(sp.cancel(sp.together(sp.simplify(expression))))  # Combine rational terms, cancel common factors, and factor the result.


def _uses_only_requested_symbols(lhs_residual: sp.Expr, rhs_residual: sp.Expr, allowed_symbol_names: set[str]) -> bool:  # Check symbol-list coverage.
    used_symbol_names = {symbol.name for residual in (lhs_residual, rhs_residual) for symbol in residual.free_symbols}  # Collect every free symbol used by either equation.
    return used_symbol_names.issubset(allowed_symbol_names)  # Accept only equations whose symbols are all declared by the caller.


def _same_zero_residual(lhs_residual: sp.Expr, rhs_residual: sp.Expr) -> bool:  # Test direct residual equivalence.
    lhs_numerator = _zero_numerator(lhs_residual)  # Extract the zero-defining numerator from the left residual.
    rhs_numerator = _zero_numerator(rhs_residual)  # Extract the zero-defining numerator from the right residual.
    lhs_is_zero = _proves_zero(lhs_numerator)  # Determine whether the left residual is identically zero.
    rhs_is_zero = _proves_zero(rhs_numerator)  # Determine whether the right residual is identically zero.
    if lhs_is_zero and rhs_is_zero:  # Check whether both equations are identities.
        return True  # Report that two identity equations are equivalent.
    if lhs_is_zero or rhs_is_zero:  # Check whether only one equation is an identity.
        return False  # Report that an identity and a non-identity equation are not equivalent.
    if _proves_zero(lhs_numerator - rhs_numerator):  # Check whether the residuals are exactly the same.
        return True  # Report direct equality of the residual equations.
    if _proves_zero(lhs_numerator + rhs_numerator):  # Check whether the residuals differ only by sign.
        return True  # Report equivalence because f = 0 and -f = 0 define the same equation.
    ratio = _safe_simplify(lhs_numerator / rhs_numerator)  # Compute the multiplier between residuals.
    return _is_nonzero_constant(ratio)  # Accept only nonzero constant multipliers as direct equivalence.


def _zero_numerator(expression: sp.Expr) -> sp.Expr:  # Extract the part of an expression that must be zero.
    simplified = _safe_simplify(expression)  # Simplify the expression before separating rational numerator and denominator.
    numerator, _denominator = sp.fraction(sp.together(simplified))  # Use the numerator because a fraction is zero exactly when its numerator is zero.
    return sp.factor(sp.cancel(numerator))  # Return a factored numerator for easier comparison.


def _same_solved_relation(lhs_residual: sp.Expr, rhs_residual: sp.Expr, symbols: list[sp.Symbol]) -> bool:  # Compare equations by solving them for each declared symbol.
    for symbol in symbols:  # Try every declared symbol as a possible solved variable.
        if not lhs_residual.has(symbol) and not rhs_residual.has(symbol):  # Skip symbols that neither equation actually uses.
            continue  # Move to the next declared symbol.
        if _has_possible_extra_zero_factor(lhs_residual, symbol):  # Avoid solve() false positives caused by omitted multiplicative zero factors.
            continue  # Move to the next symbol because this solved form is not a safe proof.
        if _has_possible_extra_zero_factor(rhs_residual, symbol):  # Apply the same multiplicative-factor check to the right equation.
            continue  # Move to the next symbol because this solved form is not a safe proof.
        lhs_solutions = _solve_for_symbol(lhs_residual, symbol)  # Solve the left equation for the current symbol.
        rhs_solutions = _solve_for_symbol(rhs_residual, symbol)  # Solve the right equation for the current symbol.
        if _solution_lists_equal(lhs_solutions, rhs_solutions):  # Compare the two finite solution lists.
            return True  # Report equivalence when both equations solve to the same relation for this symbol.
    return False  # Report that no solved form proved equivalence.


def _has_possible_extra_zero_factor(residual: sp.Expr, solve_symbol: sp.Symbol) -> bool:  # Detect symbol-dependent factors that solve() can silently drop.
    numerator = _zero_numerator(residual)  # Work with the zero-defining numerator of the residual.
    factored = sp.factor(numerator)  # Factor the numerator so multiplicative parts are visible.
    if not isinstance(factored, sp.Mul):  # Non-products do not expose extra multiplicative zero factors.
        return False  # Report no unsafe factor.
    for factor in factored.args:  # Inspect every multiplicative factor.
        if factor.free_symbols and not factor.has(solve_symbol) and not _can_prove_nonzero(factor):  # Find factors independent of the solved symbol that might become zero.
            return True  # Report that this solved form could add extra solutions.
    return False  # Report no unsafe extra factor.


def _solve_for_symbol(residual: sp.Expr, symbol: sp.Symbol) -> list[sp.Expr] | None:  # Solve one residual equation for one symbol.
    try:  # SymPy may raise when an equation is unsupported by solve().
        raw_solutions = sp.solve(sp.Eq(residual, 0), symbol, dict=False, simplify=True)  # Ask SymPy for explicit finite solutions.
    except Exception:  # Treat solver failures as an unproven comparison.
        return None  # Signal that no reliable solution list is available.
    if not isinstance(raw_solutions, (list, tuple, set)):  # Reject unexpected solve() return shapes.
        return None  # Signal that no reliable solution list is available.
    solutions: list[sp.Expr] = []  # Build a normalized list of expression solutions.
    for solution in raw_solutions:  # Normalize every returned solution.
        if isinstance(solution, dict):  # Skip dictionary solutions because this function solves one symbol at a time.
            return None  # Signal that no reliable single-symbol solution list is available.
        solutions.append(_safe_simplify(solution))  # Store a simplified solution expression.
    return solutions  # Return the finite solution list.


def _solution_lists_equal(lhs_solutions: list[sp.Expr] | None, rhs_solutions: list[sp.Expr] | None) -> bool:  # Compare two finite solution lists.
    if lhs_solutions is None or rhs_solutions is None:  # Reject unavailable solution lists.
        return False  # Report that unavailable solutions do not prove equivalence.
    if not lhs_solutions or not rhs_solutions:  # Reject empty lists because solve() uses them for both no-solution and unsupported cases.
        return False  # Report that empty solve output is not enough proof.
    if len(lhs_solutions) != len(rhs_solutions):  # Require the same number of explicit solutions.
        return False  # Report non-equivalence for solution lists with different lengths.
    matched_rhs_indexes: set[int] = set()  # Track right-side solutions already matched to a left-side solution.
    for lhs_solution in lhs_solutions:  # Match each left solution against one right solution.
        matched_index = _find_matching_solution(lhs_solution, rhs_solutions, matched_rhs_indexes)  # Search for an unused equivalent right solution.
        if matched_index is None:  # Detect a left solution with no right-side equivalent.
            return False  # Report non-equivalence when any solution is unmatched.
        matched_rhs_indexes.add(matched_index)  # Mark the matched right-side solution as used.
    return True  # Report equivalence when every solution has a one-to-one match.


def _find_matching_solution(lhs_solution: sp.Expr, rhs_solutions: list[sp.Expr], used_indexes: set[int]) -> int | None:  # Find one equivalent unused solution.
    for index, rhs_solution in enumerate(rhs_solutions):  # Check every right-side solution with its index.
        if index in used_indexes:  # Skip right-side solutions already matched.
            continue  # Move to the next right-side solution.
        if _expressions_equal(lhs_solution, rhs_solution):  # Test whether the two solution expressions are equivalent.
            return index  # Return the matching right-side index.
    return None  # Report that no matching solution was found.


def _expressions_equal(lhs_expression: sp.Expr, rhs_expression: sp.Expr) -> bool:  # Test expression equivalence.
    return _proves_zero(lhs_expression - rhs_expression)  # Expressions are equivalent when their difference simplifies to zero.


def _proves_zero(expression: sp.Expr) -> bool:  # Ask several SymPy simplifiers whether an expression is zero.
    candidates = _zero_proof_candidates(expression)  # Build a small set of equivalent simplification candidates.
    for candidate in candidates:  # Inspect each candidate expression.
        if candidate == 0:  # Check exact Python/SymPy equality with zero.
            return True  # Report a proven zero expression.
        if getattr(candidate, "is_zero", None) is True:  # Check SymPy's structural zero assumption.
            return True  # Report a proven zero expression.
        try:  # SymPy's equals() can fail on unsupported expressions.
            if candidate.equals(0) is True:  # Ask SymPy for semantic equality with zero.
                return True  # Report a proven zero expression.
        except Exception:  # Ignore equality-check failures.
            continue  # Move to the next candidate.
    return False  # Report that no simplifier proved the expression is zero.


def _zero_proof_candidates(expression: sp.Expr) -> list[sp.Expr]:  # Generate simplification candidates for zero testing.
    candidates = [expression]  # Start with the original expression.
    simplifiers = (sp.simplify, lambda value: sp.cancel(sp.together(value)), sp.factor, sp.trigsimp, lambda value: sp.powsimp(value, force=True), lambda value: sp.logcombine(value, force=True))  # List targeted simplifiers used by the checker.
    for simplifier in simplifiers:  # Apply each simplifier independently.
        try:  # Some simplifiers fail on some expression classes.
            candidates.append(simplifier(expression))  # Store the simplified candidate.
        except Exception:  # Ignore simplifier failures.
            continue  # Continue with the remaining simplifiers.
    return candidates  # Return all zero-proof candidates.


def _safe_simplify(expression: sp.Expr) -> sp.Expr:  # Simplify an expression while keeping failures contained.
    try:  # SymPy simplification can raise for malformed or unsupported expressions.
        return sp.simplify(expression)  # Return SymPy's simplified expression.
    except Exception:  # Fall back to the original expression when simplification fails.
        return expression  # Preserve the expression for later proof attempts.


def _is_nonzero_constant(expression: sp.Expr) -> bool:  # Decide whether an expression is a nonzero constant multiplier.
    simplified = _safe_simplify(expression)  # Simplify before checking symbols and zero-ness.
    if simplified.free_symbols:  # Reject multipliers that depend on any declared variable.
        return False  # Report that a variable-dependent multiplier is unsafe.
    if simplified.has(sp.nan, sp.zoo, sp.oo, -sp.oo):  # Reject undefined or infinite multipliers.
        return False  # Report that invalid constants are unsafe.
    return not _proves_zero(simplified)  # Accept finite constants that are not zero.


def _can_prove_nonzero(expression: sp.Expr) -> bool:  # Decide whether a factor is definitely never zero.
    simplified = _safe_simplify(expression)  # Simplify the factor before checking nonzero assumptions.
    if _proves_zero(simplified):  # Check whether the factor is actually zero.
        return False  # Report that zero is not nonzero.
    if getattr(simplified, "is_zero", None) is False:  # Use SymPy assumptions to prove nonzero factors such as exp(y).
        return True  # Report a proven nonzero factor.
    return False  # Report that nonzero-ness could not be proven.
