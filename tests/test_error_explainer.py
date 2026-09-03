import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lexer import LexError
from parser import ParseError
from semantic import SemError
from tac_interpreter import RuntimeErrorObject
from error_explainer import explain, levenshtein_distance, find_suggestion


class TestErrorExplainer(unittest.TestCase):

    def test_levenshtein_distance(self):
        self.assertEqual(levenshtein_distance("pritn", "print"), 2)
        self.assertEqual(levenshtein_distance("totl", "total"), 1)

    def test_find_suggestion(self):
        sug = find_suggestion("totl", ["total", "subtotal", "count"])
        self.assertEqual(sug, "total")

    def test_error_explanations(self):
        lex_err = LexError("LEX001", 1, "Unexpected char @", {"char": "@"})
        exp1 = explain(lex_err)
        self.assertIn("What happened:", exp1)
        self.assertIn("@", exp1)

        run_err = RuntimeErrorObject("RUN001", 3, "Division by zero")
        exp2 = explain(run_err)
        self.assertIn("Division by zero", exp2)
        self.assertIn("How to fix it:", exp2)


if __name__ == "__main__":
    unittest.main()
