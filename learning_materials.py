"""
Learning Materials & Curriculum for EduLang
Contains 14 interactive compiler design lessons with runnable code examples.
"""

LESSONS = [
    {
        "id": "1_intro",
        "title": "1. What is a Compiler?",
        "category": "Fundamentals",
        "what": "A compiler is a specialized software system that translates computer programs written in high-level human-readable programming languages into executable low-level target code.",
        "why": "Computers cannot directly execute high-level source code like Python or EduLang. Compilers analyze program structure, check for structural errors, and translate instructions step-by-step.",
        "how": "The compiler runs a pipeline of distinct phases: Lexical Analysis (Tokens) → Syntax Analysis (AST) → Semantic Analysis (Symbol Table & Types) → Code Generation (TAC) → Virtual Machine Execution.",
        "code": """# Lesson 1: Basic Program
int a = 10;
int b = 20;
int result = a + b;
print("Result of addition:");
print(result);
"""
    },
    {
        "id": "2_lexer",
        "title": "2. Lexical Analysis",
        "category": "Front-End",
        "what": "Lexical Analysis (Scanning) is the very first phase of compilation. It converts a raw stream of source characters into a stream of structured tokens.",
        "why": "Processing character-by-character in later stages is inefficient and prone to errors. Grouping characters into meaningful tokens simplifies language parsing.",
        "how": "The Lexer scans input text character-by-character, discards whitespace and comments (`#`), and matches patterns for numbers, keywords (`if`, `int`), identifiers, and operators.",
        "code": """# Lesson 2: Scanning & Tokens
int count = 100;
float pi = 3.14159;
string name = "EduLang";
"""
    },
    {
        "id": "3_tokens",
        "title": "3. Tokens & Lexemes",
        "category": "Front-End",
        "what": "A Lexeme is the raw substring in source code. A Token is an abstract object wrapping the lexeme with a token type (e.g. KEYWORD, IDENTIFIER, NUMBER_LIT), line number, and column position.",
        "why": "Tokens decouple raw source formatting from the grammatical structure of the language.",
        "how": "For example, the lexeme `int` becomes `Token(INT, 'int', line=1, col=1)`. The lexeme `15` becomes `Token(NUMBER_LIT, 15, line=1, col=5)`.",
        "code": """# Lesson 3: Keywords vs Identifiers
int x = 42;
if (x == 42) {
    print("Matched integer literal!");
}
"""
    },
    {
        "id": "4_syntax",
        "title": "4. Syntax Analysis & Parsing",
        "category": "Front-End",
        "what": "Syntax Analysis (Parsing) checks whether a token stream satisfies the formal grammar rules of the programming language.",
        "why": "A program can have valid tokens but still be grammatically incorrect (e.g. `int = ; x 10`). Parsing verifies sentence structure.",
        "how": "EduLang uses a Recursive-Descent Parser. Each grammar production rule corresponds to a parsing function (e.g., `parse_decl()`, `parse_if()`, `parse_expr()`).",
        "code": """# Lesson 4: Statement Structure
int score = 85;
if (score >= 50) {
    print("Passed exam!");
} else {
    print("Needs review.");
}
"""
    },
    {
        "id": "5_cfg",
        "title": "5. Context-Free Grammars (CFG)",
        "category": "Front-End",
        "what": "A Context-Free Grammar (CFG) is a set of mathematical production rules defining the set of all syntactically valid programs in a language.",
        "why": "CFGs provide an unambiguous specification of language syntax and guide parser design.",
        "how": "Rules are written in Backus-Naur Form (BNF). Example: `VarDecl ::= Type IDENT '=' Expression ';'`.",
        "code": """# Lesson 5: Expression Precedence
int x = 5 + 3 * 2;
# Multiplication (3 * 2) evaluates before addition (5 + 6 = 11)
print(x);
"""
    },
    {
        "id": "6_parse_trees",
        "title": "6. Parse Trees vs AST",
        "category": "Front-End",
        "what": "A Parse Tree represents every concrete rule matched during parsing (including semicolons and braces). An Abstract Syntax Tree (AST) retains only structural semantic nodes.",
        "why": "Parse trees contain redundant punctuation details. ASTs are compact and convenient for semantic checks and code generation.",
        "how": "EduLang parses concrete tokens directly into clean AST node instances like `VarDecl`, `Assign`, `BinOp`, and `If`.",
        "code": """# Lesson 6: Nested Blocks
{
    int level = 1;
    print(level);
}
"""
    },
    {
        "id": "7_ast",
        "title": "7. Abstract Syntax Trees (AST)",
        "category": "Front-End",
        "what": "An Abstract Syntax Tree (AST) is a hierarchical tree structure representing the logical structure of a program.",
        "why": "Trees naturally model nested expressions, statements, conditional blocks, and loops.",
        "how": "The root node is a `Program`. Parent nodes are control flow statements (`If`, `While`), and leaf nodes are literals or variable references (`Literal`, `VarRef`).",
        "code": """# Lesson 7: Complex AST Branches
int x = 10;
while (x > 7) {
    print(x);
    x = x - 1;
}
"""
    },
    {
        "id": "8_semantic",
        "title": "8. Semantic Analysis",
        "category": "Middle-End",
        "what": "Semantic Analysis checks the meaning of a syntactically valid AST. It ensures variables are declared before use, types match, and operations are valid.",
        "why": "Code can be syntactically correct (e.g. `int x = \"hello\";`) but semantically invalid.",
        "how": "The Semantic Analyzer traverses the AST recursively, updating and inspecting the Symbol Table at every node.",
        "code": """# Lesson 8: Type Checking
int age = 20;
string greeting = "Hello";
print(greeting);
"""
    },
    {
        "id": "9_symbol_table",
        "title": "9. Symbol Tables & Scope",
        "category": "Middle-End",
        "what": "A Symbol Table is a data structure tracking declared variables, their types, and their scope level during compilation.",
        "why": "Languages support block scoping `{ ... }`. Inner scopes can access outer variables, but outer scopes cannot access inner variables.",
        "how": "EduLang creates a chain of `Scope` objects linked to parent scopes. Scope lookup traverses upward from current scope to global scope.",
        "code": """# Lesson 9: Scope Hierarchy
int outer = 100;
if (outer > 50) {
    int inner = 500;
    print(outer + inner);
}
"""
    },
    {
        "id": "10_type_checking",
        "title": "10. Type Checking & Safety",
        "category": "Middle-End",
        "what": "Type Checking enforces type compatibility rules (e.g., preventing addition between `string` and `int`).",
        "why": "Static type checking prevents invalid memory operations and runtime type errors before code runs.",
        "how": "EduLang verifies assignment compatibility, condition boolean types in `if`/`while`, and valid operator types (`+`, `-`, `*`, `/`, `and`, `or`).",
        "code": """# Lesson 10: Boolean Types
bool flag = true;
if (flag and true) {
    print("Flag is active!");
}
"""
    },
    {
        "id": "11_ir",
        "title": "11. Intermediate Representation (IR)",
        "category": "Back-End",
        "what": "An Intermediate Representation (IR) is an abstract code format between source code and machine code.",
        "why": "IR decouples language front-ends from hardware back-ends, enabling portable code generation and machine-independent optimizations.",
        "how": "Common IR formats include Three-Address Code (TAC), Control Flow Graphs, and Abstract Virtual Machine Bytecode.",
        "code": """# Lesson 11: Intermediate Code Prep
int a = 5;
int b = 10;
int c = a * b + 2;
print(c);
"""
    },
    {
        "id": "12_tac",
        "title": "12. Three-Address Code (TAC)",
        "category": "Back-End",
        "what": "Three-Address Code (TAC) is an IR where every instruction has at most one operator and three operand addresses (result, left, right).",
        "why": "Complex nested expressions (e.g., `x = a + b * c`) are flattened into linear primitive instructions with temporary variables (`t0`, `t1`).",
        "how": "Example: `t0 = b * c` followed by `t1 = a + t0` followed by `x = t1`.",
        "code": """# Lesson 12: TAC Generation
int val = (10 + 20) * 2;
print(val);
"""
    },
    {
        "id": "13_vm",
        "title": "13. Virtual Machine & Execution",
        "category": "Back-End",
        "what": "A Virtual Machine (VM) is a software execution engine that interprets TAC instructions or bytecode.",
        "why": "VMs allow safe, sandboxed execution with step limits, memory isolation, and runtime error trap handling.",
        "how": "The TAC VM uses a Program Counter (`PC`), variable memory dictionary (`env`), instruction array, and output buffer.",
        "code": """# Lesson 13: Loop Execution
int i = 1;
int sum = 0;
while (i <= 5) {
    sum = sum + i;
    i = i + 1;
}
print(sum);
"""
    },
    {
        "id": "14_diagnostics",
        "title": "14. Compiler Diagnostics & Debugging",
        "category": "Diagnostics",
        "what": "Compiler diagnostics report error phase, line number, plain-English explanation, and suggested fix when compilation fails.",
        "why": "Clear diagnostics help programmers quickly identify and resolve bugs.",
        "how": "EduLang's Error Explainer matches error codes (`LEX001`, `SYN001`, `SEM001`, `RUN001`), uses Levenshtein distance for typos, and maps compiler concepts.",
        "code": """# Lesson 14: Diagnostic Example
int count = 10;
print(count);
"""
    }
]
