"""
Phase 3 Test Suite — UI/UX Polish, Pipeline Status Propagation, Empty State Handling,
Token Category Filtering, Line Inspector Mapping, and Deployment Safety.
"""

import os
import pytest
from lexer import Lexer, Token
from parser import Parser
from semantic import SemanticAnalyzer
from tac_generator import generate_tac
from tac_interpreter import TACInterpreter
from app import compile_pipeline, SAMPLE_CATEGORIES, SAMPLE_DIR
from ast_printer import find_ast_nodes_for_line


# ===========================================================================
# 1. Sample Category Organization Tests
# ===========================================================================
def test_sample_categories_organization():
    assert "--- BASIC EXAMPLES ---" in SAMPLE_CATEGORIES
    assert "--- CONTROL FLOW ---" in SAMPLE_CATEGORIES
    assert "--- ERROR DIAGNOSTICS ---" in SAMPLE_CATEGORIES

    total_samples = 0
    for cat_name, file_list in SAMPLE_CATEGORIES.items():
        assert len(file_list) > 0
        for filename in file_list:
            total_samples += 1
            sample_path = os.path.join(SAMPLE_DIR, filename)
            assert os.path.exists(sample_path), f"Sample file {filename} does not exist on disk"

    assert total_samples == 20


# ===========================================================================
# 2. Pipeline Status Propagation Tests
# ===========================================================================
def test_pipeline_status_propagation_lexical_failure():
    res = compile_pipeline("int x @ 10;")
    status = res["pipeline_status"]
    assert status["Lexer"] == "✗"
    assert status["Parser"] == "—"
    assert status["Semantic"] == "—"
    assert status["TAC Gen"] == "—"
    assert status["Execution"] == "—"
    assert res["error_category"] == "🟡 LEXICAL ERROR"


def test_pipeline_status_propagation_syntax_failure():
    res = compile_pipeline("int x = 10")
    status = res["pipeline_status"]
    assert status["Lexer"] == "✓"
    assert status["Parser"] == "✗"
    assert status["Semantic"] == "—"
    assert status["TAC Gen"] == "—"
    assert status["Execution"] == "—"
    assert res["error_category"] == "🔴 SYNTAX ERROR"


def test_pipeline_status_propagation_semantic_failure():
    res = compile_pipeline("y = 10;")
    status = res["pipeline_status"]
    assert status["Lexer"] == "✓"
    assert status["Parser"] == "✓"
    assert status["Semantic"] == "✗"
    assert status["TAC Gen"] == "—"
    assert status["Execution"] == "—"
    assert res["error_category"] == "🟠 SEMANTIC ERROR"


def test_pipeline_status_propagation_runtime_failure():
    res = compile_pipeline("int x = 10 / 0;")
    status = res["pipeline_status"]
    assert status["Lexer"] == "✓"
    assert status["Parser"] == "✓"
    assert status["Semantic"] == "✓"
    assert status["TAC Gen"] == "✓"
    assert status["Execution"] == "✗"
    assert res["error_category"] == "🟣 RUNTIME ERROR"


# ===========================================================================
# 3. Empty & Whitespace Code Safety Tests
# ===========================================================================
def test_empty_code_compilation_safety():
    res_empty = compile_pipeline("")
    assert res_empty["success"] is False
    assert res_empty["tokens"] == []
    assert res_empty["ast_obj"] is None

    res_spaces = compile_pipeline("   \n\t  ")
    assert res_spaces["success"] is False
    assert res_spaces["tokens"] == []


# ===========================================================================
# 4. Token Category Filtering Tests
# ===========================================================================
def test_token_category_filtering():
    code = "int count = 10;\nif (count > 5) { print(\"Hi\"); }"
    tokens, _ = Lexer(code).tokenize()

    keywords = [t for t in tokens if t.type in ("INT", "IF", "PRINT")]
    assert len(keywords) >= 3

    identifiers = [t for t in tokens if t.type == "IDENT"]
    assert any(t.value == "count" for t in identifiers)

    literals = [t for t in tokens if t.type in ("NUMBER_LIT", "STRING_LIT")]
    assert any(t.value == 10 for t in literals)
    assert any(t.value == "Hi" for t in literals)

    operators = [t for t in tokens if t.type in ("ASSIGN", "GT")]
    assert len(operators) >= 2

    punctuation = [t for t in tokens if t.type in ("SEMI", "LPAREN", "RPAREN", "LBRACE", "RBRACE")]
    assert len(punctuation) >= 5


# ===========================================================================
# 5. Line Inspector AST & TAC Mapping Tests
# ===========================================================================
def test_line_inspector_ast_and_tac_mapping():
    code = "int a = 10;\nint b = 20;\nint c = a + b;"
    res = compile_pipeline(code)

    assert res["ast_obj"] is not None
    line2_ast = find_ast_nodes_for_line(res["ast_obj"], 2)
    assert len(line2_ast) > 0
    assert any(getattr(n, "name", "") == "b" for n in line2_ast)

    assert len(res["tac"]) > 0
    line3_tac = [instr for instr in res["tac"] if getattr(instr, "line", None) == 3]
    assert len(line3_tac) > 0


# ===========================================================================
# 6. VM Step Safeguard Test
# ===========================================================================
def test_vm_step_safeguard():
    code = "int i = 1; while (i > 0) { i = i + 1; }"
    tokens, _ = Lexer(code).tokenize()
    ast = Parser(tokens).parse_program()
    tac = generate_tac(ast)
    vm = TACInterpreter(tac, step_limit=100)

    with pytest.raises(Exception) as exc_info:
        vm.run()
    assert getattr(exc_info.value, "code", None) == "RUN003"
