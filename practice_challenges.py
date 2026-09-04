"""
Practice & Debugging Arena Challenges for EduLang
Contains interactive debugging challenges categorized by error phase.
"""

PRACTICE_CHALLENGES = [
    {
        "id": "prac_lex_01",
        "title": "Lexical Challenge 1: Invalid Character",
        "category": "Lexical Analysis",
        "difficulty": "Easy",
        "description": "The program contains an unsupported symbol `@` in a variable declaration.",
        "buggy_code": """int price@ = 100;
print(price@);
""",
        "hint": "EduLang variable identifiers can only contain letters, digits, and underscores. Remove `@`.",
        "solution_code": """int price = 100;
print(price);
""",
        "expected_category": "🟢 SUCCESS"
    },
    {
        "id": "prac_lex_02",
        "title": "Lexical Challenge 2: Unterminated String",
        "category": "Lexical Analysis",
        "difficulty": "Easy",
        "description": "A string literal is missing its closing double quote.",
        "buggy_code": """string msg = "Welcome to EduLang;
print(msg);
""",
        "hint": "Every string literal must start and end with a double-quote (\"). Add a closing quote after 'EduLang'.",
        "solution_code": """string msg = "Welcome to EduLang";
print(msg);
""",
        "expected_category": "🟢 SUCCESS"
    },
    {
        "id": "prac_syn_01",
        "title": "Syntax Challenge 1: Missing Semicolon",
        "category": "Syntax Analysis",
        "difficulty": "Easy",
        "description": "Statement termination error on line 1.",
        "buggy_code": """int count = 5
print(count);
""",
        "hint": "In EduLang, every statement must end with a semicolon `;`.",
        "solution_code": """int count = 5;
print(count);
""",
        "expected_category": "🟢 SUCCESS"
    },
    {
        "id": "prac_syn_02",
        "title": "Syntax Challenge 2: Unmatched Parentheses",
        "category": "Syntax Analysis",
        "difficulty": "Medium",
        "description": "The `if` condition is missing a closing parenthesis `)`.",
        "buggy_code": """int score = 75;
if (score > 50 {
    print("Pass");
}
""",
        "hint": "Count the opening '(' and closing ')' parentheses in the `if` condition.",
        "solution_code": """int score = 75;
if (score > 50) {
    print("Pass");
}
""",
        "expected_category": "🟢 SUCCESS"
    },
    {
        "id": "prac_sem_01",
        "title": "Semantic Challenge 1: Undeclared Variable",
        "category": "Semantic Analysis",
        "difficulty": "Medium",
        "description": "Variable `total` is used in calculation without prior type declaration.",
        "buggy_code": """int item = 15;
total = item + 5;
print(total);
""",
        "hint": "Declare `total` with a type keyword (e.g. `int total = item + 5;`) before assigning to it.",
        "solution_code": """int item = 15;
int total = item + 5;
print(total);
""",
        "expected_category": "🟢 SUCCESS"
    },
    {
        "id": "prac_sem_02",
        "title": "Semantic Challenge 2: Type Mismatch Assignment",
        "category": "Semantic Analysis",
        "difficulty": "Medium",
        "description": "Assigning a string literal to an integer variable.",
        "buggy_code": """int age = "twenty";
print(age);
""",
        "hint": "An `int` variable can only hold integer numbers. Change value to `20` or change type to `string`.",
        "solution_code": """int age = 20;
print(age);
""",
        "expected_category": "🟢 SUCCESS"
    },
    {
        "id": "prac_run_01",
        "title": "Runtime Challenge 1: Division by Zero",
        "category": "Runtime / Execution",
        "difficulty": "Hard",
        "description": "Program attempts to divide by a variable that evaluates to 0.",
        "buggy_code": """int num = 50;
int divisor = 0;
int result = num / divisor;
print(result);
""",
        "hint": "Check that the divisor is non-zero before performing division.",
        "solution_code": """int num = 50;
int divisor = 5;
int result = num / divisor;
print(result);
""",
        "expected_category": "🟢 SUCCESS"
    }
]
