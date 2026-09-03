"""Renders the real AST produced by parser.py as an indented tree of text
lines, for display in tooling/UIs. Purely a formatter — does not alter
or reinterpret the tree in any way."""

from parser import (
    Program, VarDecl, Assign, Print, If, While, Block, BinOp, UnaryOp, Literal, VarRef
)


def render(node, prefix="", is_last=True, is_root=True):
    lines = []
    connector = "" if is_root else ("└── " if is_last else "├── ")
    lines.append(prefix + connector + _label(node))

    child_prefix = prefix if is_root else prefix + ("    " if is_last else "│   ")
    children = _children(node)
    for i, child in enumerate(children):
        lines.extend(render(child, child_prefix, i == len(children) - 1, is_root=False))
    return lines


def _label(node):
    if isinstance(node, Program):
        return "Program"
    if isinstance(node, VarDecl):
        return f"VarDecl ({node.var_type} {node.name}) [line {node.line}]"
    if isinstance(node, Assign):
        return f"Assign ({node.name}) [line {node.line}]"
    if isinstance(node, Print):
        return f"Print [line {node.line}]"
    if isinstance(node, If):
        return f"If [line {node.line}]"
    if isinstance(node, While):
        return f"While [line {node.line}]"
    if isinstance(node, Block):
        return "Block"
    if isinstance(node, BinOp):
        return f"BinOp ({node.op}) [line {node.line}]"
    if isinstance(node, UnaryOp):
        return f"UnaryOp ({node.op}) [line {node.line}]"
    if isinstance(node, Literal):
        return f"Literal ({node.kind}: {node.value!r}) [line {node.line}]"
    if isinstance(node, VarRef):
        return f"VarRef ({node.name}) [line {node.line}]"
    return type(node).__name__


def _children(node):
    if isinstance(node, Program):
        return list(node.statements)
    if isinstance(node, VarDecl):
        return [node.expr] if node.expr is not None else []
    if isinstance(node, Assign):
        return [node.expr]
    if isinstance(node, Print):
        return [node.expr]
    if isinstance(node, If):
        kids = [node.cond, node.then_block]
        if node.else_block is not None:
            kids.append(node.else_block)
        return kids
    if isinstance(node, While):
        return [node.cond, node.block]
    if isinstance(node, Block):
        return list(node.statements)
    if isinstance(node, BinOp):
        return [node.left, node.right]
    if isinstance(node, UnaryOp):
        return [node.expr]
    return []


def render_program(program):
    return "\n".join(render(program))


def find_ast_nodes_for_line(node, target_line):
    """Finds all AST nodes associated with a specific line number."""
    matches = []
    if getattr(node, "line", None) == target_line:
        matches.append(node)
    for child in _children(node):
        matches.extend(find_ast_nodes_for_line(child, target_line))
    return matches
