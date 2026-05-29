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
    """Verify YAML structure, symbolic proofs, and calculations from a YAML file path."""
    try:
        with open(file_path, "r", encoding="utf-8") as handle:
            yaml_text = handle.read()
    except Exception as exc:
        return f"Error! YAML file is invalid: line 1: unable to read file: {exc}"

    try:
        ast_lines = _extract_lines(yaml_text)
        loaded = yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        reason = getattr(exc, "problem", str(exc))
        line_number = _line(mark) if mark is not None else 1
        return f"Error! YAML file is invalid: line {line_number}: {reason}"
    except Exception as exc:
        return f"Error! YAML file is invalid: line 1: {exc}"

    if not isinstance(loaded, dict):
        return "Error! YAML file is invalid: line 1: top-level YAML must be a mapping"

    axioms = loaded.get("axioms")
    if not isinstance(axioms, dict):
        top_line = ast_lines["top"].get("axioms", 1)
        return f"Error! YAML file is invalid: line {top_line}: axioms must be a mapping"

    known_equations: list[dict[str, Any]] = []
    known_expressions: list[dict[str, Any]] = []

    for axiom_name, axiom_value in axioms.items():
        axiom_line = ast_lines["axioms"].get(axiom_name, {}).get("_self", ast_lines["top"].get("axioms", 1))
        if not isinstance(axiom_value, dict):
            return f"Error! YAML file is invalid: line {axiom_line}: axiom '{axiom_name}' must be a mapping"
        if "vars" not in axiom_value:
            return f"Error! YAML file is invalid: line {axiom_line}: axiom '{axiom_name}' is missing vars"
        if "equation" not in axiom_value:
            return f"Error! YAML file is invalid: line {axiom_line}: axiom '{axiom_name}' is missing equation"
        vars_line = ast_lines["axioms"].get(axiom_name, {}).get("vars", axiom_line)
        ok, reason = _validate_vars_and_equation(axiom_value.get("vars"), axiom_value.get("equation"), vars_line)
        if not ok:
            return f"Error! YAML file is invalid: {reason}"
        ax_vars = [value.strip() for value in axiom_value["vars"]]
        ax_equation = axiom_value["equation"].strip()
        known_equations.append({"equation": ax_equation, "vars": ax_vars, "line": axiom_line, "source": axiom_name})
        split = _split_equation_sides(ax_equation)
        if split is not None:
            known_expressions.append({"expression": split[0], "vars": ax_vars, "line": axiom_line, "source": axiom_name})
            known_expressions.append({"expression": split[1], "vars": ax_vars, "line": axiom_line, "source": axiom_name})

    for top_key, top_value in loaded.items():
        if top_key in {"axioms", "calculations"}:
            continue
        section_line = ast_lines["top"].get(top_key, 1)
        if not isinstance(top_value, dict):
            return f"Error! YAML file is invalid: line {section_line}: section '{top_key}' must be a mapping"
        if "vars" not in top_value:
            return f"Error! YAML file is invalid: line {section_line}: section '{top_key}' is missing vars"
        if "equation" not in top_value:
            return f"Error! YAML file is invalid: line {section_line}: section '{top_key}' is missing equation"
        vars_line = ast_lines["sections"].get(top_key, {}).get("vars", section_line)
        if not isinstance(top_value.get("vars"), list) or not all(isinstance(item, str) for item in top_value.get("vars", [])):
            return f"Error! YAML file is invalid: line {vars_line}: vars must be a list of strings"
        section_vars = [value.strip() for value in top_value["vars"]]
        equation_block = top_value.get("equation")
        eq_line = ast_lines["sections"].get(top_key, {}).get("equation", section_line)
        if not isinstance(equation_block, str) or not equation_block.strip():
            return f"Error! YAML file is invalid: line {eq_line}: equation must be a non-empty proof block"
        step_lines = [row for row in equation_block.splitlines() if row.strip()]
        if not step_lines:
            return f"Error! YAML file is invalid: line {eq_line}: equation proof block has no steps"
        previous_rhs: str | None = None
        for index, raw_step in enumerate(step_lines):
            step_line = eq_line + index
            clean_step = _strip_inline_comment(raw_step)
            if clean_step.count("->") != 1:
                return f"Error! Math proofs are invalid: line {step_line}: proof step must contain exactly one '->'"
            lhs_text, rhs_text = [part.strip() for part in clean_step.split("->", 1)]
            if not lhs_text or not rhs_text:
                return f"Error! Math proofs are invalid: line {step_line}: proof step sides cannot be empty"
            if index == 0:
                if not _equation_matches_known(lhs_text, section_vars, known_equations):
                    return f"Error! Math proofs are invalid: line {step_line}: first step left-hand side must match an axiom or prior theorem equation"
            else:
                assert previous_rhs is not None
                if not is_equation_equal(section_vars, lhs_text, previous_rhs):
                    return f"Error! Math proofs are invalid: line {step_line}: left-hand side must equal previous step right-hand side"
            if not is_equation_equal(section_vars, lhs_text, rhs_text):
                return f"Error! Math proofs are invalid: line {step_line}: symbolic transformation is not equivalent"
            previous_rhs = rhs_text
            known_equations.append({"equation": rhs_text, "vars": section_vars, "line": step_line, "source": top_key})
            split_rhs = _split_equation_sides(rhs_text)
            if split_rhs is not None:
                known_expressions.append({"expression": split_rhs[0], "vars": section_vars, "line": step_line, "source": top_key})
                known_expressions.append({"expression": split_rhs[1], "vars": section_vars, "line": step_line, "source": top_key})

    calculations = loaded.get("calculations")
    if calculations is not None:
        calc_top_line = ast_lines["top"].get("calculations", 1)
        if not isinstance(calculations, dict):
            return f"Error! YAML file is invalid: line {calc_top_line}: calculations must be a mapping"
        for calc_name, calc_value in calculations.items():
            calc_line = ast_lines["calculations"].get(calc_name, {}).get("_self", calc_top_line)
            if not isinstance(calc_value, dict):
                return f"Error! YAML file is invalid: line {calc_line}: calculation '{calc_name}' must be a mapping"
            required = ["vars", "values", "equation", "tolerance", "expected_value", "expected_symbol"]
            for field in required:
                if field not in calc_value:
                    return f"Error! YAML file is invalid: line {calc_line}: calculation '{calc_name}' is missing {field}"
            vars_list = calc_value["vars"]
            values = calc_value["values"]
            equation = calc_value["equation"]
            tolerance = calc_value["tolerance"]
            expected_value = calc_value["expected_value"]
            expected_symbol = calc_value["expected_symbol"]
            if not isinstance(vars_list, list) or not all(isinstance(item, str) for item in vars_list):
                vars_line = ast_lines["calculations"].get(calc_name, {}).get("vars", calc_line)
                return f"Error! YAML file is invalid: line {vars_line}: calculation vars must be a list of strings"
            if not isinstance(values, list):
                values_line = ast_lines["calculations"].get(calc_name, {}).get("values", calc_line)
                return f"Error! YAML file is invalid: line {values_line}: calculation values must be a list"
            if len(vars_list) != len(values):
                values_line = ast_lines["calculations"].get(calc_name, {}).get("values", calc_line)
                return f"Error! YAML file is invalid: line {values_line}: calculation vars and values length must match"
            if not isinstance(equation, str) or not equation.strip():
                eq_line = ast_lines["calculations"].get(calc_name, {}).get("equation", calc_line)
                return f"Error! YAML file is invalid: line {eq_line}: calculation equation must be a non-empty string"
            if not isinstance(expected_symbol, str) or not expected_symbol.strip():
                sym_line = ast_lines["calculations"].get(calc_name, {}).get("expected_symbol", calc_line)
                return f"Error! YAML file is invalid: line {sym_line}: expected_symbol must be a non-empty string"
            calc_vars = [value.strip() for value in vars_list]
            if not _expression_matches_known(equation.strip(), calc_vars, known_expressions):
                eq_line = ast_lines["calculations"].get(calc_name, {}).get("equation", calc_line)
                return f"Error! Calculations are invalid: line {eq_line}: equation must match an expression from an axiom or theorem"
            if not is_calculation_correct(calc_vars, values, equation, expected_value, tolerance):
                eq_line = ast_lines["calculations"].get(calc_name, {}).get("equation", calc_line)
                return f"Error! Calculations are invalid: line {eq_line}: numeric evaluation does not satisfy expected value within tolerance"

    return "Math proofs are valid"
