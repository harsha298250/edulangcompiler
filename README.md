# EduLang Compiler — Student-Friendly Compiler that Explains Errors in Natural Language
**Team 5**

A full-fledged teaching compiler and Web IDE for EduLang that catches lexical, syntax, semantic, and runtime errors, explaining each diagnostic in clear, plain English with actionable fixes.

---

## 🚀 How to Run

### 1. Web IDE (Streamlit UI)
```bash
python -m streamlit run app.py
```
Open **http://localhost:8501** in your browser.

### 2. CLI Runner
```bash
python main.py sample_programs/01_valid_arithmetic.edu
```

### 3. Automated Test Suite
```bash
python -m unittest discover -s tests
```

---

## 🏛️ Compiler Pipeline & Architecture

```text
Source (.edu) → Lexer → Parser → Semantic Analyzer → TAC Generator → TAC Virtual Machine → Explainer / Output
```

1. **`lexer.py`** — Tokenizes source text into tokens (numbers, strings, keywords, operators). Reports `LEX` errors (unexpected characters, unterminated strings).
2. **`parser.py`** — Recursive-descent expression parser with operator precedence levels. Builds Abstract Syntax Tree (AST). Reports `SYN` errors (missing semicolons, unmatched brackets, malformed expressions).
3. **`semantic.py`** — Scoped symbol table hierarchy analysis. Collects all `SEM` errors (undeclared variables, redeclarations, type mismatches, invalid condition types).
4. **`tac_generator.py`** — Code generator pass emitting Three-Address Code (TAC) intermediate representation.
5. **`tac_interpreter.py`** — **TAC Virtual Machine**. Executes generated TAC instructions directly with step-limit infinite-loop protection. Raises structured `RUN` runtime errors (division by zero, modulo by zero).
6. **`error_explainer.py`** — Decoupled deterministic diagnostic explainer. Uses template matching and Levenshtein edit-distance to provide "Did you mean?" suggestions for variable & keyword typos.

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
