# EduLang: A Student-Friendly Compiler That Explains Errors in Natural Language
## Project Final Academic Submission Report & Presentation Guide (v4.0 Final)

**Team 5**:
1. **H. Harshavardhan** (Register No: 192521171) — *Module: Lexical Analysis & Tokenization*
2. **R. Sivasakthi** (Register No: 192521147) — *Module: Syntax Analysis & AST Construction*
3. **Santhosh G** (Register No: 192521035) — *Module: Semantic Analysis & Symbol Tables*
4. **Sivadharshini** (Register No: 192521261) — *Module: Three-Address Code Generation & VM Execution*
5. **Chithirai Selvan B** (Register No: 192521263) — *Module: Natural-Language Error Explainer & Web IDE*

---

## 1. ABSTRACT & EXECUTIVE SUMMARY

High-level programming languages rely on compilers to translate human-readable source code into machine instructions. However, standard production compilers produce cryptic error diagnostics (e.g. `syntax error near line 4`, `type mismatch in binary expression`) that intimidate novice students. **EduLang** is an interactive, web-based educational compiler and learning laboratory designed to bridge this pedagogical gap.

EduLang executes a complete, genuine 5-stage compilation pipeline:
$$\text{Source Code} \longrightarrow \text{Lexer} \longrightarrow \text{Parser (AST)} \longrightarrow \text{Semantic Analyzer (Scopes)} \longrightarrow \text{TAC Generator} \longrightarrow \text{TAC VM}$$

Unlike traditional compilers or black-box educational IDEs, EduLang makes every intermediate representation visible and interactive while providing plain-English error explanations with typo suggestions, corrective code hints, line location pointers, and integrated curriculum lessons.

---

## 2. PROBLEM STATEMENT & OBJECTIVES

### Problem Statement
1. **Cryptic Diagnostics**: Standard compiler error messages assume deep expertise and fail to explain *why* an error occurred or *how* to fix it.
2. **Opaque Transformations**: Students cannot observe how high-level code converts into intermediate representations (tokens, ASTs, scope symbols, Three-Address Code).
3. **Static Learning Materials**: Conventional textbooks separate theoretical compiler theory from live practical execution.

### Key Project Objectives
- Construct a 100% deterministic Python compiler pipeline without external LLM dependencies.
- Build interactive visualizers for Tokens, Abstract Syntax Trees, Scoped Symbol Tables, Three-Address Code, and VM Execution step debugging.
- Implement a Natural-Language Error Explainer converting diagnostic codes (`LEX001`, `SYN001`, `SEM001`, `RUN001`) into structured cards with typo suggestions (Levenshtein distance).
- Provide an integrated learning platform featuring a 10-stage pipeline walkthrough, 14 curriculum lessons, multi-tier hint practice challenges, and knowledge assessment quizzes.

---

## 3. SYSTEM ARCHITECTURE & COMPILER PIPELINE

```
                        +----------------------------+
                        |     EduLang Source Code    |
                        +----------------------------+
                                      |
                                      v
                        +----------------------------+
                        |  Lexer (Scanner / Tokens)  |
                        +----------------------------+
                                      |
                                      v
                        +----------------------------+
                        |   Parser (Recursive-Descent) |
                        +----------------------------+
                                      |
                                      v
                        +----------------------------+
                        | Abstract Syntax Tree (AST) |
                        +----------------------------+
                                      |
                                      v
                        +----------------------------+
                        |  Semantic Analyzer (Scopes) |
                        +----------------------------+
                                      |
                                      v
                        +----------------------------+
                        |     TAC Generator (IR)     |
                        +----------------------------+
                                      |
                                      v
                        +----------------------------+
                        |   TAC Virtual Machine (VM) |
                        +----------------------------+
                                      |
                                      v
                        +----------------------------+
                        |     Stdout Console Output  |
                        +----------------------------+

DIAGNOSTIC PATH:
Compiler Exception -> Error Explainer -> Structured Explanation Card -> Lesson / Practice Links
```

### Pipeline Components:
1. **Lexical Analyzer (`lexer.py`)**: Converts raw source text into structured `Token(type, value, line, col)` objects. Discards whitespace and comments (`#`).
2. **Syntax Analyzer (`parser.py`)**: Recursive-descent parser verifying grammar rules and building the AST. Implements error recovery via statement boundary synchronization.
3. **Semantic Analyzer (`semantic.py`)**: Traverses the AST, enforces static typing, manages block scope hierarchies (`Scope`), detects variable shadowing, and resolves symbols.
4. **TAC Generator (`tac_generator.py`)**: Flattens nested expressions into linear Three-Address Code instructions with temporaries (`t0`, `t1`) and control flow labels (`L0`, `L1`).
5. **TAC Virtual Machine (`tac_interpreter.py`)**: Executes TAC instructions with Program Counter (`PC`) step debugging, stack frames, and runtime exception handling (`RUN001` - Division by Zero, `RUN003` - Step Safeguard).
6. **Error Explainer (`error_explainer.py`)**: Formats error diagnostics into natural language with *What*, *Why*, *How to fix*, *Concept*, and Levenshtein typo suggestions.

---

## 4. SUPPORTED EDULANG LANGUAGE SPECIFICATION

| Language Feature | Specification / Syntax Example |
| :--- | :--- |
| **Data Types** | `int`, `float`, `string`, `bool` |
| **Variables** | `int x = 10;`, `float pi = 3.14;`, `string s = "EduLang";` |
| **Operators** | Arithmetic (`+`, `-`, `*`, `/`, `%`), Comparison (`==`, `!=`, `<`, `>`, `<=`, `>=`), Logical (`and`, `or`, `not`) |
| **Control Flow** | `if (cond) { ... } else { ... }`, `while (cond) { ... }` |
| **Output** | `print(expression);` |
| **Scoping** | Lexical Block Scoping `{ ... }` with inner scope variable shadowing |
| **Comments** | Single-line comments starting with `#` |

---

## 5. COMPILER CORRECTNESS VALIDATION MATRIX

| Test Scenario | Sample Program Code | Expected Output / Result | Status |
| :--- | :--- | :--- | :--- |
| **1. Basic Output** | `int x = 10; print(x);` | `10` | PASS |
| **2. Arithmetic** | `int a = 10; int b = 20; print(a + b);` | `30` | PASS |
| **3. Float Division** | `float x = 5 / 2; print(x);` | `2.5` | PASS |
| **4. Scoping & Shadowing** | `int x = 10; { int x = 20; print(x); } print(x);` | `20`<br>`10` | PASS |
| **5. Loop Execution** | `int x = 0; while (x < 3) { print(x); x = x + 1; }` | `0`<br>`1`<br>`2` | PASS |
| **6. Lexical Error** | `int price@ = 100;` | `🟡 LEXICAL ERROR (LEX001)` | PASS |
| **7. Syntax Error** | `int x = 10` | `🔴 SYNTAX ERROR (SYN001)` | PASS |
| **8. Semantic Error** | `print(unknownVar);` | `🟠 SEMANTIC ERROR (SEM001)` | PASS |
| **9. Runtime Error** | `int x = 10 / 0;` | `🟣 RUNTIME ERROR (RUN001)` | PASS |

---

## 6. INDIVIDUAL TEAM CONTRIBUTIONS

### 1. H. Harshavardhan (Register No: 192521171) — *Lexical Analysis*
- Developed `Lexer` in [`lexer.py`](file:///c:/Users/harsh/Downloads/edulang_compiler_webui_FIXED/edulang_compiler/lexer.py), tracking exact line numbers and column positions (`col`).
- Implemented token classification rules for keywords, identifiers, numeric literals, floats, string literals with escape sequences, operators, and comments (`#`).
- Authored dynamic token explanation generator `explain_token()`.

### 2. R. Sivasakthi (Register No: 19252147) — *Syntax Analysis & AST*
- Designed recursive-descent `Parser` in [`parser.py`](file:///c:/Users/harsh/Downloads/edulang_compiler_webui_FIXED/edulang_compiler/parser.py) implementing operator precedence climbing for arithmetic, logical, and comparison expressions.
- Constructed AST node hierarchy (`VarDecl`, `Assign`, `Print`, `If`, `While`, `Block`, `BinOp`, `UnaryOp`, `Literal`, `VarRef`).
- Implemented `ast_printer.py` formatter, line anchor mapping, and `explain_ast_node()`.

### 3. Santhosh G (Register No: 192521035) — *Semantic Analysis & Scopes*
- Built `SemanticAnalyzer` and `Scope` hierarchy in [`semantic.py`](file:///c:/Users/harsh/Downloads/edulang_compiler_webui_FIXED/edulang_compiler/semantic.py).
- Implemented type safety rules, variable declaration checks, assignment compatibility, and boolean condition verification.
- Developed `resolve_with_trace()` lookup simulator and `find_shadowed_variables()` detector.

### 4. Sivadharshini (Register No: 192521261) — *Code Generation & Execution*
- Developed Three-Address Code generator `generate_tac()` in [`tac_generator.py`](file:///c:/Users/harsh/Downloads/edulang_compiler_webui_FIXED/edulang_compiler/tac_generator.py) with source line metadata binding.
- Implemented `TACInterpreter` Virtual Machine in [`tac_interpreter.py`](file:///c:/Users/harsh/Downloads/edulang_compiler_webui_FIXED/edulang_compiler/tac_interpreter.py) with Program Counter (`PC`) step tracing and stack frame scope management.
- Authored natural-language TAC instruction explainer `explain_tac_instruction()`.

### 5. Chithirai Selvan B (Register No: 192521263) — *Error Explainer & Web IDE*
- Designed `error_explainer.py` formatting diagnostic codes into structured educational cards with Levenshtein typo suggestions.
- Built interactive Streamlit Web UI ([`app.py`](file:///c:/Users/harsh/Downloads/edulang_compiler_webui_FIXED/edulang_compiler/app.py)) featuring 7 platform modes, categorized sample loader, token filters, step-by-step pipeline mode, hints system, quiz mode, and error shortcuts.

---

## 7. AUTOMATED TEST SUITE & METRICS SUMMARY

- **Total Automated Tests**: **121 / 121 PASSED (100%)**
- **Execution Time**: **2.93 seconds**
- **Test File Distribution**:
  - `test_master_suite.py`: 40 tests
  - `test_phase4_bug_fixes.py`: 26 tests
  - `test_phase3_ui_and_performance.py`: 10 tests
  - `test_phase2_learning_platform.py`: 9 tests
  - `test_learning_platform.py`: 8 tests
  - `test_semantic.py`: 5 tests
  - `test_tac_vm_execution.py`: 4 tests
  - `test_error_explainer.py`: 3 tests
  - `test_lexer.py`: 3 tests
  - `test_parser.py`: 3 tests
  - `test_tac_generator.py`: 3 tests
  - `test_tac_vm.py`: 3 tests
  - `test_typo_suggestions.py`: 3 tests
  - `test_scope_hierarchy.py`: 1 test
  - `test_tac_line_mapping.py`: 1 test

---

## 8. VIVA VOCE QUESTION & ANSWER GUIDE

**Q1: What is EduLang?**  
*Answer*: EduLang is a student-friendly educational compiler and web learning laboratory. It executes a complete 5-stage Python compiler pipeline (Lexer → Parser → Semantic Analyzer → TAC Generator → TAC VM) and presents every stage interactively while explaining errors in plain English.

**Q2: What parsing technique is used in EduLang?**  
*Answer*: EduLang uses a Top-Down Recursive-Descent Parser. Each grammar production rule corresponds to a parsing method (`parse_decl`, `parse_if`, `parse_expr`), and operator precedence is handled via precedence climbing.

**Q3: How does scope resolution work in EduLang?**  
*Answer*: Scopes are represented as hierarchical `Scope` tree objects linked to parent scopes. When resolving a variable, EduLang searches the current block scope first; if not found, it traverses upward to parent scopes until reaching the Global Scope.

**Q4: What is Three-Address Code (TAC)?**  
*Answer*: TAC is an Intermediate Representation (IR) where each instruction has at most one operator and three operand addresses. Complex nested expressions like `x = (a + b) * c` are flattened into linear primitives using temporary variables (`t0 = a + b`, `t1 = t0 * c`, `x = t1`).

**Q5: How does the Error Explainer offer typo suggestions?**  
*Answer*: When an undeclared variable or keyword error occurs, EduLang calculates the Levenshtein edit distance between the misspelled token and valid candidates, suggesting *"Did you mean 'count'?"* if the distance is within threshold limits.

---

## 9. PRESENTATION (PPT) SLIDE OUTLINE

- **Slide 1**: Title Slide (EduLang Compiler & Learning Platform, Team Members, Registration Numbers).
- **Slide 2**: Problem Statement & Project Motivation.
- **Slide 3**: Project Objectives & Key Features.
- **Slide 4**: EduLang System Architecture & Compiler Pipeline.
- **Slide 5**: Lexical Analysis & Token Inspector.
- **Slide 6**: Syntax Analysis & AST Construction.
- **Slide 7**: Semantic Analysis & Scoped Symbol Tables.
- **Slide 8**: Intermediate Representation (Three-Address Code).
- **Slide 9**: TAC Virtual Machine & Step Debugger.
- **Slide 10**: Natural-Language Error Explainer & Caret Pointers.
- **Slide 11**: Integrated Learning Platform (Pipeline Mode, Curriculum, Practice, Quiz).
- **Slide 12**: Automated Test Results & Verification Metrics (95 / 95 Passed).
- **Slide 13**: Team Member Contributions.
- **Slide 14**: Conclusion & Demonstration.
