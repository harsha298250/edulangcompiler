"""
Recursive-descent parser for EduLang.
Builds an AST from the token stream produced by the Lexer.
Raises a single ParseError as soon as the grammar is violated (classic
single-error-per-compile-pass behaviour, same as most teaching compilers).
"""


class ParseError(Exception):
    def __init__(self, code, line, technical, context=None):
        self.phase = "Syntax"
        self.code = code
        self.line = line
        self.technical = technical
        self.context = context or {}
        super().__init__(technical)


# ---------- AST node types (simple namedtuple-like classes) ----------

class Program:
    def __init__(self, statements):
        self.statements = statements

class VarDecl:
    def __init__(self, var_type, name, expr, line):
        self.var_type = var_type; self.name = name; self.expr = expr; self.line = line

class Assign:
    def __init__(self, name, expr, line):
        self.name = name; self.expr = expr; self.line = line

class Print:
    def __init__(self, expr, line):
        self.expr = expr; self.line = line

class If:
    def __init__(self, cond, then_block, else_block, line):
        self.cond = cond; self.then_block = then_block; self.else_block = else_block; self.line = line

class While:
    def __init__(self, cond, block, line):
        self.cond = cond; self.block = block; self.line = line

class Block:
    def __init__(self, statements, line=None):
        self.statements = statements; self.line = line

class BinOp:
    def __init__(self, op, left, right, line):
        self.op = op; self.left = left; self.right = right; self.line = line

class UnaryOp:
    def __init__(self, op, expr, line):
        self.op = op; self.expr = expr; self.line = line

class Literal:
    def __init__(self, value, kind, line):
        self.value = value; self.kind = kind; self.line = line

class VarRef:
    def __init__(self, name, line):
        self.name = name; self.line = line


TYPE_TOKENS = {"INT", "FLOAT", "STRING", "BOOL"}


def _display(tok):
    """Human-friendly text for a token, used in error messages."""
    if tok.type == "EOF":
        return "the end of the file"
    return tok.value if tok.value is not None else tok.type


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errors = []

    def peek(self, offset=0):
        idx = self.pos + offset
        return self.tokens[idx] if idx < len(self.tokens) else self.tokens[-1]

    def current(self):
        return self.tokens[self.pos]

    def advance(self):
        tok = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def check(self, type_):
        return self.current().type == type_

    def expect(self, type_, code, friendly_hint):
        if self.check(type_):
            return self.advance()
        got = self.current()
        raise ParseError(
            code, got.line,
            f"Expected {type_} but found '{_display(got)}'",
            {"expected": type_, "got": got.type, "got_value": _display(got), "hint": friendly_hint}
        )

    def synchronize(self):
        """Advances token stream past statement boundary (SEMI or keyword) to recover."""
        self.advance()
        while not self.check("EOF"):
            if self.current().type == "SEMI":
                self.advance()
                return
            if self.peek(0).type in TYPE_TOKENS or self.peek(0).type in ("IF", "WHILE", "PRINT"):
                return
            self.advance()

    # ---------- grammar ----------

    def parse_program(self):
        stmts = []
        while not self.check("EOF"):
            try:
                stmts.append(self.parse_statement())
            except ParseError as e:
                self.errors.append(e)
                self.synchronize()
                if not stmts and self.check("EOF"):
                    break
        if self.errors:
            raise self.errors[0]
        return Program(stmts)

    def parse_statement(self):
        tok = self.current()

        if tok.type in TYPE_TOKENS:
            return self.parse_decl()
        if tok.type == "IDENT":
            return self.parse_assign()
        if tok.type == "PRINT":
            return self.parse_print()
        if tok.type == "IF":
            return self.parse_if()
        if tok.type == "WHILE":
            return self.parse_while()
        if tok.type == "LBRACE":
            return self.parse_block()

        raise ParseError(
            "SYN004", tok.line,
            f"Did not expect '{_display(tok)}' here",
            {"got": tok.type, "got_value": _display(tok)}
        )

    def parse_decl(self):
        type_tok = self.advance()
        name_tok = self.expect("IDENT", "SYN002", "a variable name after the type")
        expr = None
        if self.check("ASSIGN"):
            self.advance()
            expr = self.parse_expr()
        self.expect("SEMI", "SYN001", "a semicolon ';' to end the statement")
        return VarDecl(type_tok.value, name_tok.value, expr, type_tok.line)

    def parse_assign(self):
        name_tok = self.advance()
        if not self.check("ASSIGN") and self.check("LPAREN"):
            got = self.current()
            raise ParseError(
                "SYN002", got.line,
                f"Expected '=' after identifier but found '{_display(got)}'",
                {"expected": "ASSIGN", "got": name_tok.type, "got_value": name_tok.value, "hint": "an '=' to assign a value"}
            )
        self.expect("ASSIGN", "SYN002", "an '=' to assign a value")
        expr = self.parse_expr()
        self.expect("SEMI", "SYN001", "a semicolon ';' to end the statement")
        return Assign(name_tok.value, expr, name_tok.line)

    def parse_print(self):
        line = self.advance().line
        self.expect("LPAREN", "SYN002", "an opening parenthesis '(' after print")
        expr = self.parse_expr()
        self.expect("RPAREN", "SYN003", "a closing parenthesis ')' to match the '('")
        self.expect("SEMI", "SYN001", "a semicolon ';' to end the statement")
        return Print(expr, line)

    def parse_if(self):
        line = self.advance().line
        self.expect("LPAREN", "SYN002", "an opening parenthesis '(' after if")
        cond = self.parse_expr()
        self.expect("RPAREN", "SYN003", "a closing parenthesis ')' to match the '('")
        then_block = self.parse_block()
        else_block = None
        if self.check("ELSE"):
            self.advance()
            else_block = self.parse_block()
        return If(cond, then_block, else_block, line)

    def parse_while(self):
        line = self.advance().line
        self.expect("LPAREN", "SYN002", "an opening parenthesis '(' after while")
        cond = self.parse_expr()
        self.expect("RPAREN", "SYN003", "a closing parenthesis ')' to match the '('")
        block = self.parse_block()
        return While(cond, block, line)

    def parse_block(self):
        lbrace_tok = self.expect("LBRACE", "SYN002", "an opening brace '{' to start a block")
        stmts = []
        while not self.check("RBRACE") and not self.check("EOF"):
            stmts.append(self.parse_statement())
        self.expect("RBRACE", "SYN003", "a closing brace '}' to match the '{'")
        return Block(stmts, line=lbrace_tok.line)

    # ---------- expressions (precedence climbing) ----------

    def parse_expr(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.check("OR"):
            op = self.advance()
            right = self.parse_and()
            left = BinOp("or", left, right, op.line)
        return left

    def parse_and(self):
        left = self.parse_equality()
        while self.check("AND"):
            op = self.advance()
            right = self.parse_equality()
            left = BinOp("and", left, right, op.line)
        return left

    def parse_equality(self):
        left = self.parse_comparison()
        while self.check("EQ") or self.check("NEQ"):
            op = self.advance()
            right = self.parse_comparison()
            left = BinOp(op.value, left, right, op.line)
        return left

    def parse_comparison(self):
        left = self.parse_term()
        while self.current().type in ("LT", "GT", "LTE", "GTE"):
            op = self.advance()
            right = self.parse_term()
            left = BinOp(op.value, left, right, op.line)
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.current().type in ("PLUS", "MINUS"):
            op = self.advance()
            right = self.parse_factor()
            left = BinOp(op.value, left, right, op.line)
        return left

    def parse_factor(self):
        left = self.parse_unary()
        while self.current().type in ("STAR", "SLASH", "PERCENT"):
            op = self.advance()
            right = self.parse_unary()
            left = BinOp(op.value, left, right, op.line)
        return left

    def parse_unary(self):
        if self.current().type in ("MINUS", "NOT"):
            op = self.advance()
            expr = self.parse_unary()
            return UnaryOp(op.value, expr, op.line)
        return self.parse_primary()

    def parse_primary(self):
        tok = self.current()
        if tok.type == "NUMBER_LIT":
            self.advance(); return Literal(tok.value, "int", tok.line)
        if tok.type == "FLOAT_LIT":
            self.advance(); return Literal(tok.value, "float", tok.line)
        if tok.type == "STRING_LIT":
            self.advance(); return Literal(tok.value, "string", tok.line)
        if tok.type == "TRUE":
            self.advance(); return Literal(True, "bool", tok.line)
        if tok.type == "FALSE":
            self.advance(); return Literal(False, "bool", tok.line)
        if tok.type == "IDENT":
            self.advance(); return VarRef(tok.value, tok.line)
        if tok.type == "LPAREN":
            self.advance()
            expr = self.parse_expr()
            self.expect("RPAREN", "SYN003", "a closing parenthesis ')' to match the '('")
            return expr

        raise ParseError(
            "SYN004", tok.line,
            f"Expected an expression (a number, string, variable...) but found "
            f"'{_display(tok)}'",
            {"got": tok.type, "got_value": _display(tok)}
        )
