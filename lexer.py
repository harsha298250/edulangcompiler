"""
Lexer for EduLang — a small teaching language.
Converts raw source text into a stream of tokens.
Reports lexical errors (bad characters, unterminated strings) with line numbers.
"""

KEYWORDS = {
    "int", "float", "string", "bool", "true", "false",
    "if", "else", "while", "print", "and", "or", "not"
}

SYMBOLS = {
    "+": "PLUS", "-": "MINUS", "*": "STAR", "/": "SLASH", "%": "PERCENT",
    "(": "LPAREN", ")": "RPAREN", "{": "LBRACE", "}": "RBRACE",
    ";": "SEMI", ",": "COMMA",
}


class Token:
    def __init__(self, type_, value, line, col=1):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, line={self.line}, col={self.col})"


class LexError:
    """A single lexical error, kept simple so ErrorExplainer can format it."""
    def __init__(self, code, line, technical, context=None, col=1):
        self.phase = "Lexical"
        self.code = code
        self.line = line
        self.col = col
        self.technical = technical
        self.context = context or {}


class Lexer:
    def __init__(self, source):
        self.src = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens = []
        self.errors = []

    def peek(self, offset=0):
        idx = self.pos + offset
        return self.src[idx] if idx < len(self.src) else ""

    def advance(self):
        ch = self.src[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def tokenize(self):
        while self.pos < len(self.src):
            ch = self.peek()
            start_col = self.col

            if ch in " \t\r\n":
                self.advance()
                continue

            if ch == "#":  # comment to end of line
                while self.pos < len(self.src) and self.peek() != "\n":
                    self.advance()
                continue

            if ch.isdigit():
                self._read_number(start_col)
                continue

            if ch.isalpha() or ch == "_":
                self._read_identifier(start_col)
                continue

            if ch == '"':
                self._read_string(start_col)
                continue

            if ch == "=" and self.peek(1) == "=":
                self.advance(); self.advance()
                self.tokens.append(Token("EQ", "==", self.line, start_col))
                continue
            if ch == "!" and self.peek(1) == "=":
                self.advance(); self.advance()
                self.tokens.append(Token("NEQ", "!=", self.line, start_col))
                continue
            if ch == "<" and self.peek(1) == "=":
                self.advance(); self.advance()
                self.tokens.append(Token("LTE", "<=", self.line, start_col))
                continue
            if ch == ">" and self.peek(1) == "=":
                self.advance(); self.advance()
                self.tokens.append(Token("GTE", ">=", self.line, start_col))
                continue
            if ch == "=":
                self.advance()
                self.tokens.append(Token("ASSIGN", "=", self.line, start_col))
                continue
            if ch == "<":
                self.advance()
                self.tokens.append(Token("LT", "<", self.line, start_col))
                continue
            if ch == ">":
                self.advance()
                self.tokens.append(Token("GT", ">", self.line, start_col))
                continue

            if ch in SYMBOLS:
                self.advance()
                self.tokens.append(Token(SYMBOLS[ch], ch, self.line, start_col))
                continue

            # Unknown character -> lexical error, skip it and keep going
            self.errors.append(LexError(
                "LEX001", self.line,
                f"Unexpected character '{ch}'",
                {"char": ch},
                col=start_col
            ))
            self.advance()

        self.tokens.append(Token("EOF", None, self.line, self.col))
        return self.tokens, self.errors

    def _read_number(self, start_col=1):
        start_line = self.line
        start = self.pos
        is_float = False
        while self.peek().isdigit():
            self.advance()
        if self.peek() == "." and self.peek(1).isdigit():
            is_float = True
            self.advance()
            while self.peek().isdigit():
                self.advance()
        text = self.src[start:self.pos]
        if is_float:
            self.tokens.append(Token("FLOAT_LIT", float(text), start_line, start_col))
        else:
            self.tokens.append(Token("NUMBER_LIT", int(text), start_line, start_col))

    def _read_identifier(self, start_col=1):
        start_line = self.line
        start = self.pos
        while self.peek().isalnum() or self.peek() == "_":
            self.advance()
        text = self.src[start:self.pos]
        if text in KEYWORDS:
            self.tokens.append(Token(text.upper(), text, start_line, start_col))
        else:
            self.tokens.append(Token("IDENT", text, start_line, start_col))

    def _read_string(self, start_col=1):
        start_line = self.line
        self.advance()  # opening quote
        chars = []
        raw_start = self.pos
        while self.pos < len(self.src) and self.peek() != '"' and self.peek() != "\n":
            ch = self.advance()
            if ch == "\\" and self.pos < len(self.src):
                nxt = self.peek()
                if nxt == '"':
                    chars.append('"')
                    self.advance()
                elif nxt == "\\":
                    chars.append("\\")
                    self.advance()
                elif nxt == "n":
                    chars.append("\n")
                    self.advance()
                elif nxt == "t":
                    chars.append("\t")
                    self.advance()
                else:
                    chars.append(ch)
            else:
                chars.append(ch)

        if self.pos >= len(self.src) or self.peek() == "\n":
            # unterminated string
            text = self.src[raw_start:self.pos]
            self.errors.append(LexError(
                "LEX002", start_line,
                f"Unterminated string literal starting with \"{text}",
                {"partial": text},
                col=start_col
            ))
            return
        self.advance()  # closing quote
        val = "".join(chars)
        self.tokens.append(Token("STRING_LIT", val, start_line, start_col))


def explain_token(tok):
    """Generates dynamic, student-friendly explanation for a single Token."""
    if tok is None:
        return {}

    t_type = str(tok.type)
    val = tok.value
    line = tok.line
    col = getattr(tok, "col", 1)

    what = ""
    why = ""
    where = ""

    if t_type in ("INT", "FLOAT", "STRING", "BOOL"):
        what = f"Type Keyword '{val}' specifying a primitive variable data type."
        why = f"Matches the EduLang type keyword '{val}' in the lexer keyword set."
        where = "Used by Parser (`parse_decl`) to enforce declaration types and by Semantic Analyzer to set Symbol Table types."
    elif t_type in ("IF", "ELSE", "WHILE", "PRINT", "TRUE", "FALSE", "AND", "OR", "NOT"):
        what = f"Control/Reserved Keyword '{val}' controlling statement flow or boolean logic."
        why = f"Recognized as a reserved EduLang keyword '{val}'."
        where = "Used by Parser to construct control flow AST branches (`If`, `While`, `Print`) or boolean expressions."
    elif t_type == "IDENT":
        what = f"Identifier '{val}' used to name a variable or program element."
        why = f"Follows EduLang identifier syntax rules (starts with letter/underscore, followed by alphanumeric characters) and is not a reserved keyword."
        where = "Used by Parser (`parse_decl`, `parse_assign`, `VarRef`) and resolved in Symbol Table scopes during Semantic Analysis."
    elif t_type == "NUMBER_LIT":
        what = f"Integer Literal '{val}' representing a constant whole number value."
        why = f"Scanned as a sequence of digit characters without a decimal point."
        where = "Constructs a `Literal(int)` AST node for numerical calculations."
    elif t_type == "FLOAT_LIT":
        what = f"Float Literal '{val}' representing a constant floating-point number."
        why = f"Scanned as digit characters containing a decimal point '.'."
        where = "Constructs a `Literal(float)` AST node for decimal calculations."
    elif t_type == "STRING_LIT":
        what = f"String Literal \"{val}\" representing textual content."
        why = f"Scanned inside double-quote delimiters (\"...\") on a single line."
        where = "Constructs a `Literal(string)` AST node used in text manipulation or print outputs."
    elif t_type == "ASSIGN":
        what = "Assignment Operator '=' used to store expression values into variables."
        why = "Scanned as single character '=' not followed by another '='."
        where = "Used by Parser (`parse_assign`, `parse_decl`) to link a target variable to an assigned expression."
    elif t_type in ("PLUS", "MINUS", "STAR", "SLASH", "PERCENT"):
        what = f"Arithmetic Operator '{val}' performing mathematical operations."
        why = f"Matches symbol '{val}' defined in the lexer symbol table."
        where = "Constructs `BinOp` or `UnaryOp` AST nodes for expression evaluation."
    elif t_type in ("EQ", "NEQ", "LT", "GT", "LTE", "GTE"):
        what = f"Comparison Operator '{val}' comparing left and right numerical/expression operands."
        why = f"Scanned operator symbol '{val}' yielding a boolean true/false result."
        where = "Constructs `BinOp` AST comparison nodes in conditions."
    elif t_type in ("LPAREN", "RPAREN"):
        what = f"Parenthesis '{val}' used for grouping expressions or function argument lists."
        why = f"Scanned parenthesis character '{val}'."
        where = "Guides Parser expression grouping and statement parsing (e.g. `if (...)`, `print(...)`)."
    elif t_type in ("LBRACE", "RBRACE"):
        what = f"Brace '{val}' marking the boundary of a local block scope."
        why = f"Scanned block delimiter '{val}'."
        where = "Parses `Block` AST nodes and delimits local symbol table scope lifetimes."
    elif t_type == "SEMI":
        what = "Semicolon ';' terminating a statement."
        why = "Scanned statement separator ';' required by EduLang grammar."
        where = "Signals statement completion to the Parser."
    elif t_type == "EOF":
        what = "End-Of-File marker indicating the completion of source code scanning."
        why = "Generated when Lexer reaches the end of source text."
        where = "Tells Parser to finish `parse_program` loop."
    else:
        what = f"Token '{val}' of type '{t_type}'."
        why = f"Scanned by Lexer as '{t_type}'."
        where = "Passed to Parser stream."

    return {
        "type": t_type,
        "value": str(val) if val is not None else "",
        "line": line,
        "col": col,
        "what": what,
        "why": why,
        "where": where
    }

