import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lexer import Lexer
from parser import Parser, ParseError, Program, VarDecl, Assign, Print, If, While, BinOp, UnaryOp


class TestParser(unittest.TestCase):

    def test_parse_declarations_and_assignments(self):
        source = "int x = 10; float y = 2.5; x = x + 1;"
        tokens, _ = Lexer(source).tokenize()
        parser = Parser(tokens)
        prog = parser.parse_program()
        self.assertIsInstance(prog, Program)
        self.assertEqual(len(prog.statements), 3)
        self.assertIsInstance(prog.statements[0], VarDecl)
        self.assertIsInstance(prog.statements[2], Assign)

    def test_parse_if_while_blocks(self):
        source = """
        if (x > 0) {
            print(x);
        } else {
            print(0);
        }
        while (x < 10) {
            x = x + 1;
        }
        """
        tokens, _ = Lexer(source).tokenize()
        parser = Parser(tokens)
        prog = parser.parse_program()
        self.assertIsInstance(prog.statements[0], If)
        self.assertIsInstance(prog.statements[1], While)

    def test_syntax_errors(self):
        # Missing semicolon
        tokens1, _ = Lexer("int x = 5\nprint(x);").tokenize()
        with self.assertRaises(ParseError) as ctx1:
            Parser(tokens1).parse_program()
        self.assertEqual(ctx1.exception.code, "SYN001")

        # Missing closing paren
        tokens2, _ = Lexer("print(10;").tokenize()
        with self.assertRaises(ParseError) as ctx2:
            Parser(tokens2).parse_program()
        self.assertEqual(ctx2.exception.code, "SYN003")


if __name__ == "__main__":
    unittest.main()
