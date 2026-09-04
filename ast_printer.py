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


def get_all_ast_nodes(node):
    """Returns a flat list of all AST node objects in pre-order traversal."""
    nodes = []
    if node is not None:
        nodes.append(node)
        for child in _children(node):
            nodes.extend(get_all_ast_nodes(child))
    return nodes


def explain_ast_node(node):
    """Returns educational metadata dictionary explaining an AST node."""
    if node is None:
        return {}
    line = getattr(node, "line", None)
    line_str = f"Line {line}" if line else "Program Level"

    if isinstance(node, Program):
        return {
            "type": "Program (Root)",
            "label": "Program",
            "line": line_str,
            "meaning": "The root node of the AST containing all statements in the program.",
            "source": "Entire Source Program"
        }
    if isinstance(node, VarDecl):
        init_str = " (uninitialized)" if node.expr is None else ""
        return {
            "type": "Variable Declaration (VarDecl)",
            "label": f"VarDecl: {node.var_type} {node.name}{init_str}",
            "line": line_str,
            "meaning": f"Declares a variable '{node.name}' of type '{node.var_type}' in the current scope.",
            "source": f"{node.var_type} {node.name} ...;"
        }
    if isinstance(node, Assign):
        return {
            "type": "Assignment Statement (Assign)",
            "label": f"Assign: {node.name} =",
            "line": line_str,
            "meaning": f"Evaluates the right-hand side expression and assigns the result to variable '{node.name}'.",
            "source": f"{node.name} = ...;"
        }
    if isinstance(node, Print):
        return {
            "type": "Print Output Statement (Print)",
            "label": "Print Statement",
            "line": line_str,
            "meaning": "Evaluates the enclosed expression and prints the formatted result to stdout console.",
            "source": "print(...);"
        }
    if isinstance(node, If):
        else_str = " with Else block" if node.else_block else ""
        return {
            "type": "Conditional Branch (If)",
            "label": f"If Statement{else_str}",
            "line": line_str,
            "meaning": "Evaluates condition expression; executes Then-block if true, or Else-block if false.",
            "source": "if (...) { ... }"
        }
    if isinstance(node, While):
        return {
            "type": "Loop Control Statement (While)",
            "label": "While Loop",
            "line": line_str,
            "meaning": "Repeatedly evaluates condition expression and executes body block as long as condition remains true.",
            "source": "while (...) { ... }"
        }
    if isinstance(node, Block):
        return {
            "type": "Block Scope (Block)",
            "label": "Block Scope { ... }",
            "line": line_str,
            "meaning": "Creates a local lexical scope frame containing zero or more nested statements.",
            "source": "{ ... }"
        }
    if isinstance(node, BinOp):
        return {
            "type": "Binary Expression (BinOp)",
            "label": f"BinOp: {node.op}",
            "line": line_str,
            "meaning": f"Performs binary operation '{node.op}' between left and right sub-expression values.",
            "source": f"left {node.op} right"
        }
    if isinstance(node, UnaryOp):
        return {
            "type": "Unary Expression (UnaryOp)",
            "label": f"UnaryOp: {node.op}",
            "line": line_str,
            "meaning": f"Applies unary operator '{node.op}' to child sub-expression.",
            "source": f"{node.op} expr"
        }
    if isinstance(node, Literal):
        return {
            "type": f"Literal Value ({node.kind})",
            "label": f"Literal: {node.value!r} ({node.kind})",
            "line": line_str,
            "meaning": f"Constant literal value of type '{node.kind}'.",
            "source": str(node.value)
        }
    if isinstance(node, VarRef):
        return {
            "type": "Variable Reference (VarRef)",
            "label": f"VarRef: {node.name}",
            "line": line_str,
            "meaning": f"References value stored in variable '{node.name}', resolved via Symbol Table lookup.",
            "source": node.name
        }
    return {"type": type(node).__name__, "label": _label(node), "line": line_str, "meaning": "AST Node", "source": ""}

