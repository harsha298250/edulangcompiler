import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lexer import Lexer, Token, LexError


class TestLexer(unittest.TestCase):

    def test_tokenize_literals_and_keywords(self):
        source = 'int x = 15; float y = 3.14; string s = "hello"; bool b = true;'
        lexer = Lexer(source)
        tokens, errors = lexer.tokenize()
        self.assertEqual(len(errors), 0)
        types = [t.type for t in tokens]
        self.assertIn("INT", types)
        self.assertIn("FLOAT_LIT", types)
        self.assertIn("STRING_LIT", types)
        self.assertIn("BOOL", types)
        self.assertIn("TRUE", types)

    def test_operators_and_comments(self):
        source = """
        # this is a comment
        x = x + 1;
        bool check = (x >= 10) and (x != 5);
        """
        lexer = Lexer(source)
        tokens, errors = lexer.tokenize()
        self.assertEqual(len(errors), 0)
        types = [t.type for t in tokens]
        self.assertIn("PLUS", types)
        self.assertIn("GTE", types)
        self.assertIn("NEQ", types)
        self.assertIn("AND", types)

    def test_lexical_errors(self):
        source = 'int a = 10 @ 2; string s = "unterminated;'
        lexer = Lexer(source)
        tokens, errors = lexer.tokenize()
        self.assertGreaterEqual(len(errors), 2)
        codes = [e.code for e in errors]
        self.assertIn("LEX001", codes)
        self.assertIn("LEX002", codes)


if __name__ == "__main__":
    unittest.main()
