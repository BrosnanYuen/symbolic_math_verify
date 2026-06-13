"""Validate YAML-encoded symbolic math axioms, proofs, and calculations."""

from __future__ import annotations

import re
from typing import Any

import yaml

from .check_calculation import is_calculation_correct
from .check_util import _build_parse_locals
from .check_util import _build_symbol_map
from .check_util import _parse_equation
from .check_util import _parse_expression
from .check_util import is_equation_equal


def _line(mark: Any) -> int:
    """Return a 1-based line number from a PyYAML mark-like object."""
    return int(getattr(mark, "line", 0)) + 1


def _strip_inline_comment(value: str) -> str:
    """Strip YAML-style inline comments from a proof step side."""
    return value.split("#", 1)[0].strip()


def _extract_lines(yaml_text: str) -> dict[str, Any]:
    """Collect key line numbers from the YAML AST for precise diagnostics."""
    root = yaml.compose(yaml_text)
    lines: dict[str, Any] = {"top": {}, "axioms": {}, "sections": {}, "calculations": {}}
    if root is None or not isinstance(root, yaml.nodes.MappingNode):
        return lines
    for top_key_node, top_value_node in root.value:
        top_key = top_key_node.value
        lines["top"][top_key] = _line(top_key_node.start_mark)
        if top_key == "axioms" and isinstance(top_value_node, yaml.nodes.MappingNode):
            for ax_key_node, ax_val_node in top_value_node.value:
                ax_name = ax_key_node.value
                ax_lines: dict[str, int] = {"_self": _line(ax_key_node.start_mark)}
                if isinstance(ax_val_node, yaml.nodes.MappingNode):
                    for k_node, _v_node in ax_val_node.value:
                        ax_lines[k_node.value] = _line(k_node.start_mark)
                lines["axioms"][ax_name] = ax_lines
        elif top_key == "calculations" and isinstance(top_value_node, yaml.nodes.MappingNode):
            for calc_key_node, calc_val_node in top_value_node.value:
                calc_name = calc_key_node.value
                calc_lines: dict[str, int] = {"_self": _line(calc_key_node.start_mark)}
                if isinstance(calc_val_node, yaml.nodes.MappingNode):
                    for k_node, _v_node in calc_val_node.value:
                        calc_lines[k_node.value] = _line(k_node.start_mark)
                lines["calculations"][calc_name] = calc_lines
        elif isinstance(top_value_node, yaml.nodes.MappingNode):
            sec_lines: dict[str, int] = {"_self": _line(top_key_node.start_mark)}
            for k_node, _v_node in top_value_node.value:
                sec_lines[k_node.value] = _line(k_node.start_mark)
            lines["sections"][top_key] = sec_lines
    return lines


def _validate_vars_and_equation(vars_list: Any, equation: Any, line_number: int) -> tuple[bool, str]:
    """Validate section vars/equation schema and SymPy compatibility constraints."""
    if not isinstance(vars_list, list) or not all(isinstance(item, str) for item in vars_list):
        return False, f"line {line_number}: vars must be a list of strings"
    if not isinstance(equation, str) or not equation.strip():
        return False, f"line {line_number}: equation must be a non-empty string"
    try:
        symbol_map = _build_symbol_map(vars_list)
        parse_locals = _build_parse_locals(symbol_map)
        parsed = _parse_equation(equation, parse_locals)
        if parsed is None:
            return False, f"line {line_number}: equation is not a valid SymPy equation"
        used = {symbol.name for symbol in parsed.free_symbols}
        declared = {value.strip() for value in vars_list}
        missing = sorted(used - declared)
        extra = sorted(declared - used)
        if missing:
            return False, f"line {line_number}: vars missing symbols used by equation: {missing}"
        if extra:
            return False, f"line {line_number}: vars include unused symbols: {extra}"
    except Exception as exc:
        return False, f"line {line_number}: equation validation failed: {exc}"
    return True, ""


def _split_equation_sides(equation: str) -> tuple[str, str] | None:
    """Split an equation into left/right sides when exactly one equals exists."""
    if equation.count("=") != 1:
        return None
    left, right = equation.split("=", 1)
    left_clean = left.strip()
    right_clean = right.strip()
    if not left_clean or not right_clean:
        return None
    return left_clean, right_clean


def _union_vars(lhs: list[str], rhs: list[str]) -> list[str]:
    """Build an ordered union of symbol names used for cross-section equation checks."""
    out: list[str] = []
    seen: set[str] = set()
    for name in lhs + rhs:
        if name not in seen:
            seen.add(name)
            out.append(name)
    return out


def _equation_matches_known(candidate: str, candidate_vars: list[str], known_equations: list[dict[str, Any]]) -> bool:
    """Return True when candidate equation matches a known equation by symbolic equivalence."""
    for known in known_equations:
        combined = _union_vars(candidate_vars, known["vars"])
        if is_equation_equal(combined, candidate, known["equation"]):
            return True
    return False


def _expression_matches_known(candidate: str, candidate_vars: list[str], known_expressions: list[dict[str, Any]]) -> bool:
    """Return True when candidate expression matches a known expression by symbolic equivalence."""
    for known in known_expressions:
        combined = _union_vars(candidate_vars, known["vars"])
        if is_equation_equal(combined, f"({candidate}) = ({known['expression']})", "0 = 0"):
            return True
    return False


def verify_yaml_file(file_path: str) -> str:
    """Verify YAML structure, symbolic proofs, and calculations from a YAML file path."""  # Document the public YAML verification entry point.
    from .check_substitution import is_substitution_correct  # Import substitution checking locally so this new feature stays scoped to this function.
    from .check_subscript_substitution import is_subscript_substitution_correct  # Import subscript substitution checking locally so colon proof steps stay scoped to this function.

    def _remember_known_equation(equation_text: str, equation_vars: list[str], line_number: int, source_name: str) -> None:  # Record equations and their sides for later theorem and calculation checks.
        known_equations.append({"equation": equation_text, "vars": equation_vars, "line": line_number, "source": source_name})  # Store the full equation so later proof steps can reference it.
        split_equation = _split_equation_sides(equation_text)  # Split the equation when possible so calculations can reference either side as an expression.
        if split_equation is None:  # Skip expression-side tracking for strings that are not simple single-equals equations.
            return  # Exit early because there are no individual equation sides to store.
        left_text, right_text = split_equation  # Unpack the left and right equation sides for expression tracking.
        known_expressions.append({"expression": left_text, "vars": equation_vars, "line": line_number, "source": source_name})  # Store the left side as a known expression.
        known_expressions.append({"expression": right_text, "vars": equation_vars, "line": line_number, "source": source_name})  # Store the right side as a known expression.

    try:  # Convert file-read failures into the public invalid-YAML result shape.
        with open(file_path, "r", encoding="utf-8") as handle:  # Open the YAML file as UTF-8 text.
            yaml_text = handle.read()  # Read the whole YAML document so we can parse it and recover line numbers.
    except Exception as exc:  # Catch file-system and decoding failures.
        return f"Error! YAML file is invalid: line 1: unable to read file: {exc}"  # Report file-read failures as invalid YAML at line 1.

    try:  # Parse both the YAML AST and the loaded data structure.
        ast_lines = _extract_lines(yaml_text)  # Extract YAML line-number metadata before semantic validation.
        loaded = yaml.safe_load(yaml_text)  # Load the YAML content into Python data structures.
    except yaml.YAMLError as exc:  # Catch YAML syntax and structure parser errors.
        mark = getattr(exc, "problem_mark", None)  # Recover the parser location when PyYAML provides one.
        reason = getattr(exc, "problem", str(exc))  # Prefer PyYAML's concise parser error message when available.
        line_number = _line(mark) if mark is not None else 1  # Convert the YAML parser location into a 1-based line number.
        return f"Error! YAML file is invalid: line {line_number}: {reason}"  # Report YAML syntax errors with the exact parser line.
    except Exception as exc:  # Catch unexpected loader failures.
        return f"Error! YAML file is invalid: line 1: {exc}"  # Report unexpected parse failures as invalid YAML.

    if not isinstance(loaded, dict):  # Require the top-level YAML document to be a mapping.
        return "Error! YAML file is invalid: line 1: top-level YAML must be a mapping"  # Reject non-mapping YAML documents.

    axioms = loaded.get("axioms")  # Extract the required axioms block from the loaded YAML.
    if not isinstance(axioms, dict):  # Require axioms to be present as a mapping.
        top_line = ast_lines["top"].get("axioms", 1)  # Recover the best available line number for the axioms key.
        return f"Error! YAML file is invalid: line {top_line}: axioms must be a mapping"  # Reject missing or malformed axioms blocks.

    known_equations: list[dict[str, Any]] = []  # Track axioms and proven theorem results that later steps may reference.
    known_expressions: list[dict[str, Any]] = []  # Track equation sides that later calculations may reference.

    for axiom_name, axiom_value in axioms.items():  # Validate each declared axiom and add it to the known-equation pool.
        axiom_line = ast_lines["axioms"].get(axiom_name, {}).get("_self", ast_lines["top"].get("axioms", 1))  # Recover the best available line number for this axiom.
        if not isinstance(axiom_value, dict):  # Require each axiom entry to be a mapping.
            return f"Error! YAML file is invalid: line {axiom_line}: axiom '{axiom_name}' must be a mapping"  # Reject non-mapping axiom entries.
        if "vars" not in axiom_value:  # Require every axiom to declare its symbol list.
            return f"Error! YAML file is invalid: line {axiom_line}: axiom '{axiom_name}' is missing vars"  # Report missing axiom vars.
        if "equation" not in axiom_value:  # Require every axiom to declare its equation text.
            return f"Error! YAML file is invalid: line {axiom_line}: axiom '{axiom_name}' is missing equation"  # Report missing axiom equations.
        vars_line = ast_lines["axioms"].get(axiom_name, {}).get("vars", axiom_line)  # Recover the best available line number for the vars field.
        ok, reason = _validate_vars_and_equation(axiom_value.get("vars"), axiom_value.get("equation"), vars_line)  # Reuse the shared axiom-equation validator.
        if not ok:  # Stop immediately when an axiom fails schema or SymPy validation.
            return f"Error! YAML file is invalid: {reason}"  # Surface the exact validation reason and line number.
        ax_vars = [value.strip() for value in axiom_value["vars"]]  # Normalize axiom symbol names by trimming whitespace.
        ax_equation = axiom_value["equation"].strip()  # Normalize the axiom equation text before storing it.
        _remember_known_equation(ax_equation, ax_vars, axiom_line, axiom_name)  # Make the validated axiom available to later proofs and calculations.

    for top_key, top_value in loaded.items():  # Validate every theorem/proof section after axioms have been collected.
        if top_key in {"axioms", "calculations"}:  # Skip the non-proof top-level sections handled elsewhere.
            continue  # Move on to the next top-level YAML entry.
        section_line = ast_lines["top"].get(top_key, 1)  # Recover the best available line number for this section.
        if not isinstance(top_value, dict):  # Require each theorem/proof section to be a mapping.
            return f"Error! YAML file is invalid: line {section_line}: section '{top_key}' must be a mapping"  # Reject non-mapping theorem sections.
        if "vars" not in top_value:  # Require every theorem/proof section to declare its symbols.
            return f"Error! YAML file is invalid: line {section_line}: section '{top_key}' is missing vars"  # Report missing theorem vars.
        if "equation" not in top_value:  # Require every theorem/proof section to declare its proof block.
            return f"Error! YAML file is invalid: line {section_line}: section '{top_key}' is missing equation"  # Report missing theorem equation blocks.
        vars_line = ast_lines["sections"].get(top_key, {}).get("vars", section_line)  # Recover the best available line number for the theorem vars field.
        if not isinstance(top_value.get("vars"), list) or not all(isinstance(item, str) for item in top_value.get("vars", [])):  # Require theorem vars to be a list of strings.
            return f"Error! YAML file is invalid: line {vars_line}: vars must be a list of strings"  # Reject malformed theorem vars declarations.
        section_vars = [value.strip() for value in top_value["vars"]]  # Normalize theorem symbol names by trimming whitespace.
        equation_block = top_value.get("equation")  # Extract the proof block text for this theorem.
        eq_line = ast_lines["sections"].get(top_key, {}).get("equation", section_line)  # Recover the best available line number for the proof block.
        if not isinstance(equation_block, str) or not equation_block.strip():  # Require a non-empty proof block string.
            return f"Error! YAML file is invalid: line {eq_line}: equation must be a non-empty proof block"  # Reject empty or non-string proof blocks.
        step_lines = [row for row in equation_block.splitlines() if row.strip()]  # Keep only non-empty proof-step lines from the block scalar.
        if not step_lines:  # Guard against proof blocks that contain only blank lines.
            return f"Error! YAML file is invalid: line {eq_line}: equation proof block has no steps"  # Reject proof blocks with no usable steps.
        previous_rhs: str | None = None  # Track the previous step result for proof chaining within this section.
        for index, raw_step in enumerate(step_lines):  # Validate each proof step in order.
            step_line = eq_line + index  # Map the proof-step index back to its YAML line number.
            clean_step = _strip_inline_comment(raw_step)  # Remove any trailing YAML-style inline comment from the proof line.
            if clean_step.count("->") != 1:  # Require every proof step to contain exactly one transformation arrow.
                return f"Error! Math proofs are invalid: line {step_line}: proof step must contain exactly one '->'"  # Reject malformed transformation syntax.
            step_left, rhs_text = [part.strip() for part in clean_step.split("->", 1)]  # Split the proof line into its left input and right output equations.
            if not rhs_text:  # Require the proof step to provide a non-empty result equation.
                return f"Error! Math proofs are invalid: line {step_line}: proof step right-hand side cannot be empty"  # Reject proof steps that omit the result equation.
            semicolon_count = step_left.count(";")  # Count ordinary substitution markers so malformed steps can be rejected precisely.
            colon_count = step_left.count(":")  # Count subscript substitution markers so malformed steps can be rejected precisely.
            if semicolon_count > 1:  # Allow at most one explicit ordinary substitution marker per proof step.
                return f"Error! Math proofs are invalid: line {step_line}: proof step can contain at most one ';' substitution marker"  # Reject ambiguous multi-substitution step syntax.
            if colon_count > 1:  # Allow at most one explicit subscript substitution marker per proof step.
                return f"Error! Math proofs are invalid: line {step_line}: proof step can contain at most one ':' subscript substitution marker"  # Reject ambiguous multi-subscript step syntax.
            if semicolon_count and colon_count:  # Disallow mixing ordinary substitution and subscript substitution in the same step.
                return f"Error! Math proofs are invalid: line {step_line}: proof step cannot mix ';' and ':' substitution markers"  # Reject ambiguous mixed substitution syntax.
            substitution_text: str | None = None  # Default to ordinary substitution being absent unless a semicolon marker is present.
            subscript_text: str | None = None  # Default to subscript substitution being absent unless a colon marker is present.
            lhs_text = step_left  # Start with the whole left side and refine it if a substitution marker exists.
            if ";" in step_left:  # Handle proof steps that explicitly request ordinary substitution checking.
                lhs_text, substitution_text = [part.strip() for part in step_left.split(";", 1)]  # Split the step into the source equation and the substitution equation.
                if not lhs_text:  # Require the source equation before the substitution marker.
                    return f"Error! Math proofs are invalid: line {step_line}: substitution source equation cannot be empty"  # Reject proof steps that start with a bare semicolon.
                if not substitution_text:  # Require the substitution equation after the substitution marker.
                    return f"Error! Math proofs are invalid: line {step_line}: substitution equation cannot be empty"  # Reject proof steps that omit the substitution equation.
            elif ":" in step_left:  # Handle proof steps that explicitly request subscript substitution checking.
                lhs_text, subscript_text = [part.strip() for part in step_left.split(":", 1)]  # Split the step into the source equation and the requested subscript suffix.
                if not lhs_text:  # Require the source equation before the subscript marker.
                    return f"Error! Math proofs are invalid: line {step_line}: subscript substitution source equation cannot be empty"  # Reject proof steps that start with a bare colon.
                if not subscript_text:  # Require the subscript suffix after the subscript marker.
                    return f"Error! Math proofs are invalid: line {step_line}: subscript substitution suffix cannot be empty"  # Reject proof steps that omit the requested subscript suffix.
            elif not lhs_text:  # Require ordinary proof steps to provide a non-empty input equation.
                return f"Error! Math proofs are invalid: line {step_line}: proof step left-hand side cannot be empty"  # Reject proof steps that omit the input equation.
            if index == 0:  # The first step must start from an axiom or a previously proven theorem.
                if not _equation_matches_known(lhs_text, section_vars, known_equations):  # Compare the first step input against the known-equation pool.
                    return f"Error! Math proofs are invalid: line {step_line}: first step left-hand side must match an axiom or prior theorem equation"  # Reject theorems that start from an unknown equation.
            else:  # All later steps must continue from the previous step result.
                assert previous_rhs is not None  # Keep the type checker aligned with the proof-step sequencing logic.
                if not is_equation_equal(section_vars, lhs_text, previous_rhs):  # Require the next step input to match the previous step output.
                    return f"Error! Math proofs are invalid: line {step_line}: left-hand side must equal previous step right-hand side"  # Reject broken proof chains.
            if substitution_text is not None:  # Use substitution checking only when the step explicitly uses ';'.
                if not _equation_matches_known(substitution_text, section_vars, known_equations):  # Require the substitution equation to come from axioms or prior theorems.
                    return f"Error! Math proofs are invalid: line {step_line}: substitution equation must match an axiom or prior theorem equation"  # Reject substitutions based on unknown relations.
                if not is_substitution_correct(section_vars, lhs_text, substitution_text, rhs_text):  # Delegate the mathematical substitution proof to the existing substitution checker.
                    return f"Error! Math proofs are invalid: line {step_line}: substitution is not correct"  # Reject incorrect substitution steps.
            elif subscript_text is not None:  # Use subscript substitution checking only when the step explicitly uses ':'.
                try:  # Parse the source equation so the subscript checker receives only the original symbols that actually appear before substitution.
                    section_symbol_map = _build_symbol_map(section_vars)  # Build parser symbols from the theorem's declared variable list.
                    section_parse_locals = _build_parse_locals(section_symbol_map)  # Build the parser namespace needed to read the source equation.
                    lhs_residual = _parse_equation(lhs_text, section_parse_locals)  # Parse the source equation so we can inspect the original free symbols it uses.
                except Exception:  # Treat parser failures inside subscript steps as invalid proof syntax rather than raising.
                    lhs_residual = None  # Fall back to a None sentinel so the next guard can report a precise proof error.
                if lhs_residual is None:  # Reject subscript steps whose source equation cannot be parsed as a SymPy equation.
                    return f"Error! Math proofs are invalid: line {step_line}: subscript substitution source equation is not a valid SymPy equation"  # Report an explicit parse failure for the colon step source equation.
                lhs_symbol_names = {symbol.name for symbol in lhs_residual.free_symbols}  # Collect the unsuffixed symbols that actually appear in the source equation.
                original_symbol_names = [symbol_name for symbol_name in section_vars if symbol_name in lhs_symbol_names]  # Preserve section order while passing only the original source-equation symbols to the checker.
                if not is_subscript_substitution_correct(original_symbol_names, lhs_text, subscript_text, rhs_text):  # Delegate the mathematical subscript substitution proof to the dedicated checker with only the pre-substitution symbols.
                    return f"Error! Math proofs are invalid: line {step_line}: subscript substitution is not correct"  # Reject incorrect subscript substitution steps.
            elif not is_equation_equal(section_vars, lhs_text, rhs_text):  # Preserve ordinary symbolic-equivalence checking for non-substitution steps.
                return f"Error! Math proofs are invalid: line {step_line}: symbolic transformation is not equivalent"  # Reject invalid non-substitution proof steps.
            previous_rhs = rhs_text  # Advance the proof chain to the current step result.
            _remember_known_equation(rhs_text, section_vars, step_line, top_key)  # Make the newly proven equation available to later sections and calculations.

    calculations = loaded.get("calculations")  # Extract the optional calculations block after theorem validation.
    if calculations is not None:  # Validate calculations only when the YAML file declares them.
        calc_top_line = ast_lines["top"].get("calculations", 1)  # Recover the best available line number for the calculations key.
        if not isinstance(calculations, dict):  # Require calculations to be a mapping when present.
            return f"Error! YAML file is invalid: line {calc_top_line}: calculations must be a mapping"  # Reject non-mapping calculations blocks.
        for calc_name, calc_value in calculations.items():  # Validate each named calculation entry.
            calc_line = ast_lines["calculations"].get(calc_name, {}).get("_self", calc_top_line)  # Recover the best available line number for this calculation.
            if not isinstance(calc_value, dict):  # Require each calculation entry to be a mapping.
                return f"Error! YAML file is invalid: line {calc_line}: calculation '{calc_name}' must be a mapping"  # Reject non-mapping calculation entries.
            required = ["vars", "values", "equation", "tolerance", "expected_value", "expected_symbol"]  # Define the required calculation fields.
            for field in required:  # Check every required calculation field.
                if field not in calc_value:  # Stop immediately when a required field is missing.
                    return f"Error! YAML file is invalid: line {calc_line}: calculation '{calc_name}' is missing {field}"  # Report the missing calculation field.
            vars_list = calc_value["vars"]  # Extract the calculation symbol list for validation.
            values = calc_value["values"]  # Extract the numeric substitution values for validation.
            equation = calc_value["equation"]  # Extract the calculation expression/equation text.
            tolerance = calc_value["tolerance"]  # Extract the numeric tolerance for result comparison.
            expected_value = calc_value["expected_value"]  # Extract the expected numeric result for validation.
            expected_symbol = calc_value["expected_symbol"]  # Extract the label for the expected computed symbol.
            if not isinstance(vars_list, list) or not all(isinstance(item, str) for item in vars_list):  # Require calculation vars to be a list of strings.
                vars_line = ast_lines["calculations"].get(calc_name, {}).get("vars", calc_line)  # Recover the best available line number for the vars field.
                return f"Error! YAML file is invalid: line {vars_line}: calculation vars must be a list of strings"  # Reject malformed calculation vars.
            if not isinstance(values, list):  # Require calculation values to be a list.
                values_line = ast_lines["calculations"].get(calc_name, {}).get("values", calc_line)  # Recover the best available line number for the values field.
                return f"Error! YAML file is invalid: line {values_line}: calculation values must be a list"  # Reject malformed calculation values.
            if len(vars_list) != len(values):  # Require the vars and values lists to have matching lengths.
                values_line = ast_lines["calculations"].get(calc_name, {}).get("values", calc_line)  # Recover the best available line number for the values field.
                return f"Error! YAML file is invalid: line {values_line}: calculation vars and values length must match"  # Reject mismatched calculation arity.
            if not isinstance(equation, str) or not equation.strip():  # Require a non-empty calculation expression string.
                eq_line = ast_lines["calculations"].get(calc_name, {}).get("equation", calc_line)  # Recover the best available line number for the equation field.
                return f"Error! YAML file is invalid: line {eq_line}: calculation equation must be a non-empty string"  # Reject empty calculation equations.
            if not isinstance(expected_symbol, str) or not expected_symbol.strip():  # Require a non-empty expected_symbol label.
                sym_line = ast_lines["calculations"].get(calc_name, {}).get("expected_symbol", calc_line)  # Recover the best available line number for the expected_symbol field.
                return f"Error! YAML file is invalid: line {sym_line}: expected_symbol must be a non-empty string"  # Reject empty expected_symbol labels.
            calc_vars = [value.strip() for value in vars_list]  # Normalize calculation symbol names by trimming whitespace.
            if not _expression_matches_known(equation.strip(), calc_vars, known_expressions):  # Require the calculation expression to come from a known axiom or theorem side.
                eq_line = ast_lines["calculations"].get(calc_name, {}).get("equation", calc_line)  # Recover the best available line number for the equation field.
                return f"Error! Calculations are invalid: line {eq_line}: equation must match an expression from an axiom or theorem"  # Reject calculations based on unknown expressions.
            if not is_calculation_correct(calc_vars, values, equation, expected_value, tolerance):  # Reuse the existing numeric calculation checker.
                eq_line = ast_lines["calculations"].get(calc_name, {}).get("equation", calc_line)  # Recover the best available line number for the equation field.
                return f"Error! Calculations are invalid: line {eq_line}: numeric evaluation does not satisfy expected value within tolerance"  # Reject incorrect calculation results.

    return "Math proofs are valid"  # Report success only after YAML structure, proofs, and calculations all validate.
