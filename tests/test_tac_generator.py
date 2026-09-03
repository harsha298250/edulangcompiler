import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lexer import Lexer
from parser import Parser
from tac_generator import generate_tac, explain_tac_instruction


class TestTACGenerator(unittest.TestCase):

    def test_tac_generation_arithmetic(self):
        source = "int x = 10; int y = 20; int z = x + y * 2;"
        tokens, _ = Lexer(source).tokenize()
        prog = Parser(tokens).parse_program()
        tac = generate_tac(prog)
        self.assertTrue(any("x = 10" in line for line in tac))
        self.assertTrue(any("y = 20" in line for line in tac))
        self.assertTrue(any("+" in line for line in tac))
        self.assertTrue(any("*" in line for line in tac))

    def test_tac_generation_control_flow(self):
        source = """
        if (x > 0) {
            print(x);
        }
        while (y < 5) {
            y = y + 1;
        }
        """
        tokens, _ = Lexer(source).tokenize()
        prog = Parser(tokens).parse_program()
        tac = generate_tac(prog)
        self.assertTrue(any(line.startswith("IF_FALSE") for line in tac))
        self.assertTrue(any(line.startswith("GOTO") for line in tac))

    def test_tac_instruction_explanations(self):
        exp1 = explain_tac_instruction("t0 = x + y")
        self.assertIn("x + y", exp1)
        exp2 = explain_tac_instruction("IF_FALSE t0 GOTO L1")
        self.assertIn("L1", exp2)


if __name__ == "__main__":
    unittest.main()
