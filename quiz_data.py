"""
Compiler Design Quiz Data for EduLang
Self-assessment questions covering compiler design concepts.
"""

QUIZ_QUESTIONS = [
    {
        "id": "q1",
        "question": "What is the primary role of the Lexer (Lexical Analyzer) in a compiler?",
        "options": [
            "To execute machine code on CPU",
            "To convert raw source code characters into a stream of tokens",
            "To check if variable assignment types match",
            "To generate assembly language instructions"
        ],
        "correct": 1,
        "explanation": "The Lexer scans raw source characters and groups them into structured tokens (keywords, literals, identifiers, operators)."
    },
    {
        "id": "q2",
        "question": "Which compiler phase is responsible for building the Abstract Syntax Tree (AST)?",
        "options": [
            "Lexical Analyzer",
            "Semantic Analyzer",
            "Syntax Analyzer (Parser)",
            "TAC Generator"
        ],
        "correct": 2,
        "explanation": "The Parser performs syntax analysis according to grammar rules and constructs the AST."
    },
    {
        "id": "q3",
        "question": "What type of error is 'Variable x is used before declaration'?",
        "options": [
            "Lexical Error",
            "Syntax Error",
            "Semantic Error",
            "Linker Error"
        ],
        "correct": 2,
        "explanation": "Undeclared variable errors are semantic errors checked via symbol table resolution."
    },
    {
        "id": "q4",
        "question": "What does TAC stand for in compiler intermediate representations?",
        "options": [
            "Technical Access Code",
            "Three-Address Code",
            "Target Architecture Control",
            "Type Assignment Checker"
        ],
        "correct": 1,
        "explanation": "TAC stands for Three-Address Code, an intermediate representation where each instruction has at most one operator and 3 addresses."
    },
    {
        "id": "q5",
        "question": "Why do compilers use block-scoped Symbol Tables?",
        "options": [
            "To format text colors in IDE",
            "To manage variable declarations and visibility per lexical scope level",
            "To speed up file download speed",
            "To convert string literals to uppercase"
        ],
        "correct": 1,
        "explanation": "Scoped symbol tables track variable declarations within local blocks `{ ... }` and global scopes."
    },
    {
        "id": "q6",
        "question": "What happens if a program contains a Division by Zero during execution in the TAC VM?",
        "options": [
            "The compiler crashes silently",
            "The Virtual Machine catches a RUN001 runtime error and provides a friendly explanation",
            "The CPU reboots",
            "The program converts the result to infinity string"
        ],
        "correct": 1,
        "explanation": "The TAC VM safely intercepts division by zero and triggers a RUN001 diagnostic error."
    }
]
