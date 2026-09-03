import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lexer import Lexer
from parser import Parser, ParseError
from semantic import SemanticAnalyzer
from error_explainer import explain, find_suggestion, KEYWORDS


class TestTypoSuggestions(unittest.TestCase):

    def test_irrelevant_suggestion_prevention(self):
        # Case B: Incomplete declaration 'int \n if (sum > 30)' should NOT suggest 'if'
        source = "int\nif (sum > 30) {\n    print(1);\n}"
        tokens, _ = Lexer(source).tokenize()
        parser = Parser(tokens)
        with self.assertRaises(ParseError) as ctx:
            parser.parse_program()
        
        explanation = explain(ctx.exception)
        self.assertNotIn('Did you mean \'if\'?', explanation)
        self.assertIn("Missing variable name after type", explanation)

    def test_relevant_typo_suggestion(self):
        # Case C: 'totl = 10;' when 'total' is declared should suggest 'total'
        source = "int total = 10;\ntotl = 20;"
        tokens, _ = Lexer(source).tokenize()
        prog = Parser(tokens).parse_program()
        analyzer = SemanticAnalyzer(prog)
        sem_errors = analyzer.analyze()
        
        self.assertGreater(len(sem_errors), 0)
        explanation = explain(sem_errs := sem_errors[0])
        self.assertIn("Did you mean 'total'?", explanation)

    def test_keyword_typo_suggestion(self):
        # 'pritn(x);' should suggest 'print'
        source = "int x = 10;\npritn(x);"
        tokens, _ = Lexer(source).tokenize()
        parser = Parser(tokens)
        with self.assertRaises(ParseError) as ctx:
            parser.parse_program()
        explanation = explain(ctx.exception)
        self.assertIn("Did you mean 'print'?", explanation)


if __name__ == "__main__":
    unittest.main()
