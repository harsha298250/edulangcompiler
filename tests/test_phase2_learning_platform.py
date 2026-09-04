"""
Phase 2 Comprehensive Test Suite for EduLang Learning Platform
Covers Interactive Token Explanations, AST Inspection, Scope Lookup Simulation,
Variable Shadowing Detection, TAC Instruction Explanations, Pipeline Stages,
Error Learning Navigation, Lessons, Hints, Quiz Data, and Regression Safety.
"""

import pytest
from lexer import Lexer, Token, explain_token
from parser import Parser, VarDecl, Assign, Print, If, While, Block, BinOp, Literal, VarRef
from semantic import SemanticAnalyzer, Scope, find_shadowed_variables
from tac_generator import generate_tac, explain_tac_instruction
from error_explainer import get_lesson_id_for_error, get_practice_category_for_error
from ast_printer import get_all_ast_nodes, explain_ast_node
from app import compile_pipeline
from learning_materials import LESSONS
from practice_challenges import PRACTICE_CHALLENGES
from quiz_data import QUIZ_QUESTIONS


# ===========================================================================
# 1. Interactive Token Learning Tests
# ===========================================================================
def test_token_explanations():
    tok_kw = Token("INT", "int", line=1, col=1)
    exp_kw = explain_token(tok_kw)
    assert exp_kw["type"] == "INT"
    assert "Type Keyword" in exp_kw["what"]

    tok_id = Token("IDENT", "total", line=1, col=5)
    exp_id = explain_token(tok_id)
    assert exp_id["type"] == "IDENT"
    assert "Identifier" in exp_id["what"]
    assert "Symbol Table" in exp_id["where"]

    tok_num = Token("NUMBER_LIT", 100, line=1, col=11)
    exp_num = explain_token(tok_num)
    assert exp_num["type"] == "NUMBER_LIT"
    assert "Integer Literal" in exp_num["what"]

    tok_str = Token("STRING_LIT", "hello", line=2, col=1)
    exp_str = explain_token(tok_str)
    assert exp_str["type"] == "STRING_LIT"
    assert "hello" in exp_str["what"]


# ===========================================================================
# 2. AST Inspection & Source Mapping Tests
# ===========================================================================
def test_ast_node_inspection_and_explanation():
    code = "int x = 10; if (x > 5) { print(x); }"
    tokens, _ = Lexer(code).tokenize()
    ast = Parser(tokens).parse_program()
    all_nodes = get_all_ast_nodes(ast)

    assert len(all_nodes) > 0
    node_types = [type(n).__name__ for n in all_nodes]
    assert "Program" in node_types
    assert "VarDecl" in node_types
    assert "If" in node_types
    assert "Block" in node_types

    var_node = next(n for n in all_nodes if isinstance(n, VarDecl))
    meta_var = explain_ast_node(var_node)
    assert meta_var["type"] == "Variable Declaration (VarDecl)"
    assert "x" in meta_var["label"]
    assert "Line 1" in meta_var["line"]

    if_node = next(n for n in all_nodes if isinstance(n, If))
    meta_if = explain_ast_node(if_node)
    assert meta_if["type"] == "Conditional Branch (If)"


# ===========================================================================
# 3. Scope Lookup Simulation & Shadowing Tests
# ===========================================================================
def test_scope_lookup_trace_and_shadowing():
    global_scope = Scope("Global Scope")
    global_scope.declare("g_var", "int")

    block_scope = Scope("Block Scope (Line 2)", parent=global_scope)
    block_scope.declare("b_var", "float")

    inner_block = Scope("Block Scope (Line 4)", parent=block_scope)
    inner_block.declare("g_var", "string")  # Shadowing g_var!

    # Test Shadowing Detection
    shadowed = find_shadowed_variables(global_scope)
    assert len(shadowed) == 1
    assert shadowed[0]["var_name"] == "g_var"
    assert shadowed[0]["inner_scope"] == "Block Scope (Line 4)"
    assert shadowed[0]["outer_scope"] == "Global Scope"

    # Test Lookup Simulation Trace
    t_found, trace_local = inner_block.resolve_with_trace("b_var")
    assert t_found == "float"
    assert len(trace_local) == 2
    assert not trace_local[0]["found"]  # Not in inner block
    assert trace_local[1]["found"]      # Found in parent block scope

    t_shadow, trace_shadow = inner_block.resolve_with_trace("g_var")
    assert t_shadow == "string"
    assert trace_shadow[0]["found"]     # Found directly in inner block scope


# ===========================================================================
# 4. TAC Learning & Instruction Explanation Tests
# ===========================================================================
def test_tac_instruction_explanations():
    code = "int a = 10 + 20; print(a);"
    res = compile_pipeline(code)
    tac = res["tac"]
    exps = res["tac_explanations"]

    assert len(tac) > 0
    assert len(exps) == len(tac)

    decl_exp = next(e for t, e in zip(tac, exps) if str(t).startswith("DECL"))
    assert "Declare new local variable" in decl_exp

    print_exp = next(e for t, e in zip(tac, exps) if str(t).startswith("PRINT"))
    assert "Print the value" in print_exp


# ===========================================================================
# 5. Compiler Pipeline Stage Navigation Tests
# ===========================================================================
def test_pipeline_stages_and_partial_execution():
    code = "int x = 5;"

    res_lexer = compile_pipeline(code, max_stage=1)
    assert res_lexer["pipeline_status"]["Lexer"] == "✓"
    assert res_lexer["pipeline_status"]["Parser"] == "○"

    res_parser = compile_pipeline(code, max_stage=2)
    assert res_parser["pipeline_status"]["Parser"] == "✓"
    assert res_parser["pipeline_status"]["Semantic"] == "○"

    res_full = compile_pipeline(code, max_stage=5)
    assert res_full["pipeline_status"]["Execution"] == "✓"
    assert res_full["success"] is True


# ===========================================================================
# 6. Error Learning Navigation Tests
# ===========================================================================
def test_error_learning_navigation():
    res_lex = compile_pipeline("int x @ 10;")
    assert get_lesson_id_for_error(res_lex["error_obj"]) == "2_lexer"
    assert get_practice_category_for_error(res_lex["error_obj"]) == "Lexical Analysis"

    res_syn = compile_pipeline("int x = 10")
    assert get_lesson_id_for_error(res_syn["error_obj"]) == "4_syntax"
    assert get_practice_category_for_error(res_syn["error_obj"]) == "Syntax Analysis"

    res_sem = compile_pipeline("y = 10;")
    assert get_lesson_id_for_error(res_sem["error_obj"]) == "9_symbol_table"
    assert get_practice_category_for_error(res_sem["error_obj"]) == "Semantic Analysis"

    res_run = compile_pipeline("int x = 10 / 0;")
    assert get_lesson_id_for_error(res_run["error_obj"]) == "13_vm"
    assert get_practice_category_for_error(res_run["error_obj"]) == "Runtime / Execution"


# ===========================================================================
# 7. Curriculum Lessons & Exercises Tests
# ===========================================================================
def test_curriculum_lessons_structure():
    assert len(LESSONS) == 14
    for lesson in LESSONS:
        assert "id" in lesson
        assert "title" in lesson
        assert "level" in lesson
        assert "concept" in lesson
        assert "code" in lesson
        assert "exercise" in lesson
        ex = lesson["exercise"]
        assert len(ex["options"]) == 4
        assert 0 <= ex["answer"] < 4


# ===========================================================================
# 8. Practice Arena Hints & Solutions Tests
# ===========================================================================
def test_practice_challenges_and_hints():
    assert len(PRACTICE_CHALLENGES) >= 7
    for challenge in PRACTICE_CHALLENGES:
        assert "id" in challenge
        assert "difficulty" in challenge
        assert "hints" in challenge
        assert len(challenge["hints"]) == 3

        # Solved code must compile cleanly
        sol_res = compile_pipeline(challenge["solution_code"])
        assert sol_res["error_category"] == challenge["expected_category"]


# ===========================================================================
# 9. Quiz Data Categories & Scoring Tests
# ===========================================================================
def test_quiz_questions_data():
    assert len(QUIZ_QUESTIONS) >= 8
    for q in QUIZ_QUESTIONS:
        assert "id" in q
        assert "category" in q
        assert "question" in q
        assert len(q["options"]) == 4
        assert 0 <= q["correct"] < 4
        assert "explanation" in q
