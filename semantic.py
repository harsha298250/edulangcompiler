"""
Semantic analyzer for EduLang.
Walks the AST built by the parser, tracks a symbol table per scope hierarchy, and
collects semantic errors: undeclared variables, redeclarations, type mismatches,
and invalid condition types.
"""

from parser import (
    VarDecl, Assign, Print, If, While, Block, BinOp, UnaryOp, Literal, VarRef
)


class SemError:
    def __init__(self, code, line, technical, context=None):
        self.phase = "Semantic"
        self.code = code
        self.line = line
        self.technical = technical
        self.context = context or {}


NUMERIC = {"int", "float"}


class Scope:
    """A single lexical scope carrying declared variables, linked to parent and children."""
    def __init__(self, name="Global Scope", parent=None):
        self.name = name
        self.vars = {}
        self.parent = parent
        self.children = []
        if parent:
            parent.children.append(self)

    def declare(self, name, type_):
        self.vars[name] = type_

    def resolve(self, name):
        scope = self
        while scope:
            if name in scope.vars:
                return scope.vars[name]
            scope = scope.parent
        return None

    def resolve_with_trace(self, name):
        """Resolves a variable while recording the scope traversal lookup path."""
        steps = []
        scope = self
        found_type = None
        while scope:
            found_here = name in scope.vars
            if found_here:
                found_type = scope.vars[name]
                steps.append({
                    "scope": scope.name,
                    "found": True,
                    "type": found_type,
                    "msg": f"Searching '{scope.name}'... Found variable '{name}' of type '{found_type}'!"
                })
                break
            else:
                steps.append({
                    "scope": scope.name,
                    "found": False,
                    "type": None,
                    "msg": f"Searching '{scope.name}'... Variable '{name}' not declared here. Checking parent scope..."
                })
            scope = scope.parent
        if not found_type and steps and not steps[-1]["found"]:
            steps.append({
                "scope": "Root",
                "found": False,
                "type": None,
                "msg": f"Lookup failed: Variable '{name}' is undeclared in all active scope levels."
            })
        return found_type, steps

    def declared_here(self, name):
        return name in self.vars

    def all_declared_vars(self):
        result = set()
        scope = self
        while scope:
            result.update(scope.vars.keys())
            scope = scope.parent
        return sorted(list(result))


def find_shadowed_variables(scope):
    """Finds all variable shadowing instances across a scope hierarchy."""
    shadowed = []
    if scope is None:
        return shadowed

    def _traverse(curr_scope):
        for var_name, var_type in curr_scope.vars.items():
            parent = curr_scope.parent
            while parent:
                if var_name in parent.vars:
                    shadowed.append({
                        "var_name": var_name,
                        "inner_scope": curr_scope.name,
                        "outer_scope": parent.name,
                        "type": var_type
                    })
                    break
                parent = parent.parent
        for child in curr_scope.children:
            _traverse(child)

    _traverse(scope)
    return shadowed



def render_scope_tree(scope, prefix="", is_last=True, is_root=True):
    """Renders hierarchical tree view of global and block scopes accurately."""
    lines = []
    header = scope.name if is_root else (("└── " if is_last else "├── ") + scope.name)
    lines.append(prefix + header)

    child_prefix = prefix if is_root else prefix + ("    " if is_last else "│   ")

    items = list(scope.vars.items())
    total_children = len(items) + len(scope.children)
    curr_idx = 0

    for var_name, var_type in items:
        curr_idx += 1
        is_last_item = (curr_idx == total_children)
        conn = "└── " if is_last_item else "├── "
        lines.append(child_prefix + conn + f"{var_name} : {var_type}")

    for child in scope.children:
        curr_idx += 1
        is_last_item = (curr_idx == total_children)
        sub_lines = render_scope_tree(child, child_prefix, is_last=is_last_item, is_root=False)
        lines.extend(sub_lines.split("\n"))

    return "\n".join(lines)


class SemanticAnalyzer:
    def __init__(self, program):
        self.program = program
        self.errors = []
        self.global_scope = None

    def analyze(self):
        self.global_scope = Scope("Global Scope")
        self.visit_block_stmts(self.program.statements, self.global_scope)
        return self.errors

    def visit_block_stmts(self, statements, scope):
        for stmt in statements:
            self.visit_stmt(stmt, scope)

    def visit_stmt(self, stmt, scope):
        if isinstance(stmt, VarDecl):
            already_declared = scope.declared_here(stmt.name)
            if already_declared:
                self.errors.append(SemError(
                    "SEM002", stmt.line,
                    f"Variable '{stmt.name}' is already declared in this scope",
                    {"name": stmt.name}
                ))
            expr_type = None
            if stmt.expr is not None:
                expr_type = self.visit_expr(stmt.expr, scope)
            if not already_declared:
                scope.declare(stmt.name, stmt.var_type)
            if stmt.expr is not None:
                self.check_assign_compat(stmt.var_type, expr_type, stmt.name, stmt.line)

        elif isinstance(stmt, Assign):
            declared_type = scope.resolve(stmt.name)
            if declared_type is None:
                self.errors.append(SemError(
                    "SEM001", stmt.line,
                    f"Variable '{stmt.name}' is used but was never declared",
                    {"name": stmt.name, "declared_vars": scope.all_declared_vars()}
                ))
            expr_type = self.visit_expr(stmt.expr, scope)
            if declared_type is not None:
                self.check_assign_compat(declared_type, expr_type, stmt.name, stmt.line)

        elif isinstance(stmt, Print):
            self.visit_expr(stmt.expr, scope)

        elif isinstance(stmt, If):
            cond_type = self.visit_expr(stmt.cond, scope)
            self.check_condition_type(cond_type, stmt.line)
            then_scope = Scope(f"If-Then Scope (Line {stmt.line})", parent=scope)
            if isinstance(stmt.then_block, Block):
                self.visit_block_stmts(stmt.then_block.statements, then_scope)
            else:
                self.visit_stmt(stmt.then_block, then_scope)

            if stmt.else_block is not None:
                else_scope = Scope(f"If-Else Scope (Line {stmt.line})", parent=scope)
                if isinstance(stmt.else_block, Block):
                    self.visit_block_stmts(stmt.else_block.statements, else_scope)
                else:
                    self.visit_stmt(stmt.else_block, else_scope)

        elif isinstance(stmt, While):
            cond_type = self.visit_expr(stmt.cond, scope)
            self.check_condition_type(cond_type, stmt.line)
            while_scope = Scope(f"While Loop Scope (Line {stmt.line})", parent=scope)
            if isinstance(stmt.block, Block):
                self.visit_block_stmts(stmt.block.statements, while_scope)
            else:
                self.visit_stmt(stmt.block, while_scope)

        elif isinstance(stmt, Block):
            first_line = getattr(stmt, "line", None)
            if first_line is None and stmt.statements:
                first_line = getattr(stmt.statements[0], "line", None)
            line_str = f"Line {first_line}" if first_line is not None else "Block"
            block_scope = Scope(f"Block Scope ({line_str})", parent=scope)
            self.visit_block_stmts(stmt.statements, block_scope)

    def visit_expr(self, expr, scope):
        if isinstance(expr, Literal):
            return expr.kind

        if isinstance(expr, VarRef):
            t = scope.resolve(expr.name)
            if t is None:
                self.errors.append(SemError(
                    "SEM001", expr.line,
                    f"Variable '{expr.name}' is used but was never declared",
                    {"name": expr.name, "declared_vars": scope.all_declared_vars()}
                ))
                return None
            return t

        if isinstance(expr, UnaryOp):
            t = self.visit_expr(expr.expr, scope)
            if expr.op == "not":
                if t is not None and t != "bool":
                    self.errors.append(SemError(
                        "SEM004", expr.line,
                        f"'not' needs a true/false value, but got '{t}'",
                        {"op": "not", "type": t}
                    ))
                return "bool"
            if expr.op == "-":
                if t is not None and t not in NUMERIC:
                    self.errors.append(SemError(
                        "SEM004", expr.line,
                        f"Unary '-' needs a number, but got '{t}'",
                        {"op": "-", "type": t}
                    ))
                return t

        if isinstance(expr, BinOp):
            lt = self.visit_expr(expr.left, scope)
            rt = self.visit_expr(expr.right, scope)
            return self.check_binop(expr.op, lt, rt, expr.line)

        return None

    def check_binop(self, op, lt, rt, line):
        if lt is None or rt is None:
            return None  # already reported (undeclared var); don't cascade

        if op in ("+", "-", "*", "/", "%"):
            if op == "+" and lt == "string" and rt == "string":
                return "string"
            if lt in NUMERIC and rt in NUMERIC:
                return "float" if "float" in (lt, rt) else "int"
            self.errors.append(SemError(
                "SEM004", line,
                f"Cannot use '{op}' between a '{lt}' and a '{rt}'",
                {"op": op, "left": lt, "right": rt}
            ))
            return None

        if op in ("==", "!="):
            if lt != rt and not (lt in NUMERIC and rt in NUMERIC):
                self.errors.append(SemError(
                    "SEM004", line,
                    f"Cannot compare a '{lt}' with a '{rt}' using '{op}'",
                    {"op": op, "left": lt, "right": rt}
                ))
            return "bool"

        if op in ("<", ">", "<=", ">="):
            if lt not in NUMERIC or rt not in NUMERIC:
                self.errors.append(SemError(
                    "SEM004", line,
                    f"Cannot compare a '{lt}' with a '{rt}' using '{op}'",
                    {"op": op, "left": lt, "right": rt}
                ))
            return "bool"

        if op in ("and", "or"):
            if lt != "bool" or rt != "bool":
                self.errors.append(SemError(
                    "SEM004", line,
                    f"'{op}' needs true/false values on both sides, got '{lt}' and '{rt}'",
                    {"op": op, "left": lt, "right": rt}
                ))
            return "bool"

        return None

    def check_assign_compat(self, declared_type, expr_type, name, line):
        if expr_type is None:
            return  # already reported
        if declared_type == expr_type:
            return
        if declared_type == "float" and expr_type == "int":
            return  # int -> float widening is fine
        self.errors.append(SemError(
            "SEM003", line,
            f"Cannot assign a '{expr_type}' value to '{name}', which is declared as '{declared_type}'",
            {"name": name, "declared": declared_type, "got": expr_type}
        ))

    def check_condition_type(self, cond_type, line):
        if cond_type is not None and cond_type != "bool":
            self.errors.append(SemError(
                "SEM005", line,
                f"A condition here must be true/false, but this is a '{cond_type}'",
                {"type": cond_type}
            ))
