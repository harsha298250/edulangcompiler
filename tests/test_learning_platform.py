"""
Unit tests for EduLang Learning Platform modules:
Learning materials, practice challenges, quiz data, and structured error explanations.
"""

import pytest
from learning_materials import LESSONS
from practice_challenges import PRACTICE_CHALLENGES
from quiz_data import QUIZ_QUESTIONS
from error_explainer import explain_structured
from lexer import LexError, Lexer
from parser import ParseError, Parser
from semantic import SemError
from tac_interpreter import RuntimeErrorObject


def test_learning_lessons_structure():
    assert len(LESSONS) == 14
    for lesson in LESSONS:
        assert "id" in lesson
        assert "title" in lesson
        assert "category" in lesson
        assert "what" in lesson
        assert "why" in lesson
        assert "how" in lesson
        assert "code" in lesson


def test_practice_challenges_structure():
    assert len(PRACTICE_CHALLENGES) >= 7
    for challenge in PRACTICE_CHALLENGES:
        assert "id" in challenge
        assert "title" in challenge
        assert "category" in challenge
        assert "buggy_code" in challenge
        assert "hint" in challenge
        assert "solution_code" in challenge


def test_quiz_questions_structure():
    assert len(QUIZ_QUESTIONS) >= 6
    for q in QUIZ_QUESTIONS:
        assert "id" in q
        assert "question" in q
        assert "options" in q
        assert "correct" in q
        assert "explanation" in q
        assert 0 <= q["correct"] < len(q["options"])


def test_explain_structured_lexical():
    err = LexError("LEX001", 1, "Unexpected character '$'", {"char": "$"})
    structured = explain_structured(err)
    assert structured["title"] != ""
    assert structured["what"] != ""
    assert structured["why"] != ""
    assert structured["fix"] != ""
    assert structured["concept"] == "Lexical Analysis & Character Recognition"


def test_explain_structured_syntax():
    err = ParseError("SYN001", 3, "Missing semicolon")
    structured = explain_structured(err)
    assert structured["concept"] == "Syntax Analysis & Statement Termination"


def test_explain_structured_semantic():
    err = SemError("SEM001", 5, "Undeclared variable 'total'", {"name": "total", "declared_vars": []})
    structured = explain_structured(err)
    assert structured["concept"] == "Semantic Analysis & Symbol Table Resolution"


def test_explain_structured_runtime():
    err = RuntimeErrorObject("RUN001", 10, "Division by zero", {"op": "/"})
    structured = explain_structured(err)
    assert structured["concept"] == "Runtime Virtual Machine & Division Exception Safety"


def test_practice_challenges_compilation():
    for challenge in PRACTICE_CHALLENGES:
        lexer = Lexer(challenge["solution_code"])
        tokens, errors = lexer.tokenize()
        assert not errors, f"Solution for {challenge['id']} produced lexer errors"

        parser = Parser(tokens)
        ast = parser.parse_program()
        assert ast is not None, f"Solution for {challenge['id']} failed parsing"
