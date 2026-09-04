"""
Learning Materials & Curriculum for EduLang
Contains 14 interactive compiler design lessons with runnable code examples,
compiler phase breakdown, and mini exercises categorized by difficulty level.
"""

LESSONS = [
    {
        "id": "1_intro",
        "level": "Level 1 — Beginner",
        "title": "1. What is a Compiler?",
        "category": "Fundamentals",
        "concept": "A compiler translates human-readable source code into computer-executable target instructions.",
        "what": "A compiler is a specialized software system that translates computer programs written in high-level human-readable programming languages into executable low-level target code.",
        "why": "Computers cannot directly execute high-level source code like Python or EduLang. Compilers analyze program structure, check for structural errors, and translate instructions step-by-step.",
        "how": "The compiler runs a pipeline of distinct phases: Lexical Analysis (Tokens) → Syntax Analysis (AST) → Semantic Analysis (Symbol Table & Types) → Code Generation (TAC) → Virtual Machine Execution.",
        "compiler_action": "Translates the full source program through Lexer, Parser, Semantic Analyzer, and TAC VM without human intervention.",
        "code": """# Lesson 1: Basic Program
int a = 10;
int b = 20;
int result = a + b;
print("Result of addition:");
print(result);
""",
        "exercise": {
            "question": "What is the very first phase executed when a compiler reads source code?",
            "options": ["Syntax Analysis (Parser)", "Lexical Analysis (Lexer)", "Code Generation (TAC)", "Virtual Machine Execution"],
            "answer": 1,
            "explanation": "Lexical Analysis (the Lexer) is always the first phase. It scans raw source characters into tokens."
        }
    },
    {
        "id": "2_lexer",
        "level": "Level 1 — Beginner",
        "title": "2. Lexical Analysis",
        "category": "Front-End",
        "concept": "Lexical analysis converts a stream of raw characters into structured tokens.",
        "what": "Lexical Analysis (Scanning) is the very first phase of compilation. It converts a raw stream of source characters into a stream of structured tokens.",
        "why": "Processing character-by-character in later stages is inefficient and prone to errors. Grouping characters into meaningful tokens simplifies language parsing.",
        "how": "The Lexer scans input text character-by-character, discards whitespace and comments (`#`), and matches patterns for numbers, keywords (`if`, `int`), identifiers, and operators.",
        "compiler_action": "Scans `int count = 100;` character-by-character, discarding spaces and producing structured Token objects with line/col metadata.",
        "code": """# Lesson 2: Scanning & Tokens
int count = 100;
float pi = 3.14159;
string name = "EduLang";
""",
        "exercise": {
            "question": "What does the Lexer do when it encounters a comment starting with '#'?",
            "options": ["Generates a COMMENT token", "Raises a Lexical Error", "Ignores characters until the end of the line", "Stops compilation"],
            "answer": 2,
            "explanation": "Comments are meant for human readers. The Lexer skips comments until the end of the line without producing tokens."
        }
    },
    {
        "id": "3_tokens",
        "level": "Level 1 — Beginner",
        "title": "3. Tokens & Lexemes",
        "category": "Front-End",
        "concept": "A lexeme is raw text; a token is an abstract object carrying type, value, line, and column.",
        "what": "A Lexeme is the raw substring in source code. A Token is an abstract object wrapping the lexeme with a token type (e.g. KEYWORD, IDENTIFIER, NUMBER_LIT), line number, and column position.",
        "why": "Tokens decouple raw source formatting from the grammatical structure of the language.",
        "how": "For example, the lexeme `int` becomes `Token(INT, 'int', line=1, col=1)`. The lexeme `15` becomes `Token(NUMBER_LIT, 15, line=1, col=5)`.",
        "compiler_action": "Classifies raw lexemes into token types: `int` → `INT` (Keyword), `x` → `IDENT` (Identifier), `42` → `NUMBER_LIT` (Integer Literal).",
        "code": """# Lesson 3: Keywords vs Identifiers
int x = 42;
if (x == 42) {
    print("Matched integer literal!");
}
""",
        "exercise": {
            "question": "Which token type represents user-defined variable names like 'my_var'?",
            "options": ["KEYWORD", "IDENTIFIER", "OPERATOR", "LITERAL"],
            "answer": 1,
            "explanation": "User-defined names for variables or functions are classified as IDENTIFIER (or IDENT) tokens."
        }
    },
    {
        "id": "4_syntax",
        "level": "Level 1 — Beginner",
        "title": "4. Syntax Analysis & Parsing",
        "category": "Front-End",
        "concept": "Syntax analysis verifies that tokens satisfy the formal grammar rules of the language.",
        "what": "Syntax Analysis (Parsing) checks whether a token stream satisfies the formal grammar rules of the programming language.",
        "why": "A program can have valid tokens but still be grammatically incorrect (e.g. `int = ; x 10`). Parsing verifies sentence structure.",
        "how": "EduLang uses a Recursive-Descent Parser. Each grammar production rule corresponds to a parsing function (e.g., `parse_decl()`, `parse_if()`, `parse_expr()`).",
        "compiler_action": "Traverses tokens according to grammar rules: `VarDecl` expects `Type` → `IDENT` → `=` → `Expression` → `;`.",
        "code": """# Lesson 4: Statement Structure
int score = 85;
if (score >= 50) {
    print("Passed exam!");
} else {
    print("Needs review.");
}
""",
        "exercise": {
            "question": "If a student writes `int x = 10` without a semicolon at the end, which stage detects it?",
            "options": ["Lexical Analyzer", "Syntax Analyzer (Parser)", "Semantic Analyzer", "TAC VM"],
            "answer": 1,
            "explanation": "The Parser expects a semicolon `;` to terminate statement grammar rules and raises a Syntax Error (SYN001) if missing."
        }
    },
    {
        "id": "5_cfg",
        "level": "Level 2 — Intermediate",
        "title": "5. Context-Free Grammars (CFG)",
        "category": "Front-End",
        "concept": "CFGs define language syntax and operator precedence rules using formal production rules.",
        "what": "A Context-Free Grammar (CFG) is a set of mathematical production rules defining the set of all syntactically valid programs in a language.",
        "why": "CFGs provide an unambiguous specification of language syntax and guide parser design.",
        "how": "Rules are written in Backus-Naur Form (BNF). Example: `VarDecl ::= Type IDENT '=' Expression ';'`.",
        "compiler_action": "Parser follows precedence levels: Multiplication (`*`) is nested deeper than Addition (`+`), ensuring `5 + 3 * 2` parses as `5 + (3 * 2)`.",
        "code": """# Lesson 5: Expression Precedence
int x = 5 + 3 * 2;
# Multiplication (3 * 2 = 6) evaluates before addition (5 + 6 = 11)
print(x);
""",
        "exercise": {
            "question": "How does a recursive-descent parser enforce that '*' has higher precedence than '+'?",
            "options": ["By evaluating math during lexing", "By calling `parse_factor()` (*, /) inside `parse_term()` (+, -)", "By sorting tokens alphabetically", "By asking the operating system"],
            "answer": 1,
            "explanation": "Lower precedence rules (`parse_term` for + / -) call higher precedence rules (`parse_factor` for * / /) first."
        }
    },
    {
        "id": "6_parse_trees",
        "level": "Level 2 — Intermediate",
        "title": "6. Parse Trees vs AST",
        "category": "Front-End",
        "concept": "Parse trees include all concrete tokens; ASTs simplify structure into meaningful nodes.",
        "what": "A Parse Tree represents every concrete rule matched during parsing (including semicolons and braces). An Abstract Syntax Tree (AST) retains only structural semantic nodes.",
        "why": "Parse trees contain redundant punctuation details. ASTs are compact and convenient for semantic checks and code generation.",
        "how": "EduLang parses concrete tokens directly into clean AST node instances like `VarDecl`, `Assign`, `BinOp`, and `If`.",
        "compiler_action": "Discards punctuation like `;` and `{}` from tree nodes, keeping only logical operands and statement relationships.",
        "code": """# Lesson 6: Nested Blocks
{
    int level = 1;
    print(level);
}
""",
        "exercise": {
            "question": "What is the main difference between a Parse Tree and an Abstract Syntax Tree (AST)?",
            "options": ["Parse trees contain machine code", "ASTs strip out concrete syntax like semicolons and parenthesis", "Parse trees are created by the VM", "ASTs only exist for comments"],
            "answer": 1,
            "explanation": "ASTs discard unnecessary syntactic details (semicolons, commas, braces) and keep only structural semantics."
        }
    },
    {
        "id": "7_ast",
        "level": "Level 2 — Intermediate",
        "title": "7. Abstract Syntax Trees (AST)",
        "category": "Front-End",
        "concept": "An AST is a hierarchical tree representation of the logical structure of a program.",
        "what": "An Abstract Syntax Tree (AST) is a hierarchical tree structure representing the logical structure of a program.",
        "why": "Trees naturally model nested expressions, statements, conditional blocks, and loops.",
        "how": "The root node is a `Program`. Parent nodes are control flow statements (`If`, `While`), and leaf nodes are literals or variable references (`Literal`, `VarRef`).",
        "compiler_action": "Constructs node hierarchy: `Program` → `VarDecl(int x)` → `While(x > 7)` → `Block` → `Assign(x = x - 1)`.",
        "code": """# Lesson 7: Complex AST Branches
int x = 10;
while (x > 7) {
    print(x);
    x = x - 1;
}
""",
        "exercise": {
            "question": "In an AST representing `x = a + b;`, what node type represents the '+' operation?",
            "options": ["Literal", "VarDecl", "BinOp (Binary Operator)", "While"],
            "answer": 2,
            "explanation": "`BinOp` represents binary operations like `+`, `-`, `*`, `/`, `and`, `or` with left and right child expressions."
        }
    },
    {
        "id": "8_semantic",
        "level": "Level 2 — Intermediate",
        "title": "8. Semantic Analysis",
        "category": "Middle-End",
        "concept": "Semantic analysis checks program meaning, variable declarations, types, and scope rules.",
        "what": "Semantic Analysis checks the meaning of a syntactically valid AST. It ensures variables are declared before use, types match, and operations are valid.",
        "why": "Code can be syntactically correct (e.g. `int x = \"hello\";`) but semantically invalid.",
        "how": "The Semantic Analyzer traverses the AST recursively, updating and inspecting the Symbol Table at every node.",
        "compiler_action": "Walks AST, verifies that `age` is declared before use, and checks that `greeting` matches type `string`.",
        "code": """# Lesson 8: Type Checking
int age = 20;
string greeting = "Hello";
print(greeting);
""",
        "exercise": {
            "question": "What error occurs if a program tries to use variable `y` without declaring it first?",
            "options": ["Lexical Error (LEX001)", "Syntax Error (SYN001)", "Semantic Error (SEM001 - Undeclared Variable)", "Runtime Error (RUN001)"],
            "answer": 2,
            "explanation": "Using an undeclared variable is a semantic error (SEM001) caught during symbol table resolution."
        }
    },
    {
        "id": "9_symbol_table",
        "level": "Level 2 — Intermediate",
        "title": "9. Symbol Tables & Scope",
        "category": "Middle-End",
        "concept": "A symbol table tracks variable names, types, and scope hierarchy levels.",
        "what": "A Symbol Table is a data structure tracking declared variables, their types, and their scope level during compilation.",
        "why": "Languages support block scoping `{ ... }`. Inner scopes can access outer variables, but outer scopes cannot access inner variables.",
        "how": "EduLang creates a chain of `Scope` objects linked to parent scopes. Scope lookup traverses upward from current scope to global scope.",
        "compiler_action": "Creates `Global Scope` containing `outer : int`. Creates child `Block Scope` containing `inner : int` linked to parent.",
        "code": """# Lesson 9: Scope Hierarchy
int outer = 100;
if (outer > 50) {
    int inner = 500;
    print(outer + inner);
}
""",
        "exercise": {
            "question": "Can code outside a block access a variable declared inside `{ int inner = 500; }`?",
            "options": ["Yes, all variables are global", "No, local variables exist only within their enclosing block scope", "Only if the variable is a string", "Only during TAC generation"],
            "answer": 1,
            "explanation": "Variables declared inside a block scope are not accessible outside that block scope."
        }
    },
    {
        "id": "10_type_checking",
        "level": "Level 3 — Advanced",
        "title": "10. Type Checking & Safety",
        "category": "Middle-End",
        "concept": "Type checking enforces type rules (e.g. boolean conditions, matching variable assignments).",
        "what": "Type Checking enforces type compatibility rules (e.g., preventing addition between `string` and `int`).",
        "why": "Static type checking prevents invalid memory operations and runtime type errors before code runs.",
        "how": "EduLang verifies assignment compatibility, condition boolean types in `if`/`while`, and valid operator types (`+`, `-`, `*`, `/`, `and`, `or`).",
        "compiler_action": "Verifies `flag and true` evaluates to `bool`, ensuring `if` condition receives a boolean expression.",
        "code": """# Lesson 10: Boolean Types
bool flag = true;
if (flag and true) {
    print("Flag is active!");
}
""",
        "exercise": {
            "question": "What happens if a student writes `if (100) { ... }` in EduLang?",
            "options": ["It evaluates as true", "Semantic Analyzer raises SEM005 (Non-boolean condition)", "It compiles directly to TAC", "It formats the text in blue"],
            "answer": 1,
            "explanation": "EduLang requires conditions in `if` and `while` statements to evaluate strictly to `bool` (SEM005)."
        }
    },
    {
        "id": "11_ir",
        "level": "Level 3 — Advanced",
        "title": "11. Intermediate Representation (IR)",
        "category": "Back-End",
        "concept": "IR decouples source language front-ends from hardware back-ends for optimization and portability.",
        "what": "An Intermediate Representation (IR) is an abstract code format between source code and machine code.",
        "why": "IR decouples language front-ends from hardware back-ends, enabling portable code generation and machine-independent optimizations.",
        "how": "Common IR formats include Three-Address Code (TAC), Control Flow Graphs, and Abstract Virtual Machine Bytecode.",
        "compiler_action": "Translates high-level AST constructs into flattened intermediate instruction sequences.",
        "code": """# Lesson 11: Intermediate Code Prep
int a = 5;
int b = 10;
int c = a * b + 2;
print(c);
""",
        "exercise": {
            "question": "Why do production compilers use an Intermediate Representation (IR)?",
            "options": ["To eliminate the need for a Lexer", "To decouple language parsing from target platform code generation", "To display HTML in browser", "To encrypt source code"],
            "answer": 1,
            "explanation": "IR separates the front-end (parsing/semantics) from the back-end (codegen/optimization), allowing 1 front-end to target multiple architectures."
        }
    },
    {
        "id": "12_tac",
        "level": "Level 3 — Advanced",
        "title": "12. Three-Address Code (TAC)",
        "category": "Back-End",
        "concept": "TAC flattens expressions into instructions with at most 3 operands and temporary variables.",
        "what": "Three-Address Code (TAC) is an IR where every instruction has at most one operator and three operand addresses (result, left, right).",
        "why": "Complex nested expressions (e.g., `x = a + b * c`) are flattened into linear primitive instructions with temporary variables (`t0`, `t1`).",
        "how": "Example: `t0 = b * c` followed by `t1 = a + t0` followed by `x = t1`.",
        "compiler_action": "Generates `t0 = 10 + 20`, `t1 = t0 * 2`, `val = t1`, `PRINT val`.",
        "code": """# Lesson 12: TAC Generation
int val = (10 + 20) * 2;
print(val);
""",
        "exercise": {
            "question": "In TAC, how is a complex expression like `x = (a + b) * c` represented?",
            "options": ["As a single line `x = (a + b) * c`", "Using temporaries: `t0 = a + b`, `t1 = t0 * c`, `x = t1`", "By converting all numbers to strings", "By deleting parentheses"],
            "answer": 1,
            "explanation": "TAC breaks down nested expressions into 1 operator per line using temporary variables like `t0` and `t1`."
        }
    },
    {
        "id": "13_vm",
        "level": "Level 3 — Advanced",
        "title": "13. Virtual Machine & Execution",
        "category": "Back-End",
        "concept": "A Virtual Machine interprets TAC instructions step-by-step using PC and environment memory.",
        "what": "A Virtual Machine (VM) is a software execution engine that interprets TAC instructions or bytecode.",
        "why": "VMs allow safe, sandboxed execution with step limits, memory isolation, and runtime error trap handling.",
        "how": "The TAC VM uses a Program Counter (`PC`), variable memory dictionary (`env`), instruction array, and output buffer.",
        "compiler_action": "Executes TAC line by line, maintaining `PC`, stack frames for local block scopes, and capturing `print` output.",
        "code": """# Lesson 13: Loop Execution
int i = 1;
int sum = 0;
while (i <= 5) {
    sum = sum + i;
    i = i + 1;
}
print(sum);
""",
        "exercise": {
            "question": "What role does the Program Counter (PC) play in the TAC Virtual Machine?",
            "options": ["Counts total lines of comments", "Tracks the current index/address of the TAC instruction being executed", "Measures CPU temperature", "Counts declared variables"],
            "answer": 1,
            "explanation": "The Program Counter (PC) points to the index of the active TAC instruction in the VM."
        }
    },
    {
        "id": "14_diagnostics",
        "level": "Level 3 — Advanced",
        "title": "14. Compiler Diagnostics & Debugging",
        "category": "Diagnostics",
        "concept": "Compiler diagnostics report error phase, line number, plain English explanation, and fix.",
        "what": "Compiler diagnostics report error phase, line number, plain-English explanation, and suggested fix when compilation fails.",
        "why": "Clear diagnostics help programmers quickly identify and resolve bugs.",
        "how": "EduLang's Error Explainer matches error codes (`LEX001`, `SYN001`, `SEM001`, `RUN001`), uses Levenshtein distance for typos, and maps compiler concepts.",
        "compiler_action": "Formats structured diagnostic card with Title, Line Number, What Happened, Why, How to Fix, and Concept.",
        "code": """# Lesson 14: Diagnostic Example
int count = 10;
print(count);
""",
        "exercise": {
            "question": "What algorithm does EduLang use to suggest typo fixes like 'Did you mean count?'",
            "options": ["Dijkstra's Algorithm", "Levenshtein Distance", "Binary Search", "Quicksort"],
            "answer": 1,
            "explanation": "Levenshtein distance measures edit distance (insertions/deletions/substitutions) to find nearest valid keyword or variable candidates."
        }
    }
]
