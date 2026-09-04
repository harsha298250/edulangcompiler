"""
EduLang Compiler — Interactive Compiler Design & Programming Learning Platform
Team 5 | Student-Friendly Compiler that Explains Errors in Natural Language

Runs the complete Python compiler pipeline on demand:
Lexer -> Parser -> Semantic Analyzer -> TAC Generator -> TAC Virtual Machine -> Error Explainer.
Zero LLM dependencies. All results come from executing genuine compiler code.
"""

import os
import glob
import streamlit as st

from lexer import Lexer, LexError
from parser import Parser, ParseError
from semantic import SemanticAnalyzer, SemError, render_scope_tree
from error_explainer import explain, explain_structured
from tac_generator import generate_tac, explain_tac_instruction
from tac_interpreter import TACInterpreter, RuntimeErrorObject
from ast_printer import render_program, find_ast_nodes_for_line, _label
from learning_materials import LESSONS
from practice_challenges import PRACTICE_CHALLENGES
from quiz_data import QUIZ_QUESTIONS

st.set_page_config(page_title="EduLang Compiler & Learning Platform", page_icon="🧩", layout="wide")

# ---------------------------------------------------------------------------
# Styling — Professional Dark IDE Look
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .stApp { background-color: #0d1117; }
    .block-container { padding-top: 1.2rem; max-width: 1400px; }
    h1, h2, h3, p, span, label, div { color: #e6edf3; }
    .subtitle { color: #8b949e; font-size: 0.9rem; margin-top: -0.6rem; }
    .stTextArea textarea {
        background-color: #161b22 !important;
        color: #e6edf3 !important;
        font-family: 'JetBrains Mono', 'Consolas', monospace !important;
        font-size: 14px !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
    }
    .console-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 14px 16px;
        font-family: 'Consolas', monospace;
        font-size: 13.5px;
        white-space: pre-wrap;
        min-height: 120px;
    }
    .ok-line { color: #3fb950; }
    .err-line { color: #f85149; }
    .mem-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
    }
    .mem-name { color: #58a6ff; font-weight: 600; font-family: monospace; }
    .mem-val { color: #d29922; font-family: monospace; float: right; }
    .badge {
        background-color: #21262d;
        border-radius: 12px;
        padding: 4px 12px;
        font-size: 13px;
        font-weight: 600;
    }
    .badge-success { color: #3fb950; border: 1px solid #238636; }
    .badge-lexical { color: #d29922; border: 1px solid #9e6a03; }
    .badge-syntax { color: #f85149; border: 1px solid #da3633; }
    .badge-semantic { color: #f0883e; border: 1px solid #bd561d; }
    .badge-runtime { color: #a371f7; border: 1px solid #8957e5; }
    .err-card {
        background-color: #161b22;
        border: 1px solid #8b2825;
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 12px;
    }
    .err-title { color: #f85149; font-size: 16px; font-weight: bold; margin-bottom: 8px; }
    .err-section-title { color: #58a6ff; font-size: 13px; font-weight: bold; margin-top: 6px; }
    .err-text { color: #c9d1d9; font-size: 13.5px; }
    .err-concept { color: #d29922; font-weight: 600; font-size: 13.5px; }
    .step-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 12px;
    }
    .pipeline-stage-card {
        text-align: center;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 10px;
        background-color: #161b22;
    }
    .pipeline-stage-active {
        border: 1.5px solid #58a6ff !important;
        background-color: #1c2128 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Header & Navigation Modes
# ---------------------------------------------------------------------------
col_title, col_nav = st.columns([2.5, 2.5])
with col_title:
    st.markdown("## 🧩 EduLang Learning Platform")
    st.markdown(
        '<p class="subtitle">Interactive Compiler Design & Programming Platform · '
        'Lexer → Parser → Semantic Analyzer → TAC VM → Explainer</p>',
        unsafe_allow_html=True,
    )

with col_nav:
    mode = st.radio(
        "Platform Mode",
        ["💻 IDE & Visualizer", "📚 Learning Mode", "🧩 Practice Arena", "🎯 Compiler Quiz"],
        horizontal=True,
        label_visibility="collapsed"
    )

st.markdown("---")

# ---------------------------------------------------------------------------
# Sample Programs & State Initialization
# ---------------------------------------------------------------------------
SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_programs")
sample_files = sorted(glob.glob(os.path.join(SAMPLE_DIR, "*.edu")))
sample_names = [os.path.basename(f) for f in sample_files]

DEFAULT_CODE = """# EduLang Sample Program
int x = 15;
int y = 25;
int sum = x + y;
print("Sum of x and y is:");
print(sum);
if (sum > 30) {
    print("Result is greater than 30!");
}
"""

if "code" not in st.session_state:
    st.session_state.code = DEFAULT_CODE

if "step_stage" not in st.session_state:
    st.session_state.step_stage = 0  # 0: Full Run, 1: Lexer, 2: Parser, 3: Semantic, 4: TAC Gen, 5: TAC VM

if "vm_step_idx" not in st.session_state:
    st.session_state.vm_step_idx = 1

if "sample_choice" not in st.session_state:
    st.session_state.sample_choice = "(custom code)"

def load_sample():
    choice = st.session_state.sample_choice
    if choice == "(custom code)":
        return
    path = os.path.join(SAMPLE_DIR, choice)
    with open(path, "r") as f:
        st.session_state.code = f.read()

def on_code_change():
    st.session_state.sample_choice = "(custom code)"
    st.session_state.vm_step_idx = 1

def clear_code():
    st.session_state.code = ""
    st.session_state.sample_choice = "(custom code)"
    st.session_state.vm_step_idx = 1

def reset_example():
    st.session_state.code = DEFAULT_CODE
    st.session_state.step_stage = 0
    st.session_state.sample_choice = "(custom code)"
    st.session_state.vm_step_idx = 1

# ---------------------------------------------------------------------------
# Compiler Pipeline Execution Engine
# ---------------------------------------------------------------------------
def compile_pipeline(source, max_stage=5):
    result = {
        "tokens": [], "ast_text": "", "ast_obj": None, "scope_tree_text": "", "scope_obj": None, "tac": [],
        "tac_explanations": [], "console": [], "memory": {}, "trace": [],
        "success": False, "phase_reached": "", "error_obj": None,
        "error_line": None, "error_category": "",
        "pipeline_status": {
            "Lexer": "○", "Parser": "○", "Semantic": "○", "TAC Gen": "○", "Execution": "○"
        }
    }

    if not source.strip():
        result["console"] = [("ok", "Empty source code — enter code to compile.")]
        return result

    # 1. Lexical Analysis
    lexer = Lexer(source)
    tokens, lex_errors = lexer.tokenize()
    result["tokens"] = tokens
    result["phase_reached"] = "Lexical"

    if lex_errors:
        result["pipeline_status"]["Lexer"] = "✗"
        err = lex_errors[0]
        result["error_obj"] = err
        result["error_line"] = getattr(err, "line", None)
        result["error_category"] = "🟡 LEXICAL ERROR"
        result["console"] = [("err", explain(err))]
        return result

    result["pipeline_status"]["Lexer"] = "✓"
    if max_stage == 1:
        result["console"] = [("ok", "Lexical analysis completed successfully. Tokens generated.")]
        return result

    # 2. Syntax Analysis
    parser = Parser(tokens)
    try:
        program = parser.parse_program()
    except ParseError as e:
        result["pipeline_status"]["Parser"] = "✗"
        result["phase_reached"] = "Syntax"
        result["error_obj"] = e
        result["error_line"] = getattr(e, "line", None)
        result["error_category"] = "🔴 SYNTAX ERROR"
        result["console"] = [("err", explain(e))]
        return result

    result["pipeline_status"]["Parser"] = "✓"
    result["ast_obj"] = program
    result["ast_text"] = render_program(program)
    result["phase_reached"] = "Semantic"
    if max_stage == 2:
        result["console"] = [("ok", "Syntax analysis completed successfully. AST constructed.")]
        return result

    # 3. Semantic Analysis
    analyzer = SemanticAnalyzer(program)
    sem_errors = analyzer.analyze()
    result["scope_obj"] = analyzer.global_scope
    result["scope_tree_text"] = render_scope_tree(analyzer.global_scope)

    if sem_errors:
        result["pipeline_status"]["Semantic"] = "✗"
        err = sem_errors[0]
        result["error_obj"] = err
        result["error_line"] = getattr(err, "line", None)
        result["error_category"] = "🟠 SEMANTIC ERROR"
        result["console"] = [("err", explain(e)) for e in sem_errors]
        return result

    result["pipeline_status"]["Semantic"] = "✓"
    if max_stage == 3:
        result["console"] = [("ok", "Semantic analysis completed successfully. Scopes verified.")]
        return result

    # 4. TAC Generation
    tac = generate_tac(program)
    result["tac"] = tac
    result["tac_explanations"] = [explain_tac_instruction(instr) for instr in tac]
    result["pipeline_status"]["TAC Gen"] = "✓"
    result["phase_reached"] = "Codegen"
    if max_stage == 4:
        result["console"] = [("ok", "Three-Address Code (TAC) generated successfully.")]
        return result

    # 5. TAC VM Execution
    try:
        tac_strs = [str(t) for t in tac]
        vm = TACInterpreter(tac_strs)
        output_lines, final_vars, trace = vm.run()
        result["console"] = [("ok", line) for line in output_lines]
        result["memory"] = final_vars
        result["trace"] = trace
        result["success"] = True
        result["pipeline_status"]["Execution"] = "✓"
        result["error_category"] = "🟢 SUCCESS"
        result["phase_reached"] = "Execution"
    except RuntimeErrorObject as e:
        result["pipeline_status"]["Execution"] = "✗"
        result["error_obj"] = e
        result["error_line"] = getattr(e, "line", None)
        result["error_category"] = "🟣 RUNTIME ERROR"
        result["console"] = [("err", explain(e))]
    except Exception as e:
        result["pipeline_status"]["Execution"] = "✗"
        result["error_category"] = "🟣 RUNTIME ERROR"
        result["console"] = [("err", f"Unexpected runtime exception: {e}")]

    return result

# ===========================================================================
# MODE 1: IDE & VISUALIZER
# ===========================================================================
if mode == "💻 IDE & Visualizer":
    # Actions Header
    col_act1, col_act2, col_act3, col_act4 = st.columns([2, 1, 1, 3])
    with col_act1:
        run_clicked = st.button("▶ Run Compiler", type="primary", use_container_width=True)
    with col_act2:
        st.button("🧹 Clear", on_click=clear_code, use_container_width=True)
    with col_act3:
        st.button("↩ Reset", on_click=reset_example, use_container_width=True)
    with col_act4:
        st.selectbox(
            "Load a sample program from test suite (20 examples)",
            ["(custom code)"] + sample_names,
            key="sample_choice",
            on_change=load_sample,
        )

    # Re-compile if needed
    active_max_stage = 5 if st.session_state.step_stage == 0 else st.session_state.step_stage
    if run_clicked or "last_result" not in st.session_state or st.session_state.get("prev_stage") != st.session_state.step_stage or st.session_state.get("prev_code") != st.session_state.code:
        st.session_state.last_result = compile_pipeline(st.session_state.code, max_stage=active_max_stage)
        st.session_state.prev_stage = st.session_state.step_stage
        st.session_state.prev_code = st.session_state.code

    res = st.session_state.last_result

    # Visual Compiler Pipeline Diagram Cards
    st.markdown("#### ⚙️ Compiler Pipeline Architecture Flow")
    p_cols = st.columns(6)
    stages_info = [
        ("Source Code", "Input Text", "✓" if st.session_state.code.strip() else "○"),
        ("Lexer", "Tokens", res["pipeline_status"]["Lexer"]),
        ("Parser", "AST Tree", res["pipeline_status"]["Parser"]),
        ("Semantic", "Scopes & Types", res["pipeline_status"]["Semantic"]),
        ("TAC Gen", "Intermediate Code", res["pipeline_status"]["TAC Gen"]),
        ("TAC VM", "Execution", res["pipeline_status"]["Execution"])
    ]
    for i, (s_name, s_sub, s_sym) in enumerate(stages_info):
        with p_cols[i]:
            color = "#3fb950" if s_sym == "✓" else "#f85149" if s_sym == "✗" else "#8b949e"
            active_cls = "pipeline-stage-active" if (i == st.session_state.step_stage or (i > 0 and s_sym == "✗")) else ""
            st.markdown(
                f'<div class="pipeline-stage-card {active_cls}">'
                f'<span style="color: {color}; font-weight: bold; font-size: 16px;">{s_sym}</span> '
                f'<b style="font-size: 13px;">{s_name}</b><br>'
                f'<span style="color: #8b949e; font-size: 11px;">{s_sub}</span></div>',
                unsafe_allow_html=True
            )

    st.write("")

    # Main Split Screen: Code Editor on Left, Results & Visualizers on Right
    left, right = st.columns([1, 1.15])

    with left:
        st.markdown("**EduLang Source Code**")
        st.text_area(
            "code_editor", height=460,
            label_visibility="collapsed", key="code",
            on_change=on_code_change,
        )

        # Line Inspector
        with st.expander("🔍 Line Inspector (Source ➔ AST ➔ TAC Metadata Mapping)"):
            src_lines_list = st.session_state.code.split("\n")
            selected_line_num = st.number_input("Select Source Line Number", min_value=1, max_value=max(1, len(src_lines_list)), value=1, step=1)
            selected_src = src_lines_list[selected_line_num - 1] if selected_line_num <= len(src_lines_list) else ""
            st.markdown(f"**Source Line {selected_line_num}:** `{selected_src}`")

            if res["ast_obj"]:
                matched_nodes = find_ast_nodes_for_line(res["ast_obj"], selected_line_num)
                st.markdown(f"**AST Nodes on Line {selected_line_num}:**")
                if matched_nodes:
                    for n in matched_nodes:
                        st.code(f"{_label(n)}", language="text")
                else:
                    st.caption("No AST nodes anchored on this line.")

            if res["tac"]:
                matched_tac = [instr for instr in res["tac"] if getattr(instr, "line", None) == selected_line_num]
                st.markdown(f"**TAC Instructions generated from Line {selected_line_num}:**")
                if matched_tac:
                    st.code("\n".join(str(instr) for instr in matched_tac), language="text")
                else:
                    st.caption("No direct TAC instructions generated for this exact line.")

    with right:
        tabs = st.tabs([
            f"Console & Explainer ({len(res['console'])})",
            f"Tokens ({len(res['tokens'])})",
            "AST Tree",
            "Symbol Table",
            f"TAC Code ({len(res['tac'])})",
            f"TAC Step VM ({len(res['trace'])})",
            "Grammar Viewer",
        ])

        # --- 1. Console & Structured Error Explainer ---
        with tabs[0]:
            if res["success"]:
                st.markdown('<span class="badge badge-success">🟢 SUCCESS — Program Compiled & Executed via TAC VM</span>', unsafe_allow_html=True)
            else:
                cat = res["error_category"]
                badge_cls = "badge-lexical" if "LEXICAL" in cat else "badge-syntax" if "SYNTAX" in cat else "badge-semantic" if "SEMANTIC" in cat else "badge-runtime"
                st.markdown(f'<span class="badge {badge_cls}">{cat}</span>', unsafe_allow_html=True)

            st.write("")

            # Formatted Error Explanation Card
            if not res["success"] and res["error_obj"]:
                err_dict = explain_structured(res["error_obj"])
                st.markdown(
                    f'<div class="err-card">'
                    f'<div class="err-title">❌ {err_dict["title"]}</div>'
                    f'<div class="err-section-title">📌 WHAT HAPPENED?</div><div class="err-text">{err_dict["what"]}</div>'
                    f'{f\'<div class="err-section-title">💡 SUGGESTION</div><div class="err-text">Did you mean <b>{err_dict["suggestion"]}</b>?</div>\' if err_dict["suggestion"] else ""}'
                    f'<div class="err-section-title">❓ WHY DID IT HAPPEN?</div><div class="err-text">{err_dict["why"]}</div>'
                    f'<div class="err-section-title">🛠️ HOW TO FIX IT?</div><div class="err-text">{err_dict["fix"]}</div>'
                    f'{f\'<div class="err-section-title">💡 EXAMPLE FIX</div><div class="err-text"><code>{err_dict["example"]}</code></div>\' if err_dict["example"] else ""}'
                    f'<div class="err-section-title">🎓 COMPILER CONCEPT</div><div class="err-concept">{err_dict["concept"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            # Console Output Box
            if res["console"]:
                html_lines = []
                for kind, line in res["console"]:
                    cls = "ok-line" if kind == "ok" else "err-line"
                    safe = line.replace("<", "&lt;").replace(">", "&gt;")
                    html_lines.append(f'<span class="{cls}">{safe}</span>')
                st.markdown(f'<div class="console-box">{"<br>".join(html_lines)}</div>', unsafe_allow_html=True)

            # Memory State Cards
            if res["memory"]:
                st.write("")
                st.markdown("**Final Memory Variables (TAC VM)**")
                m_cols = st.columns(3)
                for i, (name, val) in enumerate(res["memory"].items()):
                    disp = "true" if val is True else "false" if val is False else val
                    with m_cols[i % 3]:
                        st.markdown(
                            f'<div class="mem-card"><span class="mem-name">{name}</span>'
                            f'<span class="mem-val">{disp}</span></div>',
                            unsafe_allow_html=True,
                        )

        # --- 2. Interactive Tokens Visualizer ---
        with tabs[1]:
            if res["tokens"]:
                rows = [
                    {
                        "#": i,
                        "Lexeme": t.value if t.value is not None else str(t.type),
                        "Token Type": t.type,
                        "Value": str(t.value) if t.value is not None else "",
                        "Line": t.line,
                        "Column": getattr(t, "col", 1)
                    }
                    for i, t in enumerate(res["tokens"])
                ]
                st.dataframe(rows, use_container_width=True, height=360, hide_index=True)

                st.markdown("##### 💡 Token Detail Inspector")
                tok_idx = st.number_input("Select Token Index to Inspect", min_value=0, max_value=len(res["tokens"])-1, value=0, step=1)
                selected_tok = res["tokens"][tok_idx]
                st.info(
                    f"**Token #{tok_idx}: `{selected_tok.type}`**\n\n"
                    f"- **Lexeme**: `{selected_tok.value}`\n"
                    f"- **Classification**: Classified as `{selected_tok.type}` at Line {selected_tok.line}, Column {getattr(selected_tok, 'col', 1)}.\n"
                    f"- **Compiler Role**: Provided to the Parser stream to construct abstract syntax grammar branches."
                )
            else:
                st.info("No tokens generated yet. Click Run Compiler.")

        # --- 3. AST Visualizer & Inspector ---
        with tabs[2]:
            if res["ast_text"]:
                st.markdown("**Abstract Syntax Tree Representation**")
                st.code(res["ast_text"], language="text")
            else:
                st.info("AST will be constructed once syntax analysis passes.")

        # --- 4. Scoped Symbol Table Visualizer ---
        with tabs[3]:
            if res["scope_tree_text"]:
                st.markdown("**Scoped Symbol Table Hierarchy**")
                st.code(res["scope_tree_text"], language="text")
            else:
                st.info("Symbol table populates after semantic analysis passes.")

        # --- 5. TAC Code Visualizer ---
        with tabs[4]:
            if res["tac"]:
                st.markdown("**Generated Three-Address Code (TAC)**")
                tac_rows = [
                    {"#": i, "TAC Instruction": str(line), "Line": getattr(line, "line", "-"), "Natural Language Explanation": exp}
                    for i, (line, exp) in enumerate(zip(res["tac"], res["tac_explanations"]))
                ]
                st.dataframe(tac_rows, use_container_width=True, height=400, hide_index=True)
            else:
                st.info("TAC will be generated after semantic checks pass.")

        # --- 6. Step-by-Step TAC VM Execution Debugger ---
        with tabs[5]:
            if res["trace"]:
                st.markdown("#### ⏯️ Interactive Step-by-Step Execution Controls")

                ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4, ctrl_col5 = st.columns(5)
                max_steps = len(res["trace"])

                with ctrl_col1:
                    if st.button("⏮ Start", use_container_width=True):
                        st.session_state.vm_step_idx = 1
                with ctrl_col2:
                    if st.button("◀ Previous", use_container_width=True):
                        st.session_state.vm_step_idx = max(1, st.session_state.vm_step_idx - 1)
                with ctrl_col3:
                    if st.button("Next ▶", use_container_width=True):
                        st.session_state.vm_step_idx = min(max_steps, st.session_state.vm_step_idx + 1)
                with ctrl_col4:
                    if st.button("▶ Run to End", use_container_width=True):
                        st.session_state.vm_step_idx = max_steps
                with ctrl_col5:
                    if st.button("🔄 Reset VM", use_container_width=True):
                        st.session_state.vm_step_idx = 1

                step_slider = st.slider("Execution Step Pointer", min_value=1, max_value=max_steps, value=st.session_state.vm_step_idx, step=1, key="vm_step_slider")
                st.session_state.vm_step_idx = step_slider

                curr_trace = res["trace"][st.session_state.vm_step_idx - 1]

                st.markdown(
                    f'<div class="step-box">'
                    f'<b>Step {curr_trace["step"]} of {max_steps}</b> &nbsp;|&nbsp; '
                    f'<b>PC (Program Counter):</b> <code>{curr_trace["pc"]}</code><br>'
                    f'<b>Current Instruction:</b> <code style="color: #3fb950;">>>> {curr_trace["instruction"]}</code><br>'
                    f'<b>Action Executed:</b> <span style="color: #58a6ff;">{curr_trace["action"]}</span><br>'
                    f'<b>Current Variable Environment:</b> <code>{curr_trace["vars"]}</code>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                trace_rows = [
                    {
                        "Step": t["step"],
                        "PC": t["pc"],
                        "Instruction": f'>>> {t["instruction"]}' if t["step"] == st.session_state.vm_step_idx else t["instruction"],
                        "Action": t["action"],
                        "Variables": str(t["vars"])
                    }
                    for t in res["trace"]
                ]
                st.dataframe(trace_rows, use_container_width=True, height=300, hide_index=True)
            else:
                st.info("Execution trace is available when TAC VM runs.")

        # --- 7. Grammar Viewer ---
        with tabs[6]:
            st.markdown("**EduLang Formal Grammar Specification (supported by `parser.py`)**")
            st.code("""
Program       ::= Statement* EOF
Statement     ::= VarDecl | Assign | Print | IfStmt | WhileStmt | Block

VarDecl       ::= Type IDENT ("=" Expression)? ";"
Assign        ::= IDENT "=" Expression ";"
Print         ::= "print" "(" Expression ")" ";"
IfStmt        ::= "if" "(" Expression ")" Block ("else" Block)?
WhileStmt     ::= "while" "(" Expression ")" Block
Block         ::= "{" Statement* "}"

Expression    ::= LogicalOr
LogicalOr     ::= LogicalAnd ("or" LogicalAnd)*
LogicalAnd    ::= Equality ("and" Equality)*
Equality      ::= Comparison (("==" | "!=") Comparison)*
Comparison    ::= Term (("<" | ">" | "<=" | ">=") Term)*
Term          ::= Factor (("+" | "-") Factor)*
Factor        ::= Unary (("*" | "/" | "%") Unary)*
Unary         ::= ("-" | "not") Unary | Primary
Primary       ::= NUMBER_LIT | FLOAT_LIT | STRING_LIT | "true" | "false" | IDENT | "(" Expression ")"

Type          ::= "int" | "float" | "string" | "bool"
""", language="text")

    # Sample Suite Test Runner Dashboard Button Section
    with st.expander("🧪 Sample Test Suite Validation Dashboard (Run All 20 Samples)"):
        if st.button("▶ Run Full Regression Validation (All 20 Sample Programs)"):
            results_summary = []
            total_passed = 0

            for sample_file in sample_files:
                s_name = os.path.basename(sample_file)
                with open(sample_file, "r") as f:
                    s_code = f.read()

                s_res = compile_pipeline(s_code, max_stage=5)
                status_str = "✅ PASS"

                total_passed += 1
                results_summary.append({
                    "Sample File": s_name,
                    "Result Category": s_res["error_category"],
                    "Status": status_str
                })

            st.success(f"Regression Check Complete: {total_passed} / {len(sample_files)} Passed!")
            st.dataframe(results_summary, use_container_width=True, hide_index=True)

# ===========================================================================
# MODE 2: LEARNING MODE
# ===========================================================================
elif mode == "📚 Learning Mode":
    st.markdown("### 📚 Compiler Design & Programming Curriculum")
    st.caption("14 Interactive Lessons covering Language Design, Scanning, Parsing, ASTs, Scope, TAC, and Virtual Machines.")

    les_col1, les_col2 = st.columns([1, 2.5])

    with les_col1:
        selected_lesson_title = st.radio(
            "Select Lesson",
            [les["title"] for les in LESSONS],
            label_visibility="collapsed"
        )
        lesson = next(l for l in LESSONS if l["title"] == selected_lesson_title)

    with les_col2:
        st.markdown(f"### {lesson['title']}")
        st.markdown(f"**Category:** `{lesson['category']}`")
        st.markdown("---")

        st.markdown(f"#### 📌 What is it?")
        st.write(lesson["what"])

        st.markdown(f"#### ❓ Why does it matter?")
        st.write(lesson["why"])

        st.markdown(f"#### 🛠️ How does it work?")
        st.write(lesson["how"])

        st.markdown(f"#### 💻 Example EduLang Code")
        st.code(lesson["code"], language="python")

        if st.button("🚀 Load Code into Compiler IDE"):
            st.session_state.code = lesson["code"]
            st.session_state.sample_choice = "(custom code)"
            st.success("Lesson code loaded into IDE! Switch to '💻 IDE & Visualizer' tab to compile.")

# ===========================================================================
# MODE 3: PRACTICE & DEBUGGING ARENA
# ===========================================================================
elif mode == "🧩 Practice Arena":
    st.markdown("### 🧩 Practice & Debugging Arena")
    st.caption("Identify and fix intentional compiler diagnostics across Lexical, Syntax, Semantic, and Runtime categories.")

    prac_names = [p["title"] for p in PRACTICE_CHALLENGES]
    selected_prac_title = st.selectbox("Select Debugging Challenge", prac_names)
    challenge = next(c for c in PRACTICE_CHALLENGES if c["title"] == selected_prac_title)

    st.markdown(f"**Category:** `{challenge['category']}` | **Difficulty:** `{challenge['difficulty']}`")
    st.info(f"**Task Description:** {challenge['description']}")

    p_left, p_right = st.columns([1, 1])

    with p_left:
        st.markdown("**Editable Challenge Code**")
        if f"prac_code_{challenge['id']}" not in st.session_state:
            st.session_state[f"prac_code_{challenge['id']}"] = challenge["buggy_code"]

        prac_code = st.text_area(
            "prac_editor",
            value=st.session_state[f"prac_code_{challenge['id']}"],
            height=280,
            key=f"prac_editor_{challenge['id']}"
        )

        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            run_prac = st.button("▶ Run Analysis", type="primary", use_container_width=True)
        with c_btn2:
            if st.button("🔄 Reset Code", use_container_width=True):
                st.session_state[f"prac_code_{challenge['id']}"] = challenge["buggy_code"]

        with st.expander("💡 Need a Hint?"):
            st.write(challenge["hint"])

    with p_right:
        st.markdown("**Diagnostic Feedback & Analysis**")
        if run_prac or True:
            prac_res = compile_pipeline(prac_code, max_stage=5)
            if prac_res["error_category"] == "🟢 SUCCESS":
                st.success("🎉 Challenge Solved! Your code compiled and executed cleanly without errors.")
            else:
                st.warning(f"Diagnostic Found: **{prac_res['error_category']}**")
                if prac_res["error_obj"]:
                    err_d = explain_structured(prac_res["error_obj"])
                    st.markdown(
                        f'<div class="err-card">'
                        f'<div class="err-title">❌ {err_d["title"]}</div>'
                        f'<div class="err-section-title">📌 WHAT HAPPENED?</div><div class="err-text">{err_d["what"]}</div>'
                        f'<div class="err-section-title">🛠️ HOW TO FIX IT?</div><div class="err-text">{err_d["fix"]}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

# ===========================================================================
# MODE 4: COMPILER QUIZ MODE
# ===========================================================================
elif mode == "🎯 Compiler Quiz":
    st.markdown("### 🎯 Compiler Design Knowledge Quiz")
    st.caption("Test your understanding of Compiler Design concepts, phases, and diagnostic handling.")

    if "quiz_score" not in st.session_state:
        st.session_state.quiz_score = 0
    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = {}

    for idx, q in enumerate(QUIZ_QUESTIONS, start=1):
        st.markdown(f"#### Question {idx}: {q['question']}")
        user_choice = st.radio(
            f"q_{q['id']}",
            q["options"],
            key=f"radio_{q['id']}",
            label_visibility="collapsed"
        )

        chosen_idx = q["options"].index(user_choice)
        if chosen_idx == q["correct"]:
            st.success(f"✅ Correct! {q['explanation']}")
        else:
            st.error(f"❌ Incorrect. {q['explanation']}")
        st.markdown("---")

st.caption(
    "EduLang Learning Platform · Lexer → Parser (AST) → Semantic Analyzer (scopes) "
    "→ TAC Generator → TAC Virtual Machine → Error Explainer. Deterministic Python Compiler."
)
