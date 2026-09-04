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

from lexer import Lexer, LexError, explain_token
from parser import Parser, ParseError
from semantic import SemanticAnalyzer, SemError, render_scope_tree, find_shadowed_variables
from error_explainer import explain, explain_structured, get_lesson_id_for_error, get_practice_category_for_error
from tac_generator import generate_tac, explain_tac_instruction
from tac_interpreter import TACInterpreter, RuntimeErrorObject
from ast_printer import render_program, find_ast_nodes_for_line, get_all_ast_nodes, explain_ast_node, _label
from learning_materials import LESSONS
from practice_challenges import PRACTICE_CHALLENGES
from quiz_data import QUIZ_QUESTIONS

st.set_page_config(page_title="EduLang Compiler & Learning Platform", page_icon="🧩", layout="wide")

# ---------------------------------------------------------------------------
# Styling — Professional Dark IDE & Academic Platform Look
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .stApp { background-color: #0d1117; }
    .block-container { padding-top: 1.2rem; max-width: 1400px; }
    h1, h2, h3, p, span, label, div { color: #e6edf3; }
    .subtitle { color: #8b949e; font-size: 0.95rem; margin-top: -0.6rem; }
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
    .err-highlight-box {
        background-color: #1c2128;
        border: 1px solid #d29922;
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 12px;
    }
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
    .feature-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Header & Global Navigation Modes
# ---------------------------------------------------------------------------
st.markdown("## 🧩 EduLang Interactive Compiler Learning Platform")
st.markdown(
    '<p class="subtitle">A Student-Friendly Educational Compiler That Explains Errors in Natural Language · '
    'Lexer → Parser → Semantic Analyzer → TAC VM → Explainer</p>',
    unsafe_allow_html=True,
)

# Global Session State Progress Initialization
if "progress_lessons" not in st.session_state:
    st.session_state.progress_lessons = set()
if "progress_challenges" not in st.session_state:
    st.session_state.progress_challenges = set()
if "target_lesson_id" not in st.session_state:
    st.session_state.target_lesson_id = None
if "target_practice_category" not in st.session_state:
    st.session_state.target_practice_category = None
if "nav_mode" not in st.session_state:
    st.session_state.nav_mode = "🏠 Home"

# Header Progress Bar & Mode Selection
hdr_col1, hdr_col2 = st.columns([3.5, 1])
with hdr_col1:
    mode = st.radio(
        "Select Platform Mode",
        ["🏠 Home", "💻 Compiler IDE", "🎓 Learn Compiler Pipeline", "📚 Learning Mode", "🧩 Practice Arena", "🎯 Compiler Quiz", "📖 Language Reference"],
        horizontal=True,
        key="nav_mode"
    )
with hdr_col2:
    total_l = len(LESSONS)
    total_c = len(PRACTICE_CHALLENGES)
    l_done = len(st.session_state.progress_lessons)
    c_done = len(st.session_state.progress_challenges)
    st.caption(f"**Session Progress**: Lessons `{l_done}/{total_l}` | Practice `{c_done}/{total_c}`")
    st.progress((l_done + c_done) / max(1, total_l + total_c))

st.markdown("---")

# ---------------------------------------------------------------------------
# Sample Programs & Categorized Selection
# ---------------------------------------------------------------------------
SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_programs")
sample_files = sorted(glob.glob(os.path.join(SAMPLE_DIR, "*.edu"))) if os.path.exists(SAMPLE_DIR) else []
sample_names = [os.path.basename(f) for f in sample_files]

SAMPLE_CATEGORIES = {
    "--- BASIC EXAMPLES ---": [
        "01_valid_arithmetic.edu", "02_variables.edu", "03_float_calculations.edu",
        "04_string_concatenation.edu", "05_boolean_expressions.edu"
    ],
    "--- CONTROL FLOW ---": [
        "06_if_else.edu", "07_while_loop.edu", "08_nested_blocks.edu",
        "19_nested_scope.edu", "20_complex_precedence.edu"
    ],
    "--- ERROR DIAGNOSTICS ---": [
        "09_missing_semicolon.edu", "10_invalid_character.edu", "11_unterminated_string.edu",
        "12_undeclared_variable.edu", "13_redeclared_variable.edu", "14_type_mismatch.edu",
        "15_invalid_condition.edu", "16_division_by_zero.edu", "17_modulo_by_zero.edu",
        "18_multiple_semantic_errors.edu"
    ]
}

SAMPLE_DROPDOWN_FLAT = ["(custom code)"]
for cat_name, file_list in SAMPLE_CATEGORIES.items():
    SAMPLE_DROPDOWN_FLAT.append(cat_name)
    for f in file_list:
        if f in sample_names:
            SAMPLE_DROPDOWN_FLAT.append(f)

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
    st.session_state.step_stage = 0  # 0: Full Run

if "vm_step_idx" not in st.session_state:
    st.session_state.vm_step_idx = 1

if "sample_choice" not in st.session_state:
    st.session_state.sample_choice = "(custom code)"

def load_sample():
    choice = st.session_state.sample_choice
    if choice.startswith("---") or choice == "(custom code)":
        return
    path = os.path.join(SAMPLE_DIR, choice)
    if os.path.exists(path):
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
# Compiler Pipeline Execution Engine (Stale Data Protected)
# ---------------------------------------------------------------------------
def compile_pipeline(source, max_stage=5):
    result = {
        "tokens": [], "ast_text": "", "ast_obj": None, "scope_tree_text": "", "scope_obj": None, "tac": [],
        "tac_explanations": [], "console": [], "memory": {}, "trace": [],
        "success": False, "phase_reached": "", "error_obj": None,
        "error_line": None, "error_col": None, "error_category": "",
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
    result["phase_reached"] = "Lexical"

    if lex_errors:
        result["pipeline_status"] = {"Lexer": "✗", "Parser": "—", "Semantic": "—", "TAC Gen": "—", "Execution": "—"}
        err = lex_errors[0]
        result["error_obj"] = err
        result["error_line"] = getattr(err, "line", None)
        result["error_col"] = getattr(err, "col", None)
        result["error_category"] = "🟡 LEXICAL ERROR"
        result["console"] = [("err", explain(err))]
        result["tokens"] = []
        return result

    result["tokens"] = tokens
    result["pipeline_status"]["Lexer"] = "✓"
    if max_stage == 1:
        result["console"] = [("ok", "Lexical analysis completed successfully. Tokens generated.")]
        return result

    # 2. Syntax Analysis
    parser = Parser(tokens)
    try:
        program = parser.parse_program()
    except ParseError as e:
        result["pipeline_status"] = {"Lexer": "✓", "Parser": "✗", "Semantic": "—", "TAC Gen": "—", "Execution": "—"}
        result["phase_reached"] = "Syntax"
        result["error_obj"] = e
        result["error_line"] = getattr(e, "line", None)
        result["error_col"] = getattr(e, "col", None)
        result["error_category"] = "🔴 SYNTAX ERROR"
        result["console"] = [("err", explain(e))]
        result["ast_obj"] = None
        result["ast_text"] = ""
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
        result["pipeline_status"] = {"Lexer": "✓", "Parser": "✓", "Semantic": "✗", "TAC Gen": "—", "Execution": "—"}
        err = sem_errors[0]
        result["error_obj"] = err
        result["error_line"] = getattr(err, "line", None)
        result["error_col"] = getattr(err, "col", None)
        result["error_category"] = "🟠 SEMANTIC ERROR"
        result["console"] = [("err", explain(e)) for e in sem_errors]
        result["tac"] = []
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
        vm = TACInterpreter(tac)
        output_lines, final_vars, trace = vm.run()
        result["console"] = [("ok", line) for line in output_lines]
        result["memory"] = final_vars
        result["trace"] = trace
        result["success"] = True
        result["pipeline_status"]["Execution"] = "✓"
        result["error_category"] = "🟢 SUCCESS"
        result["phase_reached"] = "Execution"
    except RuntimeErrorObject as e:
        result["pipeline_status"] = {"Lexer": "✓", "Parser": "✓", "Semantic": "✓", "TAC Gen": "✓", "Execution": "✗"}
        result["error_obj"] = e
        result["error_line"] = getattr(e, "line", None)
        result["error_col"] = getattr(e, "col", None)
        result["error_category"] = "🟣 RUNTIME ERROR"
        result["console"] = [("err", explain(e))]
    except Exception as e:
        result["pipeline_status"] = {"Lexer": "✓", "Parser": "✓", "Semantic": "✓", "TAC Gen": "✓", "Execution": "✗"}
        result["error_category"] = "🟣 RUNTIME ERROR"
        result["console"] = [("err", f"Unexpected runtime exception: {e}")]

    return result

# ===========================================================================
# MODE 0: HOME / LANDING DASHBOARD
# ===========================================================================
if mode == "🏠 Home":
    st.markdown("### 🏠 Welcome to EduLang Compiler & Learning Laboratory")
    st.markdown(
        "**EduLang** is an interactive compiler design and programming platform built for students and educators. "
        "Write code, observe how each compiler phase transforms instructions, and understand errors in plain English."
    )

    h_col1, h_col2, h_col3, h_col4, h_col5 = st.columns(5)
    with h_col1:
        if st.button("💻 Open IDE", use_container_width=True, type="primary"):
            st.session_state.nav_mode = "💻 Compiler IDE"
            st.rerun()
    with h_col2:
        if st.button("🎓 Pipeline Mode", use_container_width=True):
            st.session_state.nav_mode = "🎓 Learn Compiler Pipeline"
            st.rerun()
    with h_col3:
        if st.button("📚 Curriculum", use_container_width=True):
            st.session_state.nav_mode = "📚 Learning Mode"
            st.rerun()
    with h_col4:
        if st.button("🧩 Practice", use_container_width=True):
            st.session_state.nav_mode = "🧩 Practice Arena"
            st.rerun()
    with h_col5:
        if st.button("🎯 Quiz", use_container_width=True):
            st.session_state.nav_mode = "🎯 Compiler Quiz"
            st.rerun()

    st.markdown("---")

    st.markdown("#### 🌟 Platform Feature Highlights")
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        st.markdown(
            '<div class="feature-card">'
            '<b>🔍 1. Lexical Analysis & Token Inspection</b><br>'
            'Scans raw characters into typed tokens with line/column metadata. Select any token for dynamic explanation.'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="feature-card">'
            '<b>🌳 2. Abstract Syntax Tree (AST) Visualizer</b><br>'
            'Constructs a hierarchical AST removing concrete punctuation. Inspect nodes with direct source statement connections.'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="feature-card">'
            '<b>📚 3. Scoped Symbol Tables & Lookup Tracer</b><br>'
            'Tracks variable declarations across global and block scope levels. Simulates scope lookup and flags variable shadowing.'
            '</div>',
            unsafe_allow_html=True
        )
    with f_col2:
        st.markdown(
            '<div class="feature-card">'
            '<b>⚡ 4. Three-Address Code (TAC) Intermediate Code</b><br>'
            'Flattens complex expressions into primitive instructions with temporary variables (`t0`, `t1`) and bi-directional source mapping.'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="feature-card">'
            '<b>⏯️ 5. Step-by-Step TAC VM Execution Debugger</b><br>'
            'Step through execution line-by-line with Program Counter controls, variable environment inspection, and safety step limits.'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="feature-card">'
            '<b>🎓 6. Student-Friendly Natural-Language Error Explainer</b><br>'
            'Translates compiler diagnostic codes (`LEX001`, `SYN001`, `SEM001`, `RUN001`) into plain English explanations with typo suggestions.'
            '</div>',
            unsafe_allow_html=True
        )

# ===========================================================================
# MODE 1: IDE & VISUALIZER
# ===========================================================================
elif mode == "💻 Compiler IDE":
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
            "Load Sample Program (Categorized)",
            SAMPLE_DROPDOWN_FLAT,
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
        st.markdown("**EduLang Source Code Editor**")
        st.text_area(
            "code_editor", height=460,
            label_visibility="collapsed", key="code",
            on_change=on_code_change,
        )

        # Line Inspector (Source ➔ AST ➔ TAC Mapping)
        with st.expander("🔍 Line Inspector (Source ➔ AST ➔ TAC Mapping)"):
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
                    st.caption("No direct TAC instructions generated for this line.")

    with right:
        tabs = st.tabs([
            f"Console ({len(res['console'])})",
            f"Tokens ({len(res['tokens'])})",
            "AST Tree",
            "Symbol Table",
            f"TAC ({len(res['tac'])})",
            f"Step VM ({len(res['trace'])})",
            "Grammar",
        ])

        # --- 1. Console & Educational Error Explainer ---
        with tabs[0]:
            if res["success"]:
                st.markdown('<span class="badge badge-success">🟢 SUCCESS — Program Compiled & Executed via TAC VM</span>', unsafe_allow_html=True)
            elif res["error_category"]:
                cat = res["error_category"]
                badge_cls = "badge-lexical" if "LEXICAL" in cat else "badge-syntax" if "SYNTAX" in cat else "badge-semantic" if "SEMANTIC" in cat else "badge-runtime"
                st.markdown(f'<span class="badge {badge_cls}">{cat}</span>', unsafe_allow_html=True)
            else:
                st.info("Ready to compile. Enter source code and click ▶ Run Compiler.")

            st.write("")

            # Error Location Caret Pointer Panel
            if not res["success"] and res["error_line"]:
                err_line_num = res["error_line"]
                err_col_num = res["error_col"] or 1
                src_lines = st.session_state.code.split("\n")
                preview_formatted_lines = []
                for idx, line_text in enumerate(src_lines, start=1):
                    if idx == err_line_num:
                        preview_formatted_lines.append(f">>> Line {idx:2d} | {line_text}")
                        caret_spaces = " " * max(0, err_col_num - 1)
                        preview_formatted_lines.append(f"           | {caret_spaces}^")
                    elif abs(idx - err_line_num) <= 1:
                        preview_formatted_lines.append(f"    Line {idx:2d} | {line_text}")

                formatted_block = "\n".join(preview_formatted_lines)
                st.markdown(
                    f'<div class="err-highlight-box"><b>Source Error Location Pointer</b><br><br>'
                    f'<pre style="margin: 0; font-family: Consolas, monospace; line-height: 1.4; white-space: pre;">{formatted_block}</pre></div>',
                    unsafe_allow_html=True
                )

            # Formatted Educational Error Explanation Card
            if not res["success"] and res["error_obj"]:
                err_dict = explain_structured(res["error_obj"])
                sug_html = f'<div class="err-section-title">💡 SUGGESTION</div><div class="err-text">Did you mean <b>{err_dict["suggestion"]}</b>?</div>' if err_dict["suggestion"] else ""
                ex_html = f'<div class="err-section-title">💡 EXAMPLE FIX</div><div class="err-text"><code>{err_dict["example"]}</code></div>' if err_dict["example"] else ""

                card_html = (
                    f'<div class="err-card">'
                    f'<div class="err-title">❌ {err_dict["title"]}</div>'
                    f'<div class="err-section-title">📌 WHAT HAPPENED?</div><div class="err-text">{err_dict["what"]}</div>'
                    f'{sug_html}'
                    f'<div class="err-section-title">❓ WHY DID IT HAPPEN?</div><div class="err-text">{err_dict["why"]}</div>'
                    f'<div class="err-section-title">🛠️ HOW TO FIX IT?</div><div class="err-text">{err_dict["fix"]}</div>'
                    f'{ex_html}'
                    f'<div class="err-section-title">🎓 COMPILER CONCEPT</div><div class="err-concept">{err_dict["concept"]}</div>'
                    f'</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)

                # Error Learning Connections Buttons
                err_btn_col1, err_btn_col2 = st.columns(2)
                with err_btn_col1:
                    target_les = get_lesson_id_for_error(res["error_obj"])
                    if st.button("📖 Learn From This Error", use_container_width=True):
                        st.session_state.target_lesson_id = target_les
                        st.session_state.nav_mode = "📚 Learning Mode"
                        st.rerun()
                with err_btn_col2:
                    target_prac = get_practice_category_for_error(res["error_obj"])
                    if st.button(f"🧩 Practice {target_prac} Errors", use_container_width=True):
                        st.session_state.target_practice_category = target_prac
                        st.session_state.nav_mode = "🧩 Practice Arena"
                        st.rerun()

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

        # --- 2. Interactive Tokens Visualizer & Category Filter ---
        with tabs[1]:
            if res["tokens"]:
                tok_cat = st.selectbox("Filter Tokens by Category", ["All Tokens", "Keywords", "Identifiers", "Literals", "Operators", "Punctuation"])

                filtered_toks = res["tokens"]
                if tok_cat == "Keywords":
                    filtered_toks = [t for t in res["tokens"] if t.type in ("INT", "FLOAT", "STRING", "BOOL", "IF", "ELSE", "WHILE", "PRINT", "TRUE", "FALSE", "AND", "OR", "NOT")]
                elif tok_cat == "Identifiers":
                    filtered_toks = [t for t in res["tokens"] if t.type == "IDENT"]
                elif tok_cat == "Literals":
                    filtered_toks = [t for t in res["tokens"] if t.type in ("NUMBER_LIT", "FLOAT_LIT", "STRING_LIT")]
                elif tok_cat == "Operators":
                    filtered_toks = [t for t in res["tokens"] if t.type in ("ASSIGN", "PLUS", "MINUS", "STAR", "SLASH", "PERCENT", "EQ", "NEQ", "LT", "GT", "LTE", "GTE")]
                elif tok_cat == "Punctuation":
                    filtered_toks = [t for t in res["tokens"] if t.type in ("LPAREN", "RPAREN", "LBRACE", "RBRACE", "SEMI", "COMMA")]

                rows = [
                    {
                        "#": i,
                        "Token Type": t.type,
                        "Value": str(t.value) if t.value is not None else "",
                        "Line": t.line,
                        "Column": getattr(t, "col", 1)
                    }
                    for i, t in enumerate(filtered_toks)
                ]
                st.dataframe(rows, use_container_width=True, height=280, hide_index=True)

                st.markdown("##### 💡 Interactive Token Detail Inspector")
                tok_idx = st.number_input("Select Token # to Inspect", min_value=0, max_value=max(0, len(filtered_toks)-1), value=0, step=1)
                if filtered_toks:
                    selected_tok = filtered_toks[tok_idx]
                    t_info = explain_token(selected_tok)

                    st.info(
                        f"**Token #{tok_idx}: `{t_info['type']}` (Value: `{t_info['value']}`)**\n\n"
                        f"- **Position**: Line {t_info['line']}, Column {t_info['col']}\n"
                        f"- **What is it?**: {t_info['what']}\n"
                        f"- **Why classified this way?**: {t_info['why']}\n"
                        f"- **Where is it used?**: {t_info['where']}"
                    )

                    # Source Location Pointer for Token
                    t_src_lines = st.session_state.code.split("\n")
                    if 1 <= selected_tok.line <= len(t_src_lines):
                        tok_src_line = t_src_lines[selected_tok.line - 1]
                        tok_caret = " " * max(0, getattr(selected_tok, "col", 1) - 1) + "^"
                        st.markdown(
                            f"**Source Context (Line {selected_tok.line}, Col {getattr(selected_tok, 'col', 1)}):**\n"
                            f"```text\n{tok_src_line}\n{tok_caret}\n```"
                        )
            else:
                st.info("No tokens available yet. Enter code and compile to view tokens.")

        # --- 3. AST Visualizer & Interactive Node Inspector ---
        with tabs[2]:
            if res["ast_text"] and res["ast_obj"]:
                st.markdown("**Abstract Syntax Tree Representation**")
                st.code(res["ast_text"], language="text")

                st.markdown("##### 💡 Interactive AST Node Inspector")
                all_ast_list = get_all_ast_nodes(res["ast_obj"])
                if all_ast_list:
                    node_options = [f"{i}: {_label(n)}" for i, n in enumerate(all_ast_list)]
                    sel_ast_str = st.selectbox("Select AST Node to Inspect", node_options)
                    sel_ast_idx = int(sel_ast_str.split(":")[0])
                    selected_node = all_ast_list[sel_ast_idx]
                    ast_meta = explain_ast_node(selected_node)

                    st.info(
                        f"**AST Node: `{ast_meta['type']}`**\n\n"
                        f"- **Label**: `{ast_meta['label']}`\n"
                        f"- **Source Line**: `{ast_meta['line']}`\n"
                        f"- **Educational Meaning**: {ast_meta['meaning']}\n"
                        f"- **Source Snippet**: `{ast_meta['source']}`"
                    )
            else:
                st.info("No AST available yet. The parser generates an AST after syntax analysis succeeds.")

        # --- 4. Scoped Symbol Table & Lookup Simulator ---
        with tabs[3]:
            if res["scope_tree_text"] and res["scope_obj"]:
                st.markdown("**Scoped Symbol Table Hierarchy**")
                st.code(res["scope_tree_text"], language="text")

                # Shadowing Alert
                shadowed_list = find_shadowed_variables(res["scope_obj"])
                if shadowed_list:
                    st.warning("⚠️ **Variable Shadowing Detected:**")
                    for sh in shadowed_list:
                        st.write(
                            f"- Variable **`{sh['var_name']}`** in `{sh['inner_scope']}` shadows variable **`{sh['var_name']}`** declared in outer `{sh['outer_scope']}`."
                        )

                # Interactive Symbol Lookup Simulator
                st.markdown("##### 🔍 Interactive Symbol Lookup Simulator")
                all_vars_available = res["scope_obj"].all_declared_vars()
                if all_vars_available:
                    target_var = st.selectbox("Select Variable to Simulate Scope Resolution Lookup", all_vars_available)
                    _, trace_steps = res["scope_obj"].resolve_with_trace(target_var)
                    st.markdown(f"**Lookup Path for Variable `{target_var}`:**")
                    for s in trace_steps:
                        symbol_icon = "✅" if s["found"] else "🔍"
                        st.markdown(f"{symbol_icon} {s['msg']}")
                else:
                    st.caption("No declared variables found in symbol table.")
            else:
                st.info("Symbol table populates after semantic analysis passes.")

        # --- 5. TAC Code Visualizer & Source Mapper ---
        with tabs[4]:
            if res["tac"]:
                st.markdown("**Generated Three-Address Code (TAC)**")
                tac_rows = [
                    {"#": i, "TAC Instruction": str(line), "Source Line": getattr(line, "line", "-"), "Natural Language Explanation": exp}
                    for i, (line, exp) in enumerate(zip(res["tac"], res["tac_explanations"]))
                ]
                st.dataframe(tac_rows, use_container_width=True, height=360, hide_index=True)

                st.markdown("##### 💡 Interactive TAC Instruction Inspector")
                tac_sel_idx = st.number_input("Select TAC Instruction #", min_value=0, max_value=len(res["tac"])-1, value=0, step=1)
                selected_tac_instr = res["tac"][tac_sel_idx]
                selected_tac_exp = res["tac_explanations"][tac_sel_idx]
                tac_src_line = getattr(selected_tac_instr, "line", None)

                st.info(
                    f"**TAC #{tac_sel_idx}: `{str(selected_tac_instr).strip()}`**\n\n"
                    f"- **Source Line**: `{f'Line {tac_src_line}' if tac_src_line else 'Compiler Generated'}`\n"
                    f"- **Instruction Action**: {selected_tac_exp}\n"
                    f"- **Execution Model**: Processed by TAC VM using Program Counter and local scope frames."
                )
            else:
                st.info("No TAC generated yet. Three-Address Code is generated after semantic analysis succeeds.")

        # --- 6. Step-by-Step TAC VM Execution Debugger ---
        with tabs[5]:
            if res["trace"]:
                st.markdown("#### ⏯️ Interactive Step-by-Step Execution Controls")

                if len(res["trace"]) >= 500:
                    st.caption("ℹ️ Execution trace display truncated at 500 steps.")

                ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4, ctrl_col5 = st.columns(5)
                max_steps = len(res["trace"])

                with ctrl_col1:
                    if st.button("⏮ Start", use_container_width=True):
                        st.session_state.vm_step_slider = 1
                with ctrl_col2:
                    if st.button("◀ Previous", use_container_width=True):
                        st.session_state.vm_step_slider = max(1, st.session_state.get("vm_step_slider", 1) - 1)
                with ctrl_col3:
                    if st.button("Next ▶", use_container_width=True):
                        st.session_state.vm_step_slider = min(max_steps, st.session_state.get("vm_step_slider", 1) + 1)
                with ctrl_col4:
                    if st.button("▶ Run to End", use_container_width=True):
                        st.session_state.vm_step_slider = max_steps
                with ctrl_col5:
                    if st.button("🔄 Reset VM", use_container_width=True):
                        st.session_state.vm_step_slider = 1

                step_idx = st.slider("Execution Step Pointer", min_value=1, max_value=max_steps, value=st.session_state.get("vm_step_slider", 1), step=1, key="vm_step_slider")
                st.session_state.vm_step_idx = step_idx

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
                st.info("No execution trace available yet. The TAC Virtual Machine populates the trace during execution.")

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

# ===========================================================================
# MODE 2: STEP-BY-STEP COMPILER PIPELINE WALKTHROUGH
# ===========================================================================
elif mode == "🎓 Learn Compiler Pipeline":
    st.markdown("### 🎓 Step-by-Step Compiler Pipeline Experience")
    st.caption("Walk through every transformation stage executed by the EduLang compiler on your current program.")

    if "pipe_step" not in st.session_state:
        st.session_state.pipe_step = 0

    stages_labels = [
        "1. Source Code",
        "2. Lexical Analysis",
        "3. Token Stream",
        "4. Syntax Analysis",
        "5. Abstract Syntax Tree",
        "6. Semantic Analysis",
        "7. Symbol Table & Scopes",
        "8. TAC Code Generation",
        "9. Virtual Machine Execution",
        "10. Console Output"
    ]

    p_nav1, p_nav2, p_nav3 = st.columns([1, 3, 1])
    with p_nav1:
        if st.button("⏮ Previous Stage", use_container_width=True):
            st.session_state.pipe_step = max(0, st.session_state.pipe_step - 1)
    with p_nav3:
        if st.button("Next Stage ⏭", use_container_width=True):
            st.session_state.pipe_step = min(len(stages_labels) - 1, st.session_state.pipe_step + 1)

    curr_p_idx = st.session_state.pipe_step
    st.markdown(f"#### Active Stage: `{stages_labels[curr_p_idx]}`")
    st.progress((curr_p_idx + 1) / len(stages_labels))

    full_res = compile_pipeline(st.session_state.code, max_stage=5)

    if curr_p_idx == 0:
        st.info("**What happens here?** The programmer enters high-level EduLang source code text.")
        st.code(st.session_state.code, language="python")
    elif curr_p_idx == 1:
        st.info("**What happens here?** The Lexer scans characters sequentially, skipping comments and whitespace.")
        st.markdown(f"**Total Tokens Scanned:** `{len(full_res['tokens'])}` | **Lexical Errors:** `{1 if full_res['error_category'] == '🟡 LEXICAL ERROR' else 0}`")
        if full_res["tokens"]:
            st.write(full_res["tokens"][:10])
    elif curr_p_idx == 2:
        st.info("**What happens here?** Lexemes are wrapped into typed `Token(Type, Value, Line, Column)` objects.")
        if full_res["tokens"]:
            st.dataframe([{"#": i, "Type": t.type, "Value": str(t.value), "Line": t.line, "Col": getattr(t, 'col', 1)} for i, t in enumerate(full_res["tokens"])], use_container_width=True)
    elif curr_p_idx == 3:
        st.info("**What happens here?** The Parser matches tokens against context-free grammar production rules.")
        if full_res["pipeline_status"]["Parser"] == "✓":
            st.success("Grammar rules matched successfully!")
        else:
            st.error(f"Syntax Error: {full_res['console'][0][1] if full_res['console'] else 'Failed'}")
    elif curr_p_idx == 4:
        st.info("**What happens here?** The AST is constructed, capturing structural relationships between expressions and control flow.")
        if full_res["ast_text"]:
            st.code(full_res["ast_text"], language="text")
    elif curr_p_idx == 5:
        st.info("**What happens here?** The Semantic Analyzer verifies variable declarations, scopes, type compatibility, and boolean conditions.")
        if full_res["pipeline_status"]["Semantic"] == "✓":
            st.success("Semantic checks passed cleanly! All types and declarations are valid.")
        else:
            st.error(f"Semantic Error: {full_res['console'][0][1] if full_res['console'] else 'Failed'}")
    elif curr_p_idx == 6:
        st.info("**What happens here?** Symbol Table scope objects track variable types across global and nested block scopes.")
        if full_res["scope_tree_text"]:
            st.code(full_res["scope_tree_text"], language="text")
    elif curr_p_idx == 7:
        st.info("**What happens here?** High-level statements are converted into linear Three-Address Code (TAC) instructions.")
        if full_res["tac"]:
            st.dataframe([{"#": i, "Instruction": str(t), "Explanation": e} for i, (t, e) in enumerate(zip(full_res["tac"], full_res["tac_explanations"]))], use_container_width=True)
    elif curr_p_idx == 8:
        st.info("**What happens here?** The TAC Virtual Machine steps through instructions using PC and memory frames.")
        if full_res["trace"]:
            st.write(f"Total VM Execution Steps: **{len(full_res['trace'])}**")
            st.dataframe([{"Step": t["step"], "Instruction": t["instruction"], "Variables": str(t["vars"])} for t in full_res["trace"][:15]], use_container_width=True)
    elif curr_p_idx == 9:
        st.info("**What happens here?** Output buffer printed to standard output console.")
        if full_res["console"]:
            st.code("\n".join(line for _, line in full_res["console"]), language="text")

# ===========================================================================
# MODE 3: LEARNING MODE (Structured Lessons)
# ===========================================================================
elif mode == "📚 Learning Mode":
    st.markdown("### 📚 Compiler Design Curriculum & Structured Lessons")
    st.caption("14 Interactive Lessons organized into Beginner, Intermediate, and Advanced compiler concepts.")

    # Target Lesson Jump if navigated from Error
    if st.session_state.target_lesson_id:
        match_l = next((l for l in LESSONS if l["id"] == st.session_state.target_lesson_id), None)
        if match_l:
            st.success(f"Jumped to relevant lesson: **{match_l['title']}**")
        st.session_state.target_lesson_id = None

    if "les_idx" not in st.session_state:
        st.session_state.les_idx = 0

    les_col1, les_col2 = st.columns([1, 2.5])

    with les_col1:
        selected_level = st.selectbox("Select Difficulty Level", ["All Levels", "Level 1 — Beginner", "Level 2 — Intermediate", "Level 3 — Advanced"])
        filtered_lessons = LESSONS if selected_level == "All Levels" else [l for l in LESSONS if l.get("level") == selected_level]

        lesson_titles = [les["title"] for les in filtered_lessons]
        curr_title = LESSONS[st.session_state.les_idx]["title"] if 0 <= st.session_state.les_idx < len(LESSONS) else lesson_titles[0]
        curr_title = curr_title if curr_title in lesson_titles else lesson_titles[0]

        selected_lesson_title = st.radio("Select Lesson", lesson_titles, index=lesson_titles.index(curr_title), label_visibility="collapsed")
        st.session_state.les_idx = next(i for i, l in enumerate(LESSONS) if l["title"] == selected_lesson_title)
        lesson = LESSONS[st.session_state.les_idx]

        st.caption(f"Lesson **{st.session_state.les_idx + 1}** of **{len(LESSONS)}**")
        st.progress((st.session_state.les_idx + 1) / len(LESSONS))

        nav_l_col1, nav_l_col2 = st.columns(2)
        with nav_l_col1:
            if st.button("⏮ Previous", key="prev_les_btn", use_container_width=True):
                st.session_state.les_idx = max(0, st.session_state.les_idx - 1)
                st.rerun()
        with nav_l_col2:
            if st.button("Next ⏭", key="next_les_btn", use_container_width=True):
                st.session_state.les_idx = min(len(LESSONS) - 1, st.session_state.les_idx + 1)
                st.rerun()

    with les_col2:
        st.markdown(f"### {lesson['title']}")
        st.markdown(f"**Level:** `{lesson.get('level', 'Level 1')}` | **Category:** `{lesson['category']}`")
        st.markdown("---")

        st.markdown(f"#### 📌 Concept: {lesson.get('concept', '')}")

        st.markdown(f"#### 💡 What is it?")
        st.write(lesson["what"])

        st.markdown(f"#### ❓ Why does it matter?")
        st.write(lesson["why"])

        st.markdown(f"#### 🛠️ How does it work?")
        st.write(lesson["how"])

        st.markdown(f"#### ⚙️ Compiler Action")
        st.info(lesson.get("compiler_action", "Executes phase logic across pipeline."))

        st.markdown(f"#### 💻 Example EduLang Code")
        st.code(lesson["code"], language="python")

        if st.button("🚀 Load Code into Compiler IDE"):
            st.session_state.code = lesson["code"]
            st.session_state.sample_choice = "(custom code)"
            st.session_state.nav_mode = "💻 Compiler IDE"
            st.success("Lesson code loaded into IDE!")
            st.rerun()

        # Mini Exercise Section
        if "exercise" in lesson:
            st.markdown("---")
            st.markdown("#### 📝 Mini Exercise")
            ex = lesson["exercise"]
            st.write(ex["question"])

            user_ans = st.radio(f"ex_{lesson['id']}", ex["options"], key=f"ex_radio_{lesson['id']}")
            if st.button("Submit Exercise Answer", key=f"ex_btn_{lesson['id']}"):
                user_idx = ex["options"].index(user_ans)
                if user_idx == ex["answer"]:
                    st.success(f"🎉 Correct! {ex['explanation']}")
                    st.session_state.progress_lessons.add(lesson["id"])
                else:
                    st.error(f"❌ Incorrect. {ex['explanation']}")

# ===========================================================================
# MODE 4: PRACTICE & DEBUGGING ARENA (Explicit Run Only)
# ===========================================================================
elif mode == "🧩 Practice Arena":
    st.markdown("### 🧩 Practice & Debugging Arena")
    st.caption("Identify and fix intentional compiler diagnostics across Lexical, Syntax, Semantic, and Runtime categories.")

    # Target Category Filter Jump if navigated from Error
    default_cat_idx = 0
    if st.session_state.target_practice_category:
        cat_map = {"Lexical Analysis": 1, "Syntax Analysis": 2, "Semantic Analysis": 3, "Runtime / Execution": 4}
        default_cat_idx = cat_map.get(st.session_state.target_practice_category, 0)
        st.session_state.target_practice_category = None

    diff_filter = st.selectbox(
        "Filter Challenges by Category / Difficulty",
        ["All Challenges", "Lexical Analysis", "Syntax Analysis", "Semantic Analysis", "Runtime / Execution"],
        index=default_cat_idx
    )

    filtered_prac = PRACTICE_CHALLENGES if diff_filter == "All Challenges" else [c for c in PRACTICE_CHALLENGES if c["category"] == diff_filter]

    prac_names = [p["title"] for p in filtered_prac]
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
            run_prac = st.button("🚀 Run Compiler Analysis", type="primary", use_container_width=True)
        with c_btn2:
            if st.button("🔄 Reset Challenge Code", use_container_width=True):
                st.session_state[f"prac_code_{challenge['id']}"] = challenge["buggy_code"]
                st.rerun()

        # Multi-Tier Hint System
        with st.expander("💡 Progressive Hint System"):
            hints = challenge.get("hints", [challenge.get("hint", "")])
            for h_idx, h_text in enumerate(hints, start=1):
                if st.checkbox(f"Show Hint {h_idx}", key=f"chk_hint_{challenge['id']}_{h_idx}"):
                    st.info(h_text)

    with p_right:
        st.markdown("**Diagnostic Feedback & Analysis**")
        if run_prac:
            prac_res = compile_pipeline(prac_code, max_stage=5)
            if prac_res["error_category"] == "🟢 SUCCESS":
                st.success("🎉 Challenge Solved! Your code compiled and executed cleanly without errors.")
                st.session_state.progress_challenges.add(challenge["id"])
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
        else:
            st.info("Click 🚀 Run Compiler Analysis above to evaluate your challenge solution.")

# ===========================================================================
# MODE 5: COMPILER QUIZ MODE
# ===========================================================================
elif mode == "🎯 Compiler Quiz":
    st.markdown("### 🎯 Compiler Design Knowledge Quiz")
    st.caption("Test your understanding of Compiler Design concepts, phases, and diagnostic handling.")

    if "quiz_idx" not in st.session_state:
        st.session_state.quiz_idx = 0
    if "quiz_score" not in st.session_state:
        st.session_state.quiz_score = 0
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False

    total_q = len(QUIZ_QUESTIONS)

    if st.session_state.quiz_idx < total_q:
        q = QUIZ_QUESTIONS[st.session_state.quiz_idx]
        st.markdown(f"#### Question {st.session_state.quiz_idx + 1} of {total_q} (`Category: {q.get('category', 'General')}`)")
        st.markdown(f"**{q['question']}**")

        user_choice = st.radio(
            f"q_{q['id']}",
            q["options"],
            key=f"radio_{q['id']}",
            label_visibility="collapsed"
        )

        if not st.session_state.quiz_submitted:
            if st.button("Submit Answer", type="primary"):
                st.session_state.quiz_submitted = True
                chosen_idx = q["options"].index(user_choice)
                if chosen_idx == q["correct"]:
                    st.session_state.quiz_score += 1
                st.rerun()
        else:
            chosen_idx = q["options"].index(user_choice)
            if chosen_idx == q["correct"]:
                st.success(f"✅ Correct! {q['explanation']}")
            else:
                st.error(f"❌ Incorrect. Correct answer: '{q['options'][q['correct']]}'.\n\n{q['explanation']}")

            if st.button("Next Question ▶", type="primary"):
                st.session_state.quiz_idx += 1
                st.session_state.quiz_submitted = False
                st.rerun()
    else:
        # Final Quiz Breakdown
        score = st.session_state.quiz_score
        pct = (score / total_q) * 100
        rating = "Outstanding! Comprehensive compiler design mastery." if pct >= 80 else "Good effort! Solid foundation." if pct >= 50 else "Needs Improvement. Review Learning Mode lessons."

        st.markdown("### 🏆 Quiz Completed!")
        st.metric("Final Score", f"{score} / {total_q}", delta=f"{pct:.0f}%")
        st.info(f"**Performance Rating:** {rating}")

        if st.button("🔄 Retry Quiz", type="primary"):
            st.session_state.quiz_idx = 0
            st.session_state.quiz_score = 0
            st.session_state.quiz_submitted = False
            st.rerun()

# ===========================================================================
# MODE 6: LANGUAGE REFERENCE & GLOSSARY
# ===========================================================================
elif mode == "📖 Language Reference":
    st.markdown("### 📖 EduLang Language Reference & Compiler Glossary")
    st.caption("Official language specification, data types, operators, grammar BNF, diagnostic error codes, and compiler terminology.")

    ref_tabs = st.tabs([
        "Data Types & Variables",
        "Operators & Logic",
        "Control Flow Statements",
        "Diagnostic Error Codes",
        "Compiler Glossary"
    ])

    with ref_tabs[0]:
        st.markdown("#### 📌 Data Types")
        st.markdown("""
- **`int`**: Whole integer numbers (e.g., `42`, `-10`, `0`).
- **`float`**: Floating-point decimal numbers (e.g., `3.14`, `0.001`, `-5.5`).
- **`string`**: Double-quoted text strings (e.g., `"Hello EduLang"`).
- **`bool`**: Boolean truth values (`true`, `false`).
""")
        st.code("""
int count = 10;
float pi = 3.14159;
string name = "EduLang";
bool isActive = true;
""", language="python")

    with ref_tabs[1]:
        st.markdown("#### 📌 Operators & Precedence")
        st.markdown("""
- **Arithmetic**: `+`, `-`, `*`, `/`, `%`
- **Comparison**: `==`, `!=`, `<`, `>`, `<=`, `>=`
- **Boolean Logic**: `and`, `or`, `not`
- **Assignment**: `=`
""")
        st.code("""
int result = (10 + 20) * 2;
bool isValid = (result > 50) and not false;
""", language="python")

    with ref_tabs[2]:
        st.markdown("#### 📌 Control Flow")
        st.markdown("""
- **Conditional Branching**: `if (condition) { ... } else { ... }`
- **Loops**: `while (condition) { ... }`
- **Console Output**: `print(expression);`
- **Lexical Blocks**: `{ ... }`
""")
        st.code("""
int x = 0;
while (x < 3) {
    print(x);
    x = x + 1;
}
""", language="python")

    with ref_tabs[3]:
        st.markdown("#### 📌 Compiler Diagnostic Error Codes")
        st.markdown("""
| Code | Phase | Category | Description |
| :--- | :--- | :--- | :--- |
| **`LEX001`** | Lexical | Invalid Character | Found a character outside EduLang's alphabet |
| **`LEX002`** | Lexical | Unterminated String | String literal missing closing quote `"` |
| **`SYN001`** | Syntax | Missing Semicolon | Statement missing closing `;` |
| **`SYN002`** | Syntax | Unexpected Token | Token sequence violates production rules |
| **`SYN003`** | Syntax | Unmatched Delimiter | Missing `)` or `}` |
| **`SEM001`** | Semantic | Undeclared Variable | Variable referenced before declaration |
| **`SEM002`** | Semantic | Redeclared Variable | Variable re-declared in same scope |
| **`SEM003`** | Semantic | Type Mismatch | Assigned value type does not match variable |
| **`SEM004`** | Semantic | Invalid Operator | Incompatible types for binary/unary op |
| **`SEM005`** | Semantic | Non-Boolean Condition | `if`/`while` condition is not a `bool` |
| **`RUN001`** | Runtime | Division by Zero | Integer/Float division by zero at runtime |
| **`RUN002`** | Runtime | Modulo by Zero | Modulo operation by zero at runtime |
| **`RUN003`** | Runtime | Step Limit Exceeded | VM step count exceeded safeguard limit |
""")

    with ref_tabs[4]:
        st.markdown("#### 📌 Compiler Glossary")
        terms = [
            ("Lexer (Scanner)", "Converts a raw stream of source text characters into a stream of structured tokens."),
            ("Token", "An abstract object storing token type (e.g. KEYWORD, IDENTIFIER), lexeme value, line, and column."),
            ("Lexeme", "The exact raw character sequence in source code that matches a token pattern."),
            ("Parser (Syntax Analyzer)", "Checks whether tokens satisfy formal grammar production rules and constructs an AST."),
            ("Abstract Syntax Tree (AST)", "A hierarchical tree representing the logical structural semantics of a program."),
            ("Semantic Analyzer", "Verifies program meaning, type compatibility, variable declarations, and scope rules."),
            ("Scope & Symbol Table", "A data structure tracking declared variables, types, and lexical scope hierarchy levels."),
            ("Variable Shadowing", "When an inner block variable hides an outer variable with the same name."),
            ("Three-Address Code (TAC)", "An intermediate representation where instructions have at most 3 operands and 1 operator."),
            ("Virtual Machine (VM)", "A software execution engine that steps through TAC instructions using a Program Counter (PC).")
        ]
        for term, desc in terms:
            with st.expander(f"📌 {term}"):
                st.write(desc)

st.caption(
    "EduLang Learning Platform · Lexer → Parser (AST) → Semantic Analyzer (scopes) "
    "→ TAC Generator → TAC Virtual Machine → Error Explainer. Deterministic Python Compiler."
)
