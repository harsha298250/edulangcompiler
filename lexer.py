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
        start = self.pos
        while self.pos < len(self.src) and self.peek() != '"' and self.peek() != "\n":
            self.advance()
        if self.pos >= len(self.src) or self.peek() == "\n":
            # unterminated string
            text = self.src[start:self.pos]
            self.errors.append(LexError(
                "LEX002", start_line,
                f"Unterminated string literal starting with \"{text}",
                {"partial": text},
                col=start_col
            ))
            return
        text = self.src[start:self.pos]
        self.advance()  # closing quote
        self.tokens.append(Token("STRING_LIT", text, start_line, start_col))
