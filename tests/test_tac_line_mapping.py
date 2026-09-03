import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lexer import Lexer
from parser import Parser
from tac_generator import generate_tac, TACInstruction


class TestTACLineMapping(unittest.TestCase):

    def test_source_line_to_tac_metadata_mapping(self):
        source = "int x = 15;\nint y = 25;\nint sum = x + y;"
        tokens, _ = Lexer(source).tokenize()
        prog = Parser(tokens).parse_program()
        tac = generate_tac(prog)

        line3_tac = [instr for instr in tac if getattr(instr, "line", None) == 3]
        self.assertGreater(len(line3_tac), 0)
        self.assertTrue(any("sum" in str(instr) for instr in line3_tac))


if __name__ == "__main__":
    unittest.main()
