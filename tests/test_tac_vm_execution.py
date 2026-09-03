import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lexer import Lexer
from parser import Parser
from tac_generator import generate_tac
from tac_interpreter import TACInterpreter, RuntimeErrorObject


class TestTACVMExecution(unittest.TestCase):

    def test_successful_tac_execution(self):
        # Tests E & J: Successful TAC VM Execution Output
        source = """
        int x = 10;
        int y = 20;
        int sum = x + y;
        print(sum);
        """
        tokens, _ = Lexer(source).tokenize()
        prog = Parser(tokens).parse_program()
        tac = generate_tac(prog)
        tac_strs = [str(t) for t in tac]

        vm = TACInterpreter(tac_strs)
        output, final_vars, trace = vm.run()
        self.assertEqual(output, ["30"])
        self.assertEqual(final_vars["sum"], 30)
        self.assertGreater(len(trace), 0)

    def test_runtime_division_by_zero(self):
        # Test F: RUN001
        source = "int x = 10; int y = 0; print(x / y);"
        tokens, _ = Lexer(source).tokenize()
        prog = Parser(tokens).parse_program()
        tac = generate_tac(prog)
        tac_strs = [str(t) for t in tac]

        vm = TACInterpreter(tac_strs)
        with self.assertRaises(RuntimeErrorObject) as ctx:
            vm.run()
        self.assertEqual(ctx.exception.code, "RUN001")

    def test_runtime_modulo_by_zero(self):
        # Test G: RUN002
        source = "int x = 10; int y = 0; print(x % y);"
        tokens, _ = Lexer(source).tokenize()
        prog = Parser(tokens).parse_program()
        tac = generate_tac(prog)
        tac_strs = [str(t) for t in tac]

        vm = TACInterpreter(tac_strs)
        with self.assertRaises(RuntimeErrorObject) as ctx:
            vm.run()
        self.assertEqual(ctx.exception.code, "RUN002")

    def test_step_limit_infinite_loop_protection(self):
        # Test H: RUN003
        source = "int x = 1; while (x > 0) { print(x); }"
        tokens, _ = Lexer(source).tokenize()
        prog = Parser(tokens).parse_program()
        tac = generate_tac(prog)
        tac_strs = [str(t) for t in tac]

        vm = TACInterpreter(tac_strs, step_limit=100)
        with self.assertRaises(RuntimeErrorObject) as ctx:
            vm.run()
        self.assertEqual(ctx.exception.code, "RUN003")


if __name__ == "__main__":
    unittest.main()
