# EduLang – An Interactive Compiler Design & Programming Learning Platform
**Team 5**

A full-fledged teaching compiler, Web IDE, and interactive learning platform for EduLang that catches lexical, syntax, semantic, and runtime errors, explaining each diagnostic in natural language with compiler design concepts and actionable fixes.

---

## 🚀 How to Run

### 1. Interactive Web IDE & Learning Platform (Streamlit UI)
```bash
python -m streamlit run app.py
```
Open **http://localhost:8501** in your browser.

### 2. CLI Runner
```bash
python main.py sample_programs/01_valid_arithmetic.edu
```

### 3. Automated Test Suite (120 Automated Tests — 100% Passing)
```bash
python -m pytest
```

---

## 🏛️ Platform Modes & Features

1. **`💻 IDE & Visualizer Mode`**:
   - **Interactive Compiler Pipeline**: Visual status graph (`Source` → `Lexer` → `Parser` → `Semantic` → `TAC Gen` → `TAC VM`).
   - **Enhanced Token Visualizer**: Detailed table (`Lexeme`, `Token Type`, `Value`, `Line`, `Column`) and Token Detail Inspector.
   - **AST Visualizer**: Text and visual tree inspector with node property detail cards.
   - **Scoped Symbol Table Visualizer**: Multi-scope hierarchy viewer for global and nested block scopes.
   - **Step-by-Step TAC VM Stepper**: Interactive execution debugger (`[Start]`, `[Previous]`, `[Next]`, `[Run]`, `[Reset]`) displaying live PC, current instruction, variables, and stdout output.
   - **Structured Error Explainer**: 4-part diagnostic layout (What happened, Why, How to fix, Compiler Concept) with Levenshtein distance typo suggestions.

2. **`📚 Learning Mode`**:
   - 14 Structured Interactive Lessons covering Compiler Architecture, Lexical Analysis, Tokens, CFGs, Parsing, ASTs, Semantic Analysis, Symbol Tables, Type Safety, IR, TAC, VMs, and Error Diagnostics.
   - Includes 1-click `🚀 Load Code into IDE` for every lesson.

3. **`🧩 Practice Arena`**:
   - Controlled debugging challenges across Lexical, Syntax, Semantic, and Runtime categories with hint support and live solution validation.

4. **`🎯 Compiler Quiz Mode`**:
   - Knowledge self-assessment quiz on compiler design principles, score counter, and concept explanations.

---

## 🏛️ Compiler Pipeline & Architecture

```text
Source (.edu) → Lexer → Parser → Semantic Analyzer → TAC Generator → TAC Virtual Machine → Explainer / Output
```

1. **`lexer.py`** — Tokenizes source text into tokens with line and column position tracking. Reports `LEX` errors.
2. **`parser.py`** — Recursive-descent parser with operator precedence. Builds Abstract Syntax Tree (AST). Reports `SYN` errors.
3. **`semantic.py`** — Scoped symbol table hierarchy analysis. Collects `SEM` errors (undeclared variables, redeclarations, type mismatches).
4. **`tac_generator.py`** — Generates Three-Address Code (TAC) intermediate representation with source line metadata.
5. **`tac_interpreter.py`** — **TAC Virtual Machine**. Executes TAC instructions directly with step-limit protection, collecting variable environment states and step traces. Reports `RUN` runtime errors.
6. **`error_explainer.py`** — Deterministic diagnostic explainer. Formats 4-part explanations with Levenshtein edit-distance typo suggestions and compiler design concepts.

---

## 🧪 Sample Program Test Suite (`sample_programs/`)

Contains 20 comprehensive `.edu` programs:
- `01_valid_arithmetic.edu` - Arithmetic operations and operator precedence
- `02_variables.edu` - Variable declaration and assignment
- `03_float_calculations.edu` - Floating-point calculations
- `04_string_concatenation.edu` - String concatenation
- `05_boolean_expressions.edu` - Boolean logical operations (`and`, `or`, `not`)
- `06_if_else.edu` - Conditional branching
- `07_while_loop.edu` - Loops and iteration
- `08_nested_blocks.edu` - Nested block scoping
- `09_missing_semicolon.edu` - Syntax error demonstration
- `10_invalid_character.edu` - Lexical error demonstration
- `11_unterminated_string.edu` - Unterminated string lexical error
- `12_undeclared_variable.edu` - Semantic error + "Did you mean?" suggestion
- `13_redeclared_variable.edu` - Scope redeclaration error
- `14_type_mismatch.edu` - Type mismatch assignment error
- `15_invalid_condition.edu` - Non-boolean condition error
- `16_division_by_zero.edu` - TAC VM runtime division by zero
- `17_modulo_by_zero.edu` - TAC VM runtime modulo by zero
- `18_multiple_semantic_errors.edu` - Multiple semantic error collection
- `19_nested_scope.edu` - Scoped variable resolution
- `20_complex_precedence.edu` - Complex expression precedence test

