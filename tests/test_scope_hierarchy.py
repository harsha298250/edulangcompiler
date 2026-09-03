import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer, render_scope_tree


class TestScopeHierarchy(unittest.TestCase):

    def test_actual_scope_visualization_data(self):
        source = """
        int x = 10;
        if (x > 5) {
            int y = 20;
            print(y);
        }
        """
        tokens, _ = Lexer(source).tokenize()
        prog = Parser(tokens).parse_program()
        analyzer = SemanticAnalyzer(prog)
        analyzer.analyze()

        tree_text = render_scope_tree(analyzer.global_scope)
        self.assertIn("Global Scope", tree_text)
        self.assertIn("x : int", tree_text)
        self.assertIn("If-Then Scope (Line 3)", tree_text)
        self.assertIn("y : int", tree_text)
        # Verify no phantom generic "Nested Block"
        self.assertNotIn("Nested Block", tree_text)


if __name__ == "__main__":
    unittest.main()
