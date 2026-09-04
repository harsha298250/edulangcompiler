"""
Phase 4 Regression & Hardening Test Suite for EduLang v4.0.

Verifies:
1. Bug #1: Variables starting with 't' (total, temp, type, t, totalMarks) are preserved in final VM variable state while compiler temporaries (t0, t1) are filtered.
2. Bug #2: Self-referencing declarations (int x = x + 1;) fail in semantic analysis (SEM001) and never reach TAC execution.
3. Bug #3: Numeric equality comparisons (int == float, int != float) are semantically valid and execute accurately.
4. Bug #4: interpreter.py role documentation.
5. Final Validation Matrix (Tests 1 - 14).
"""

import pytest
from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer
from tac_generator import generate_tac
from tac_interpreter import TACInterpreter, is_temporary, RuntimeErrorObject
import interpreter


def run_pipeline(source_code):
    """Executes the full 5-stage backend compiler pipeline: Lexer -> Parser -> Semantic -> TAC -> VM."""
    lexer = Lexer(source_code)
    tokens, lex_errors = lexer.tokenize()
    if lex_errors:
        return None, None, lex_errors

    parser = Parser(tokens)
    ast = parser.parse_program()
    if parser.errors:
        return None, None, parser.errors

    analyzer = SemanticAnalyzer(ast)
    sem_errors = analyzer.analyze()
    if sem_errors:
        return None, None, sem_errors

    tac = generate_tac(ast)
    vm = TACInterpreter(tac)
    out, vars_, trace = vm.run()
    return out, vars_, []


def test_bug1_t_prefixed_variables_preserved():
    """Verify legitimate user variables starting with 't' are preserved in VM state."""
    code = """
    int total = 100;
    int temp = 200;
    int type = 300;
    int t = 400;
    int totalMarks = 500;
    print(total);
    print(temp);
    print(type);
    print(t);
    print(totalMarks);
    """
    out, vars_, errors = run_pipeline(code)
    assert errors == []
    assert out == ["100", "200", "300", "400", "500"]
    assert vars_["total"] == 100
    assert vars_["temp"] == 200
    assert vars_["type"] == 300
    assert vars_["t"] == 400
    assert vars_["totalMarks"] == 500


def test_bug1_is_temporary_helper():
    """Verify is_temporary helper correctly distinguishes temporaries from user variables."""
    assert is_temporary("t0") is True
    assert is_temporary("t1") is True
    assert is_temporary("t99") is True
    assert is_temporary("t1000") is True

    assert is_temporary("t") is False
    assert is_temporary("temp") is False
    assert is_temporary("total") is False
    assert is_temporary("type") is False
    assert is_temporary("time") is False
    assert is_temporary("test") is False
    assert is_temporary("totalMarks") is False


def test_bug2_self_referencing_declarations_fail_semantic():
    """Verify int x = x + 1 fails semantic analysis with SEM001 and does not execute."""
    for code in ["int x = x + 1;", "float x = x + 1.0;", "bool x = x;"]:
        lexer = Lexer(code)
        tokens, lex_err = lexer.tokenize()
        assert not lex_err

        parser = Parser(tokens)
        ast = parser.parse_program()
        assert not parser.errors

        analyzer = SemanticAnalyzer(ast)
        sem_err = analyzer.analyze()
        assert len(sem_err) > 0
        assert sem_err[0].code == "SEM001"


def test_bug2_parent_scope_resolution_and_shadowing():
    """Verify nested scopes and variable shadowing remain completely valid."""
    # Parent scope lookup
    code_scope = """
    int x = 10;
    {
        int y = x + 5;
        print(y);
    }
    """
    out, vars_, errors = run_pipeline(code_scope)
    assert not errors
    assert out == ["15"]

    # Shadowing
    code_shadow = """
    int x = 10;
    {
        int x = 20;
        print(x);
    }
    print(x);
    """
    out, vars_, errors = run_pipeline(code_shadow)
    assert not errors
    assert out == ["20", "10"]


def test_bug3_numeric_equality_coercion():
    """Verify int == float and int != float comparisons pass semantic analysis and execute."""
    code = """
    int a = 5;
    float b = 5.0;
    print(a == b);
    print(a != b);
    print(a < b);
    print(a <= b);
    print(a > b);
    print(a >= b);
    """
    out, vars_, errors = run_pipeline(code)
    assert not errors
    assert out == ["true", "false", "false", "true", "false", "true"]


def test_bug4_interpreter_module_docstring():
    """Verify interpreter.py docstring documents its teaching role."""
    doc = interpreter.__doc__
    assert "Alternative Tree-Walking Interpreter" in doc
    assert "teaching and reference implementation" in doc


# ============================================================
# FINAL VALIDATION MATRIX (Tests 1 - 14)
# ============================================================

def test_matrix_01_valid_program():
    out, vars_, errs = run_pipeline("int x = 10; print(x);")
    assert not errs
    assert out == ["10"]


def test_matrix_02_total_variable():
    out, vars_, errs = run_pipeline("int total = 100; print(total);")
    assert not errs
    assert out == ["100"]
    assert "total" in vars_


def test_matrix_03_temp_variable():
    out, vars_, errs = run_pipeline("int temp = 200; print(temp);")
    assert not errs
    assert out == ["200"]
    assert "temp" in vars_


def test_matrix_04_type_variable():
    out, vars_, errs = run_pipeline("int type = 300; print(type);")
    assert not errs
    assert out == ["300"]
    assert "type" in vars_


def test_matrix_05_t_variable():
    out, vars_, errs = run_pipeline("int t = 400; print(t);")
    assert not errs
    assert out == ["400"]
    assert "t" in vars_


def test_matrix_06_self_referencing():
    lexer = Lexer("int x = x + 1;")
    tokens, _ = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse_program()
    analyzer = SemanticAnalyzer(ast)
    sem_errs = analyzer.analyze()
    assert len(sem_errs) > 0
    assert sem_errs[0].code == "SEM001"


def test_matrix_07_nested_scope():
    out, vars_, errs = run_pipeline("int x = 10; { int y = x + 5; print(y); }")
    assert not errs
    assert out == ["15"]


def test_matrix_08_shadowing():
    out, vars_, errs = run_pipeline("int x = 10; { int x = 20; print(x); } print(x);")
    assert not errs
    assert out == ["20", "10"]


def test_matrix_09_float_division():
    out, vars_, errs = run_pipeline("float x = 5 / 2; print(x);")
    assert not errs
    assert out == ["2.5"]


def test_matrix_10_numeric_equality():
    out, vars_, errs = run_pipeline("int a = 5; float b = 5.0; print(a == b);")
    assert not errs
    assert out == ["true"]


def test_matrix_11_division_by_zero():
    lexer = Lexer("int x = 10; print(x / 0);")
    tokens, _ = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse_program()
    analyzer = SemanticAnalyzer(ast)
    sem_errs = analyzer.analyze()
    assert not sem_errs
    tac = generate_tac(ast)
    vm = TACInterpreter(tac)
    with pytest.raises(RuntimeErrorObject) as exc_info:
        vm.run()
    assert exc_info.value.code == "RUN001"


def test_matrix_12_invalid_lexical_character():
    lexer = Lexer("int x = 10 @ 5;")
    tokens, errs = lexer.tokenize()
    assert len(errs) > 0
    assert errs[0].code == "LEX001"


from parser import Parser, ParseError


def test_matrix_13_missing_semicolon():
    lexer = Lexer("int x = 10")
    tokens, _ = lexer.tokenize()
    parser = Parser(tokens)
    with pytest.raises(ParseError) as exc_info:
        parser.parse_program()
    assert exc_info.value.code == "SYN001"


def test_matrix_14_undeclared_variable():
    lexer = Lexer("print(unknownVariable);")
    tokens, _ = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse_program()
    analyzer = SemanticAnalyzer(ast)
    errs = analyzer.analyze()
    assert len(errs) > 0
    assert errs[0].code == "SEM001"


def test_uninitialized_declaration_and_assignment():
    """Verify int x; x = 10; print(x); succeeds with output 10."""
    out, vars_, errs = run_pipeline("int x; x = 10; print(x);")
    assert not errs
    assert out == ["10"]
    assert vars_["x"] == 10


def test_parent_scope_assignment():
    """Verify assigning to parent scope variable inside block updates parent variable."""
    out, vars_, errs = run_pipeline("int x = 10; { x = 20; } print(x);")
    assert not errs
    assert out == ["20"]
    assert vars_["x"] == 20


def test_malformed_parser_inputs_no_python_crash():
    """Verify malformed parser inputs raise ParseError cleanly without exposing Python tracebacks."""
    bad_codes = ["int x = ;", "int = 10;", "print(;", "if (x > 5) {"]
    for code in bad_codes:
        lexer = Lexer(code)
        tokens, _ = lexer.tokenize()
        parser = Parser(tokens)
        with pytest.raises(ParseError):
            parser.parse_program()


def test_nested_empty_blocks_safety():
    """Verify nested empty blocks { { } } parse, analyze semantically, and execute safely."""
    out, vars_, errs = run_pipeline("{ { } }")
    assert not errs
    assert out == []


def test_escaped_strings_handling():
    """Verify escaped quotes and string literal output."""
    out, vars_, errs = run_pipeline('string s = "hello"; print(s);')
    assert not errs
    assert out == ["hello"]
    assert vars_["s"] == "hello"


def test_escaped_quotes_and_concatenation():
    """Verify escaped quotes and string concatenation."""
    code_quote = r'string s = "He said \"hi\""; print(s);'
    out, vars_, errs = run_pipeline(code_quote)
    assert not errs
    assert out == ['He said "hi"']
    assert vars_["s"] == 'He said "hi"'

    code_concat = 'string a = "Hello"; string b = "EduLang"; string c = a + b; print(c);'
    out2, vars2, errs2 = run_pipeline(code_concat)
    assert not errs2
    assert out2 == ["HelloEduLang"]
    assert vars2["c"] == "HelloEduLang"

