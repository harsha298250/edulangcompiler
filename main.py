#!/usr/bin/env python3
"""
EduLang Compiler — Student-Friendly Compiler that Explains Errors in Natural Language
Team 5

Pipeline: Source -> Lexer -> Parser -> Semantic Analyzer -> TAC Generator -> TAC Virtual Machine -> Error Explainer

Usage:
    python main.py <source_file.edu>
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
from lexer import Lexer
from parser import Parser, ParseError
from semantic import SemanticAnalyzer
from tac_generator import generate_tac
from tac_interpreter import TACInterpreter, RuntimeErrorObject
from error_explainer import explain


def compile_source(source, filename="<source>"):
    print(f"\n{'='*60}\nCompiling: {filename}\n{'='*60}")

    # ---- Phase 1: Lexical analysis ----
    lexer = Lexer(source)
    tokens, lex_errors = lexer.tokenize()

    if lex_errors:
        print(f"\n🔴 Found {len(lex_errors)} lexical error(s):\n")
        for err in lex_errors:
            print(explain(err))
            print()
        return False

    # ---- Phase 2: Syntax analysis ----
    parser = Parser(tokens)
    try:
        program = parser.parse_program()
    except ParseError as err:
        print("\n🔴 Found a syntax error:\n")
        print(explain(err))
        print()
        return False

    # ---- Phase 3: Semantic analysis ----
    analyzer = SemanticAnalyzer(program)
    sem_errors = analyzer.analyze()

    if sem_errors:
        print(f"\n🔴 Found {len(sem_errors)} semantic error(s):\n")
        for err in sem_errors:
            print(explain(err))
            print()
        return False

    print("\n✅ No static errors found — your program passed Lexer, Parser, and Semantic checks!")

    # ---- Phase 4: Code generation (Three-Address Code) ----
    tac = generate_tac(program)
    print(f"\n{'-'*60}\nGenerated Three-Address Code:\n{'-'*60}")
    for line in tac:
        print(f"   {line}")

    # ---- Phase 5: Execution (TAC Virtual Machine) ----
    print(f"\n{'-'*60}\nProgram Output (TAC Virtual Machine):\n{'-'*60}")
    try:
        vm = TACInterpreter(tac)
        output_lines, final_vars, _ = vm.run()
        if output_lines:
            for line in output_lines:
                print(f"   {line}")
        else:
            print("   (this program produced no output)")
        if final_vars:
            print(f"\n   Final variable state: {final_vars}")
    except RuntimeErrorObject as err:
        print("\n🔴 Runtime error encountered during execution:\n")
        print(explain(err))
        print()
        return False

    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <source_file.edu>")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r") as f:
        source = f.read()

    ok = compile_source(source, filename=path)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
