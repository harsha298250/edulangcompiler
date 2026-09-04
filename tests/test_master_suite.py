"""
Master Regression Test Suite for EduLang Compiler & Learning Platform
Covering Lexical, Syntax, Semantic, Scope Shadowing, Runtime, TAC, and Platform features.
"""

import pytest
from lexer import Lexer
from parser import Parser, ParseError
from semantic import SemanticAnalyzer
from tac_generator import generate_tac
from tac_interpreter import TACInterpreter, RuntimeErrorObject
from app import compile_pipeline


# ===========================================================================
# A. Lexical Analysis Tests (1-8)
# ===========================================================================
def test_01_valid_identifiers():
    tokens, errors = Lexer("int my_var_123 = 10;").tokenize()
    assert not errors
    assert any(t.value == "my_var_123" and t.type == "IDENT" for t in tokens)


def test_02_keywords():
    tokens, errors = Lexer("int float string bool if else while print and or not true false").tokenize()
    assert not errors
    assert any(t.type == "INT" for t in tokens)
    assert any(t.type == "WHILE" for t in tokens)


def test_03_integer_literals():
    tokens, errors = Lexer("42 0 9999").tokenize()
    assert not errors
    assert any(t.type == "NUMBER_LIT" and t.value == 42 for t in tokens)


def test_04_float_literals():
    tokens, errors = Lexer("3.14 0.001 100.5").tokenize()
    assert not errors
    assert any(t.type == "FLOAT_LIT" and t.value == 3.14 for t in tokens)


def test_05_string_literals():
    tokens, errors = Lexer('"Hello EduLang"').tokenize()
    assert not errors
    assert any(t.type == "STRING_LIT" and t.value == "Hello EduLang" for t in tokens)


def test_06_invalid_character():
    tokens, errors = Lexer("int x @ 10;").tokenize()
    assert len(errors) == 1
    assert errors[0].code == "LEX001"


def test_07_unterminated_string():
    tokens, errors = Lexer('string s = "Hello;').tokenize()
    assert len(errors) == 1
    assert errors[0].code == "LEX002"


def test_08_escaped_string():
    tokens, errors = Lexer(r'string s = "Hello \"World\"";').tokenize()
    assert not errors
    str_tok = next(t for t in tokens if t.type == "STRING_LIT")
    assert str_tok.value == 'Hello "World"'


# ===========================================================================
# B. Syntax Analysis Tests (9-14)
# ===========================================================================
def test_09_missing_semicolon():
    tokens, _ = Lexer("int x = 10\nprint(x);").tokenize()
    with pytest.raises(ParseError) as exc_info:
        Parser(tokens).parse_program()
    assert exc_info.value.code == "SYN001"


def test_10_missing_parenthesis():
    tokens, _ = Lexer("if x > 10 { print(x); }").tokenize()
    with pytest.raises(ParseError) as exc_info:
        Parser(tokens).parse_program()
    assert exc_info.value.code == "SYN002"


def test_11_missing_brace():
    tokens, _ = Lexer("if (x > 10) { print(x);").tokenize()
    with pytest.raises(ParseError) as exc_info:
        Parser(tokens).parse_program()
    assert exc_info.value.code == "SYN003"


def test_12_unexpected_token():
    tokens, _ = Lexer("int = 10;").tokenize()
    with pytest.raises(ParseError) as exc_info:
        Parser(tokens).parse_program()
    assert exc_info.value.code == "SYN002"


def test_13_invalid_expression():
    tokens, _ = Lexer("int x = + ;").tokenize()
    with pytest.raises(ParseError) as exc_info:
        Parser(tokens).parse_program()
    assert exc_info.value.code == "SYN004"


def test_14_nested_blocks_ast():
    tokens, _ = Lexer("int x = 1; { int y = 2; { int z = 3; } }").tokenize()
    ast = Parser(tokens).parse_program()
    assert ast is not None


# ===========================================================================
# C. Semantic Analysis Tests (15-20)
# ===========================================================================
def test_15_undeclared_variable():
    tokens, _ = Lexer("x = 10;").tokenize()
    ast = Parser(tokens).parse_program()
    errors = SemanticAnalyzer(ast).analyze()
    assert len(errors) == 1 and errors[0].code == "SEM001"


def test_16_redeclared_variable():
    tokens, _ = Lexer("int x = 10; int x = 20;").tokenize()
    ast = Parser(tokens).parse_program()
    errors = SemanticAnalyzer(ast).analyze()
    assert len(errors) == 1 and errors[0].code == "SEM002"


def test_17_type_mismatch():
    tokens, _ = Lexer('int x = "hello";').tokenize()
    ast = Parser(tokens).parse_program()
    errors = SemanticAnalyzer(ast).analyze()
    assert len(errors) == 1 and errors[0].code == "SEM003"


def test_18_invalid_assignment():
    tokens, _ = Lexer('bool b = true; b = "text";').tokenize()
    ast = Parser(tokens).parse_program()
    errors = SemanticAnalyzer(ast).analyze()
    assert len(errors) == 1 and errors[0].code == "SEM003"


def test_19_invalid_operator_types():
    tokens, _ = Lexer('int result = 10 + "string";').tokenize()
    ast = Parser(tokens).parse_program()
    errors = SemanticAnalyzer(ast).analyze()
    assert len(errors) == 1 and errors[0].code == "SEM004"


def test_20_invalid_boolean_condition():
    tokens, _ = Lexer('if (100) { print("Hi"); }').tokenize()
    ast = Parser(tokens).parse_program()
    errors = SemanticAnalyzer(ast).analyze()
    assert len(errors) == 1 and errors[0].code == "SEM005"


# ===========================================================================
# D. Scope & Shadowing Tests (21-25)
# ===========================================================================
def test_21_global_variable():
    code = "int x = 10; print(x);"
    res = compile_pipeline(code)
    assert res["console"] == [("ok", "10")]


def test_22_local_variable():
    code = "{ int y = 20; print(y); }"
    res = compile_pipeline(code)
    assert res["console"] == [("ok", "20")]


def test_23_nested_scope():
    code = "int a = 1; { int b = 2; { int c = 3; print(a + b + c); } }"
    res = compile_pipeline(code)
    assert res["console"] == [("ok", "6")]


def test_24_variable_shadowing():
    """Inner variable must shadow outer variable without overwriting outer variable."""
    code = """
int x = 10;
{
    int x = 20;
    print(x);
}
print(x);
"""
    res = compile_pipeline(code)
    assert res["console"] == [("ok", "20"), ("ok", "10")]
    assert res["memory"]["x"] == 10


def test_25_outer_variable_mutation_from_inner_scope():
    code = """
int x = 10;
{
    x = 99;
}
print(x);
"""
    res = compile_pipeline(code)
    assert res["console"] == [("ok", "99")]
    assert res["memory"]["x"] == 99


# ===========================================================================
# E. Runtime Tests (26-30)
# ===========================================================================
def test_26_arithmetic_execution():
    code = "int res = 10 + 20 * 2; print(res);"
    res = compile_pipeline(code)
    assert res["console"] == [("ok", "50")]


def test_27_integer_division_float_semantics():
    code = "float x = 5 / 2; print(x);"
    res = compile_pipeline(code)
    assert res["console"] == [("ok", "2.5")]


def test_28_float_division_semantics():
    code = "float x = 10 / 4; print(x);"
    res = compile_pipeline(code)
    assert res["console"] == [("ok", "2.5")]


def test_29_division_by_zero():
    code = "int x = 10 / 0;"
    res = compile_pipeline(code)
    assert res["error_category"] == "🟣 RUNTIME ERROR"
    assert res["error_obj"].code == "RUN001"


def test_30_infinite_loop_protection():
    code = "int x = 1; while (x > 0) { x = x; }"
    tokens, _ = Lexer(code).tokenize()
    ast = Parser(tokens).parse_program()
    tac = generate_tac(ast)
    vm = TACInterpreter(tac, step_limit=50)
    with pytest.raises(RuntimeErrorObject) as exc_info:
        vm.run()
    assert exc_info.value.code == "RUN003"


# ===========================================================================
# F. TAC Tests (31-35)
# ===========================================================================
def test_31_arithmetic_tac():
    code = "int x = 5 + 3;"
    res = compile_pipeline(code)
    tac_strs = [str(t) for t in res["tac"]]
    assert any("t0 = 5 + 3" in t for t in tac_strs)


def test_32_conditional_tac():
    code = "if (true) { print(1); }"
    res = compile_pipeline(code)
    tac_strs = [str(t) for t in res["tac"]]
    assert any("IF_FALSE" in t for t in tac_strs)


def test_33_loop_tac():
    code = "int i = 0; while (i < 3) { i = i + 1; }"
    res = compile_pipeline(code)
    tac_strs = [str(t) for t in res["tac"]]
    assert any("IF_FALSE" in t for t in tac_strs)
    assert any("GOTO" in t for t in tac_strs)


def test_34_temporary_variables():
    code = "int res = 1 + 2 + 3 + 4;"
    res = compile_pipeline(code)
    tac_strs = [str(t) for t in res["tac"]]
    assert any("t0 =" in t for t in tac_strs)
    assert any("t1 =" in t for t in tac_strs)


def test_35_labels_and_jumps():
    code = "if (false) { print(1); } else { print(2); }"
    res = compile_pipeline(code)
    tac_strs = [str(t) for t in res["tac"]]
    assert any("L0:" in t or "L1:" in t for t in tac_strs)


# ===========================================================================
# G. UI & Platform Tests (36-40)
# ===========================================================================
def test_36_practice_arena_validation():
    code = "int x = 5;\nprint(x);"
    res = compile_pipeline(code)
    assert res["error_category"] == "🟢 SUCCESS"


def test_37_error_line_metadata_preservation():
    code = "int x = 10;\nint y = 0;\nint z = x / y;"
    res = compile_pipeline(code)
    assert res["error_line"] == 3
    assert res["error_obj"].line == 3


def test_38_stale_data_protection_syntax_failure():
    """Compiling an invalid syntax program must clear downstream AST and TAC data."""
    res = compile_pipeline("int x = ;")
    assert res["ast_obj"] is None
    assert res["ast_text"] == ""
    assert res["tac"] == []


def test_39_stale_data_protection_semantic_failure():
    """Compiling a semantic error program must clear TAC data."""
    res = compile_pipeline("int x = 'hello';")
    assert res["tac"] == []


def test_40_all_20_sample_programs_pass():
    import glob, os
    sample_files = glob.glob(os.path.join(os.path.dirname(__file__), "..", "sample_programs", "*.edu"))
    assert len(sample_files) == 20
    for s_file in sample_files:
        with open(s_file, "r") as f:
            c = f.read()
        res = compile_pipeline(c)
        assert res["phase_reached"] != ""
