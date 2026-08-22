"""A small, safe toolset the Worker agent can invoke.

Kept intentionally minimal for the demo: a calculator and a scratch-note
writer. Add more tools here as functions, then register them in TOOLS below.
"""

from __future__ import annotations

import ast
import operator

_ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.Mod: operator.mod,
}


def _safe_eval(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError(f"Unsupported expression: {ast.dump(node)}")


def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression, e.g. '(3 + 4) * 2'."""
    try:
        tree = ast.parse(expression, mode="eval")
        return str(_safe_eval(tree.body))
    except Exception as exc:  # noqa: BLE001 — surfaced back to the LLM as tool output
        return f"error: {exc}"


_notes: list[str] = []


def write_note(text: str) -> str:
    """Append a scratch note the reviewer/planner can see later this run."""
    _notes.append(text)
    return "note recorded"


def read_notes(_: str = "") -> str:
    """Return all notes recorded so far this run."""
    return "\n".join(_notes) if _notes else "(no notes yet)"


TOOLS = {
    "calculator": calculator,
    "write_note": write_note,
    "read_notes": read_notes,
}

TOOL_DESCRIPTIONS = """Available tools (call by name with a single string argument):
- calculator(expression): evaluate arithmetic, e.g. calculator("12 * (3 + 1)")
- write_note(text): save a short note for later steps to reference
- read_notes(): return all notes saved so far"""
