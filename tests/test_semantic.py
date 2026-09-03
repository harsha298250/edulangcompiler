import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer


class TestSemanticAnalyzer(unittest.TestCase):

    def test_valid_program_semantics(self):
        source = """
        int x = 10;
        int y = 20;
        int sum = x + y;
        bool is_large = sum > 25;
        """
        tokens, _ = Lexer(source).tokenize()
        prog = Parser(tokens).parse_program()
        analyzer = SemanticAnalyzer(prog)
        errors = analyzer.analyze()
        self.assertEqual(len(errors), 0)

    def test_undeclared_variable(self):
        source = "totl = 10;"
        tokens, _ = Lexer(source).tokenize()
        prog = Parser(tokens).parse_program()
        analyzer = SemanticAnalyzer(prog)
        errors = analyzer.analyze()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].code, "SEM001")
        self.assertEqual(errors[0].context["name"], "totl")

    def test_redeclared_variable(self):
        source = "int x = 5; int x = 10;"
        tokens, _ = Lexer(source).tokenize()
        prog = Parser(tokens).parse_program()
        analyzer = SemanticAnalyzer(prog)
        errors = analyzer.analyze()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].code, "SEM002")

    def test_type_mismatch(self):
        source = 'int num = "hello";'
        tokens, _ = Lexer(source).tokenize()
        prog = Parser(tokens).parse_program()
        analyzer = SemanticAnalyzer(prog)
        errors = analyzer.analyze()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].code, "SEM003")

    def test_invalid_condition_type(self):
        source = 'if ("hello") { print(1); }'
        tokens, _ = Lexer(source).tokenize()
        prog = Parser(tokens).parse_program()
        analyzer = SemanticAnalyzer(prog)
        errors = analyzer.analyze()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].code, "SEM005")


if __name__ == "__main__":
    unittest.main()
