"""
Error Explainer — the "student-friendly" heart of this compiler.

Takes raw error objects produced by the Lexer, Parser, Semantic Analyzer, or TAC VM
and turns them into natural-language explanations with:
  - What went wrong, in plain English
  - Why the compiler/interpreter is confused
  - How to likely fix it
  - A short example fix where useful
  - "Did you mean?" suggestions for typos in variables and keywords (via Levenshtein distance)
"""


def levenshtein_distance(s1, s2):
    """Calculates Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


KEYWORDS = [
    "int", "float", "string", "bool", "true", "false",
    "if", "else", "while", "print", "and", "or", "not"
]


def find_suggestion(word, candidates, max_dist=2):
    """Finds closest string candidate within max_dist edit distance, ignoring irrelevant matches."""
    if not word or not candidates:
        return None
    word_str = str(word).strip()
    if not word_str or word_str.lower() in [c.lower() for c in candidates]:
        return None  # Already a valid candidate, no typo suggestion needed
    
    effective_max = 1 if len(word_str) <= 2 else max_dist
    best_candidate = None
    best_dist = effective_max + 1

    for candidate in candidates:
        cand_str = str(candidate).strip()
        if not cand_str:
            continue
        dist = levenshtein_distance(word_str.lower(), cand_str.lower())
        if dist < best_dist and dist <= effective_max and dist < len(word_str):
            best_dist = dist
            best_candidate = cand_str

    return best_candidate


def _fmt(title, what, why, fix, example=None, suggestion=None):
    lines = [
        f"❌ {title}",
        f"   What happened: {what}",
    ]
    if suggestion:
        lines.append(f"   💡 Suggestion: Did you mean '{suggestion}'?")
    lines.extend([
        f"   Why: {why}",
        f"   How to fix it: {fix}",
    ])
    if example:
        lines.append(f"   Example: {example}")
    return "\n".join(lines)


def explain_lex001(err):
    ch = err.context.get("char", "?")
    return _fmt(
        f"Line {err.line}: I found a character I don't understand",
        f"The symbol '{ch}' isn't part of EduLang's alphabet.",
        "Compilers only recognize a fixed set of letters, digits, and symbols. "
        "This character might be a typo, or copy-pasted from a different font/language.",
        f"Remove or replace '{ch}' with a valid EduLang symbol.",
    )


def explain_lex002(err):
    partial = err.context.get("partial", "")
    return _fmt(
        f"Line {err.line}: A text (string) value never got closed",
        f"I started reading a string at \"{partial}... but never found the closing quote (\").",
        "Every string must start and end with a double quote on the same line.",
        "Add a closing double-quote (\") at the end of the string.",
        example=f'"{partial}"  instead of  "{partial}',
    )


def explain_syn001(err):
    return _fmt(
        f"Line {err.line}: Missing a semicolon",
        "This statement looks complete, but it's missing the ';' that ends it.",
        "EduLang (like C, Java, and many languages) uses ';' to mark the end of a statement, "
        "so the compiler knows where one instruction stops and the next begins.",
        "Add a ';' at the end of the line shown above.",
        example="int x = 5;   // not: int x = 5",
    )


def explain_syn002(err):
    hint = err.context.get("hint", "something specific")
    got = err.context.get("got_value") or err.context.get("got")
    expected = err.context.get("expected")

    # Special handling for missing variable identifier after a type keyword (e.g. `int \n if (...)`)
    if expected == "IDENT" or "variable name" in str(hint):
        return _fmt(
            f"Line {err.line}: Missing variable name after type",
            f"I found the type keyword '{got}', but there is no variable name following it.",
            "EduLang declaration grammar expects a type keyword (int, float, string, bool) followed by a valid variable identifier.",
            "Provide a variable name immediately after the type keyword.",
            example="int count = 10;   // or: int value;"
        )

    sug = find_suggestion(str(got), KEYWORDS) if got else None
    return _fmt(
        f"Line {err.line}: Something is missing in this statement",
        f"I expected {hint}, but instead I found '{got}'.",
        "The structure of this statement doesn't match EduLang's grammar rules at this point.",
        f"Check the statement on line {err.line} and add {hint}.",
        suggestion=sug
    )


def explain_syn003(err):
    hint = err.context.get("hint", "a matching bracket")
    got = err.context.get("got_value") or err.context.get("got")
    return _fmt(
        f"Line {err.line}: A bracket doesn't have its matching partner",
        f"I expected {hint}, but instead found '{got}'.",
        "Every '(' needs a ')' and every '{' needs a '}'. One of yours is missing or "
        "in the wrong place, often because of an extra or missing bracket earlier in the file.",
        "Count your opening and closing brackets above this line and add the missing one.",
    )


def explain_syn004(err):
    got = err.context.get("got_value")
    got_disp = got if got is not None else err.context.get("got")
    sug = find_suggestion(str(got_disp), KEYWORDS) if got_disp else None
    return _fmt(
        f"Line {err.line}: Expected an expression here",
        f"I was expecting a value (a number, string, variable, or '(...)') but found '{got_disp}' instead.",
        "This usually happens after an operator, '=', or an opening bracket, when the "
        "value that should follow is missing or misplaced.",
        "Make sure a valid value follows every '=', operator, or opening parenthesis.",
        suggestion=sug
    )


def explain_sem001(err):
    name = err.context.get("name")
    candidates = err.context.get("declared_vars", [])
    sug = find_suggestion(name, candidates) if candidates else find_suggestion(name, KEYWORDS)
    return _fmt(
        f"Line {err.line}: '{name}' hasn't been declared yet",
        f"You're using the variable '{name}', but I never saw it declared with a type "
        f"(like 'int {name};') earlier in the program.",
        "EduLang needs to know a variable's type before it's used, so it can check your code "
        "makes sense and reserve space for it.",
        f"Declare '{name}' before using it, e.g. 'int {name};' — or check for a typo in the name.",
        suggestion=sug
    )


def explain_sem002(err):
    name = err.context.get("name")
    return _fmt(
        f"Line {err.line}: '{name}' is already declared",
        f"You're declaring '{name}' again in the same block, but it already exists.",
        "Declaring the same name twice in one scope would be ambiguous — the compiler "
        "wouldn't know which one you mean.",
        f"Remove the duplicate declaration, or rename one of the two '{name}' variables.",
    )


def explain_sem003(err):
    name = err.context.get("name")
    declared = err.context.get("declared")
    got = err.context.get("got")
    return _fmt(
        f"Line {err.line}: Type mismatch when setting '{name}'",
        f"'{name}' was declared as '{declared}', but you're assigning it a '{got}' value.",
        "EduLang checks that the value you store in a variable matches the type you "
        "promised when you declared it, to prevent accidental bugs.",
        f"Either change the value to a '{declared}', or change {name}'s declared type to '{got}'.",
    )


def explain_sem004(err):
    op = err.context.get("op")
    left = err.context.get("left") or err.context.get("type")
    right = err.context.get("right")
    if right is not None:
        detail = f"between a '{left}' and a '{right}'"
    else:
        detail = f"on a '{left}'"
    return _fmt(
        f"Line {err.line}: '{op}' can't be used {detail}",
        f"The operator '{op}' isn't defined for these types.",
        "Some operators only make sense for certain types (e.g. you can add two numbers, "
        "and join two strings with '+', but you can't add a number to a string directly).",
        "Convert one side to match the other's type, or use a different operator.",
    )


def explain_sem005(err):
    t = err.context.get("type")
    return _fmt(
        f"Line {err.line}: This condition isn't true/false",
        f"'if' and 'while' need a true/false (bool) condition, but this one is a '{t}'.",
        "The compiler can't decide whether to take a branch or keep looping unless "
        "the condition clearly evaluates to true or false.",
        "Use a comparison like 'x > 0' or 'x == 5' instead of a plain value.",
    )


def explain_run001(err):
    line_info = f"Line {err.line}: " if getattr(err, "line", None) else ""
    return _fmt(
        f"{line_info}Division by zero",
        "You tried to divide a number by zero during execution.",
        "Division by zero is mathematically undefined.",
        "Make sure the divisor is not zero before performing the division.",
        example="if (divisor != 0) { int result = dividend / divisor; }"
    )


def explain_run002(err):
    line_info = f"Line {err.line}: " if getattr(err, "line", None) else ""
    return _fmt(
        f"{line_info}Modulo by zero",
        "You tried to calculate modulo (%) with a divisor of zero.",
        "Modulo by zero is mathematically undefined.",
        "Check that the divisor is non-zero before performing modulo operations.",
        example="if (m != 0) { int remainder = n % m; }"
    )


def explain_run003(err):
    limit = err.context.get("limit", 200000)
    return _fmt(
        "Execution step limit exceeded (Infinite Loop)",
        f"The program executed over {limit} steps without finishing.",
        "The while loop condition may never evaluate to false.",
        "Check that variables used in the loop condition are updated inside the loop body.",
        example="while (i < 10) { i = i + 1; }"
    )


def explain_run004(err):
    line_info = f"Line {err.line}: " if getattr(err, "line", None) else ""
    var = err.context.get("var")
    sug = find_suggestion(var, KEYWORDS) if var else None
    return _fmt(
        f"{line_info}Runtime evaluation error",
        err.technical,
        "The virtual machine encountered an invalid state or undefined variable during execution.",
        "Ensure all variables are declared and initialized before reading them.",
        suggestion=sug
    )


EXPLAINERS = {
    "LEX001": explain_lex001,
    "LEX002": explain_lex002,
    "SYN001": explain_syn001,
    "SYN002": explain_syn002,
    "SYN003": explain_syn003,
    "SYN004": explain_syn004,
    "SEM001": explain_sem001,
    "SEM002": explain_sem002,
    "SEM003": explain_sem003,
    "SEM004": explain_sem004,
    "SEM005": explain_sem005,
    "RUN001": explain_run001,
    "RUN002": explain_run002,
    "RUN003": explain_run003,
    "RUN004": explain_run004,
}


def explain(err):
    """Return a friendly, natural-language explanation for any error object."""
    code = getattr(err, "code", "")
    fn = EXPLAINERS.get(code)
    if fn:
        return fn(err)
    line_str = f"Line {err.line}: " if getattr(err, "line", None) else ""
    phase_str = getattr(err, "phase", "Compiler")
    tech_str = getattr(err, "technical", str(err))
    return _fmt(
        f"{line_str}{phase_str} error",
        tech_str,
        "This error type doesn't have a custom explanation template yet.",
        "Re-check the code around this line against EduLang's syntax rules.",
    )
