"""
Alternative Tree-Walking Interpreter for EduLang.

This module contains an alternative tree-walking interpreter retained as a
teaching and reference implementation. The production execution path of
EduLang uses tac_interpreter.py and the Three-Address Code (TAC) Virtual Machine.
"""

from parser import (
    VarDecl, Assign, Print, If, While, Block, BinOp, UnaryOp, Literal, VarRef
)


class Env:
    """A single scope's variable storage, chained to its parent scope."""
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def declare(self, name, value):
        self.vars[name] = value

    def get(self, name):
        scope = self
        while scope:
            if name in scope.vars:
                return scope.vars[name]
            scope = scope.parent
        raise RuntimeError(f"'{name}' not found at runtime")

    def set(self, name, value):
        scope = self
        while scope:
            if name in scope.vars:
                scope.vars[name] = value
                return
            scope = scope.parent
        # Fallback: declare in current scope if never found (shouldn't
        # happen for a program that passed semantic analysis).
        self.vars[name] = value


class Interpreter:
    """
    Executes a Program AST that has already passed semantic analysis.
    Collects stdout lines and the final flattened variable state so a UI
    can display both a console and a "memory" view.
    """

    def __init__(self, program):
        self.program = program
        self.output = []          # list of printed lines
        self.global_env = Env()
        self.trace = []           # ordered (name, value) snapshots for display
        self.step_limit = 200000  # guard against runaway while loops
        self.steps = 0

    def run(self):
        self.exec_block(self.program.statements, self.global_env)
        return self.output, self._flatten(self.global_env)

    def _flatten(self, env):
        """Flatten the (possibly nested) global scope into name->value."""
        return dict(env.vars)

    def _tick(self):
        self.steps += 1
        if self.steps > self.step_limit:
            raise RuntimeError("Execution took too long (possible infinite loop) — stopped.")

    def exec_block(self, statements, env):
        for stmt in statements:
            self.exec_stmt(stmt, env)

    def exec_stmt(self, stmt, env):
        self._tick()

        if isinstance(stmt, VarDecl):
            value = self.eval_expr(stmt.expr, env) if stmt.expr is not None else self._default(stmt.var_type)
            env.declare(stmt.name, value)

        elif isinstance(stmt, Assign):
            value = self.eval_expr(stmt.expr, env)
            env.set(stmt.name, value)

        elif isinstance(stmt, Print):
            value = self.eval_expr(stmt.expr, env)
            self.output.append(self._stringify(value))

        elif isinstance(stmt, If):
            cond = self.eval_expr(stmt.cond, env)
            if cond:
                self.exec_stmt(stmt.then_block, Env(env))
            elif stmt.else_block is not None:
                self.exec_stmt(stmt.else_block, Env(env))

        elif isinstance(stmt, While):
            while self.eval_expr(stmt.cond, env):
                self._tick()
                self.exec_stmt(stmt.block, Env(env))

        elif isinstance(stmt, Block):
            self.exec_block(stmt.statements, Env(env))

    def eval_expr(self, expr, env):
        if isinstance(expr, Literal):
            return expr.value

        if isinstance(expr, VarRef):
            return env.get(expr.name)

        if isinstance(expr, UnaryOp):
            val = self.eval_expr(expr.expr, env)
            if expr.op == "not":
                return not val
            if expr.op == "-":
                return -val

        if isinstance(expr, BinOp):
            l = self.eval_expr(expr.left, env)
            r = self.eval_expr(expr.right, env)
            return self._binop(expr.op, l, r)

        return None

    def _binop(self, op, l, r):
        if op == "+":
            return l + r
        if op == "-":
            return l - r
        if op == "*":
            return l * r
        if op == "/":
            if r == 0:
                raise RuntimeError("Division by zero")
            return l / r
        if op == "%":
            if r == 0:
                raise RuntimeError("Modulo by zero")
            if isinstance(l, float) or isinstance(r, float):
                return l - r * (int(l / r) if l / r >= 0 else -int(-(l / r)))
            # C-style modulo: result takes the sign of the dividend.
            m = abs(l) % abs(r)
            return -m if l < 0 else m
        if op == "==":
            return l == r
        if op == "!=":
            return l != r
        if op == "<":
            return l < r
        if op == ">":
            return l > r
        if op == "<=":
            return l <= r
        if op == ">=":
            return l >= r
        if op == "and":
            return bool(l) and bool(r)
        if op == "or":
            return bool(l) or bool(r)
        raise RuntimeError(f"Unknown operator '{op}'")

    def _default(self, type_):
        return {"int": 0, "float": 0.0, "string": "", "bool": False}.get(type_, None)

    def _stringify(self, value):
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)
