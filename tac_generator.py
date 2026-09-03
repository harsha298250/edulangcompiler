"""
Three-Address Code (TAC) generator for EduLang.

Walks the AST (post semantic-analysis) and emits a real intermediate
representation: every instruction has at most one operator and three
addresses (result, arg1, arg2). Propagates AST source line metadata to TAC instructions.
"""

from parser import (
    VarDecl, Assign, Print, If, While, Block, BinOp, UnaryOp, Literal, VarRef
)


class TACInstruction:
    """Represents a single TAC instruction with attached source line metadata."""
    def __init__(self, text, line=None):
        self.text = str(text)
        self.line = line

    def __str__(self):
        return self.text

    def __repr__(self):
        return f"TACInstruction({self.text!r}, line={self.line})"

    def startswith(self, prefix):
        return self.text.startswith(prefix)

    def endswith(self, suffix):
        return self.text.endswith(suffix)

    def split(self, *args, **kwargs):
        return self.text.split(*args, **kwargs)

    def __contains__(self, item):
        return item in self.text


class TACGenerator:
    def __init__(self):
        self.code = []
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self):
        name = f"t{self.temp_count}"
        self.temp_count += 1
        return name

    def new_label(self):
        name = f"L{self.label_count}"
        self.label_count += 1
        return name

    def emit(self, instr, line=None):
        if isinstance(instr, TACInstruction):
            self.code.append(instr)
        else:
            self.code.append(TACInstruction(instr, line=line))

    def generate(self, program):
        for stmt in program.statements:
            self.gen_stmt(stmt)
        return self.code

    def gen_stmt(self, stmt):
        if isinstance(stmt, VarDecl):
            if stmt.expr is not None:
                val = self.gen_expr(stmt.expr)
                self.emit(f"{stmt.name} = {val}", line=stmt.line)
            else:
                self.emit(f"{stmt.name} = <uninitialized>", line=stmt.line)

        elif isinstance(stmt, Assign):
            val = self.gen_expr(stmt.expr)
            self.emit(f"{stmt.name} = {val}", line=stmt.line)

        elif isinstance(stmt, Print):
            val = self.gen_expr(stmt.expr)
            self.emit(f"PRINT {val}", line=stmt.line)

        elif isinstance(stmt, If):
            cond = self.gen_expr(stmt.cond)
            else_label = self.new_label()
            end_label = self.new_label()
            self.emit(f"IF_FALSE {cond} GOTO {else_label}", line=stmt.line)
            self.gen_stmt(stmt.then_block)
            self.emit(f"GOTO {end_label}", line=stmt.line)
            self.emit(f"{else_label}:", line=stmt.line)
            if stmt.else_block is not None:
                self.gen_stmt(stmt.else_block)
            self.emit(f"{end_label}:", line=stmt.line)

        elif isinstance(stmt, While):
            start_label = self.new_label()
            end_label = self.new_label()
            self.emit(f"{start_label}:", line=stmt.line)
            cond = self.gen_expr(stmt.cond)
            self.emit(f"IF_FALSE {cond} GOTO {end_label}", line=stmt.line)
            self.gen_stmt(stmt.block)
            self.emit(f"GOTO {start_label}", line=stmt.line)
            self.emit(f"{end_label}:", line=stmt.line)

        elif isinstance(stmt, Block):
            for s in stmt.statements:
                self.gen_stmt(s)

    def gen_expr(self, expr):
        """Returns the 'address' (temp name, literal, or var name) holding this value."""
        if isinstance(expr, Literal):
            if expr.kind == "string":
                return f'"{expr.value}"'
            if expr.kind == "bool":
                return "true" if expr.value else "false"
            return str(expr.value)

        if isinstance(expr, VarRef):
            return expr.name

        if isinstance(expr, UnaryOp):
            val = self.gen_expr(expr.expr)
            t = self.new_temp()
            self.emit(f"{t} = {expr.op} {val}", line=expr.line)
            return t

        if isinstance(expr, BinOp):
            l = self.gen_expr(expr.left)
            r = self.gen_expr(expr.right)
            t = self.new_temp()
            self.emit(f"{t} = {l} {expr.op} {r}", line=expr.line)
            return t

        return "?"


def generate_tac(program):
    gen = TACGenerator()
    return gen.generate(program)


def explain_tac_instruction(instr):
    """Generates natural language explanation for a single TAC instruction."""
    line_str = str(instr).strip()
    if not line_str:
        return ""
    if line_str.endswith(":") and not ("=" in line_str or "GOTO" in line_str or "PRINT" in line_str):
        lbl = line_str[:-1]
        return f"Label {lbl}: Jump target for control flow"
    if line_str.startswith("PRINT "):
        arg = line_str[6:].strip()
        return f"Print the value of {arg} to console output"
    if line_str.startswith("GOTO "):
        lbl = line_str[5:].strip()
        return f"Jump directly to label {lbl}"
    if line_str.startswith("IF_FALSE "):
        parts = line_str.split()
        cond = parts[1]
        lbl = parts[3]
        return f"If condition '{cond}' is false, jump to label {lbl}"
    if "=" in line_str:
        lhs, rhs = [p.strip() for p in line_str.split("=", 1)]
        tokens = rhs.split()
        if len(tokens) == 1:
            return f"Assign value {tokens[0]} to '{lhs}'"
        if len(tokens) == 2:
            return f"Apply unary '{tokens[0]}' to {tokens[1]} and store in '{lhs}'"
        if len(tokens) == 3:
            return f"Compute ({tokens[0]} {tokens[1]} {tokens[2]}) and store in '{lhs}'"
    return "Execute instruction"
