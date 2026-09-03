import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lexer import Lexer
from parser import Parser
from tac_generator import generate_tac
from tac_interpreter import TACInterpreter, RuntimeErrorObject


class TestTACVM(unittest.TestCase):

    def test_tac_vm_execution(self):
        source = """
        int a = 10;
        int b = 20;
        int c = a + b;
        print("Sum:");
        print(c);
        """
        tokens, _ = Lexer(source).tokenize()
        prog = Parser(tokens).parse_program()
        tac = generate_tac(prog)
        vm = TACInterpreter(tac)
        output, vars_dict, trace = vm.run()
        self.assertEqual(output, ["Sum:", "30"])
        self.assertEqual(vars_dict["a"], 10)
        self.assertEqual(vars_dict["b"], 20)
        self.assertEqual(vars_dict["c"], 30)
        self.assertGreater(len(trace), 0)

    def test_division_by_zero(self):
        source = "int a = 10; int b = 0; int c = a / b;"
        tokens, _ = Lexer(source).tokenize()
        prog = Parser(tokens).parse_program()
        tac = generate_tac(prog)
        vm = TACInterpreter(tac)
        with self.assertRaises(RuntimeErrorObject) as ctx:
            vm.run()
        self.assertEqual(ctx.exception.code, "RUN001")

    def test_modulo_by_zero(self):
        source = "int a = 10; int b = 0; int c = a % b;"
        tokens, _ = Lexer(source).tokenize()
        prog = Parser(tokens).parse_program()
        tac = generate_tac(prog)
        vm = TACInterpreter(tac)
        with self.assertRaises(RuntimeErrorObject) as ctx:
            vm.run()
        self.assertEqual(ctx.exception.code, "RUN002")


if __name__ == "__main__":
    unittest.main()
