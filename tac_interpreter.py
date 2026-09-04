"""
TAC Virtual Machine / Interpreter for EduLang.

Executes generated Three-Address Code (TAC) instructions directly.
Collects stdout output, variable state snapshots, and step-by-step execution trace.
Raises structured RuntimeErrorObject for division by zero, modulo by zero, infinite loop, or runtime errors.
"""


import re


def is_temporary(name: str) -> bool:
    """Returns True iff variable name matches compiler temporary register pattern (e.g. t0, t1, t12)."""
    return bool(re.fullmatch(r"t\d+", str(name)))


class RuntimeErrorObject(Exception):
    """Structured runtime error object matching the compiler's diagnostic format."""
    def __init__(self, code, line, technical, context=None):
        self.phase = "Runtime"
        self.code = code
        self.line = line
        self.technical = technical
        self.context = context or {}
        super().__init__(technical)


class RuntimeScope:
    """Represents a single runtime scope frame linked to parent scope."""
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def declare(self, name, val):
        self.vars[name] = val

    def assign(self, name, val):
        scope = self
        while scope:
            if name in scope.vars:
                scope.vars[name] = val
                return True
            scope = scope.parent
        self.vars[name] = val
        return False

    def get(self, name):
        scope = self
        while scope:
            if name in scope.vars:
                return scope.vars[name]
            scope = scope.parent
        raise KeyError(name)

    def all_vars(self):
        result = {}
        scopes = []
        s = self
        while s:
            scopes.append(s)
            s = s.parent
        for s in reversed(scopes):
            result.update(s.vars)
        return result


class TACInterpreter:
    """
    Virtual Machine that executes TAC instruction streams with scope frames.
    """
    def __init__(self, tac_lines, step_limit=200000, max_trace_steps=500):
        self.tac_instructions = list(tac_lines)
        self.tac_lines = [str(line).strip() for line in tac_lines if str(line).strip()]
        self.step_limit = step_limit
        self.max_trace_steps = max_trace_steps
        self.global_scope = RuntimeScope()
        self.current_scope = self.global_scope
        self.output = []
        self.trace = []
        self.pc = 0
        self.steps = 0
        self.labels = {}
        self.curr_line = None
        self._build_label_table()

    def _build_label_table(self):
        for idx, raw_instr in enumerate(self.tac_instructions):
            line = str(raw_instr).strip()
            if line.endswith(":") and not ("=" in line or "GOTO" in line or "PRINT" in line):
                label_name = line[:-1].strip()
                self.labels[label_name] = idx

    def run(self):
        while self.pc < len(self.tac_instructions):
            self.steps += 1
            if self.steps > self.step_limit:
                raise RuntimeErrorObject(
                    "RUN003", self.curr_line,
                    "Program exceeded maximum execution steps (possible infinite loop)",
                    {"limit": self.step_limit}
                )

            raw_instr = self.tac_instructions[self.pc]
            self.curr_line = getattr(raw_instr, "line", None)
            line = str(raw_instr).strip()
            prev_pc_idx = self.pc

            # Ignore raw label declarations
            if line.endswith(":") and line[:-1] in self.labels:
                self.pc += 1
                continue

            self._exec_instruction(line, prev_pc_idx)

            # Advance program counter if not modified by jump
            if self.pc == prev_pc_idx:
                self.pc += 1

        # Return stdout output lines, final non-temporary variables, and trace
        user_vars = {k: v for k, v in self.current_scope.all_vars().items() if not is_temporary(k)}
        return self.output, user_vars, self.trace

    def _exec_instruction(self, line, prev_pc_idx):
        step_desc = ""

        if line == "ENTER_SCOPE":
            self.current_scope = RuntimeScope(parent=self.current_scope)
            step_desc = "Enter block scope"

        elif line == "EXIT_SCOPE":
            if self.current_scope.parent:
                self.current_scope = self.current_scope.parent
            step_desc = "Exit block scope"

        elif line.startswith("DECL "):
            rest = line[5:].strip()
            if "=" in rest:
                lhs, rhs = [p.strip() for p in rest.split("=", 1)]
                val = self._eval_rhs(rhs)
                self.current_scope.declare(lhs, val)
                step_desc = f"DECL {lhs} = {self._stringify(val)}"
            else:
                self.current_scope.declare(rest, None)
                step_desc = f"DECL {rest}"

        elif line.startswith("PRINT "):
            arg = line[6:].strip()
            val = self._eval_val(arg)
            out_str = self._stringify(val)
            self.output.append(out_str)
            step_desc = f"PRINT {out_str}"

        elif line.startswith("GOTO "):
            target = line[5:].strip()
            if target in self.labels:
                self.pc = self.labels[target]
                step_desc = f"Jump to {target}"
            else:
                raise RuntimeErrorObject("RUN004", self.curr_line, f"Unknown label '{target}'", {"label": target})

        elif line.startswith("IF_FALSE "):
            # Format: IF_FALSE cond GOTO label
            parts = line.split()
            cond_val = self._eval_val(parts[1])
            target = parts[3]
            if not cond_val:
                if target in self.labels:
                    self.pc = self.labels[target]
                    step_desc = f"Condition false -> Jump to {target}"
                else:
                    raise RuntimeErrorObject("RUN004", self.curr_line, f"Unknown label '{target}'", {"label": target})
            else:
                step_desc = f"Condition true -> Continue to next line"

        elif "=" in line:
            lhs, rhs = [p.strip() for p in line.split("=", 1)]
            val = self._eval_rhs(rhs)
            self.current_scope.assign(lhs, val)
            step_desc = f"{lhs} = {self._stringify(val)}"

        else:
            raise RuntimeErrorObject("RUN004", self.curr_line, f"Unknown TAC instruction: '{line}'", {"instruction": line})

        if len(self.trace) < self.max_trace_steps:
            user_vars = {k: self._stringify(v) for k, v in self.current_scope.all_vars().items() if not is_temporary(k)}
            self.trace.append({
                "step": self.steps,
                "pc": prev_pc_idx,
                "instruction": line,
                "action": step_desc,
                "vars": user_vars
            })

    def _tokenize_rhs(self, rhs):
        rhs = rhs.strip()
        tokens = []
        i = 0
        while i < len(rhs):
            if rhs[i].isspace():
                i += 1
                continue
            if rhs[i] == '"':
                j = i + 1
                while j < len(rhs):
                    if rhs[j] == '\\':
                        j += 2
                        continue
                    if rhs[j] == '"':
                        break
                    j += 1
                end = j if j < len(rhs) else len(rhs) - 1
                tokens.append(rhs[i:end + 1])
                i = end + 1
            else:
                j = i
                while j < len(rhs) and not rhs[j].isspace() and rhs[j] != '"':
                    j += 1
                tokens.append(rhs[i:j])
                i = j
        return tokens

    def _eval_rhs(self, rhs):
        tokens = self._tokenize_rhs(rhs)

        # Simple literal or variable reference
        if len(tokens) == 1:
            return self._eval_val(tokens[0])

        # Unary operations: e.g. "not x", "- x"
        if len(tokens) == 2:
            op, val_str = tokens
            val = self._eval_val(val_str)
            if op == "not":
                return not bool(val)
            if op == "-":
                if isinstance(val, (int, float)):
                    return -val
                raise RuntimeErrorObject("RUN004", self.curr_line, f"Cannot negate non-numeric '{val_str}'", {"val": val_str})
            raise RuntimeErrorObject("RUN004", self.curr_line, f"Unknown unary operator '{op}'", {"op": op})

        # Binary operations: e.g. "a + b", "x == y"
        if len(tokens) == 3:
            l_str, op, r_str = tokens
            left = self._eval_val(l_str)
            right = self._eval_val(r_str)
            return self._eval_binop(op, left, right)

        raise RuntimeErrorObject("RUN004", self.curr_line, f"Malformed RHS expression '{rhs}'", {"expression": rhs})

    def _eval_binop(self, op, l, r):
        if op == "+":
            if isinstance(l, str) and isinstance(r, str):
                return l + r
            return l + r
        if op == "-":
            return l - r
        if op == "*":
            return l * r
        if op == "/":
            if r == 0:
                raise RuntimeErrorObject(
                    "RUN001", self.curr_line,
                    "Division by zero encountered during execution",
                    {"op": "/"}
                )
            return l / r
        if op == "%":
            if r == 0:
                raise RuntimeErrorObject(
                    "RUN002", self.curr_line,
                    "Modulo by zero encountered during execution",
                    {"op": "%"}
                )
            if isinstance(l, float) or isinstance(r, float):
                return l - r * (int(l / r) if l / r >= 0 else -int(-(l / r)))
            m = abs(l) % abs(r)
            return -m if l < 0 else m
        if op == "==":
            return l == r
        if op == "!=":
            return l != r
        if op == "<":
            return l < r
        if op == ">":
            return l > r
        if op == "<=":
            return l <= r
        if op == ">=":
            return l >= r
        if op == "and":
            return bool(l) and bool(r)
        if op == "or":
            return bool(l) or bool(r)

        raise RuntimeErrorObject("RUN004", self.curr_line, f"Unknown binary operator '{op}'", {"op": op})

    def _eval_val(self, val_str):
        val_str = val_str.strip()
        if val_str == "true":
            return True
        if val_str == "false":
            return False
        if val_str == "<uninitialized>":
            return None
        if val_str.startswith('"') and val_str.endswith('"'):
            inner = val_str[1:-1]
            return inner.replace('\\"', '"').replace('\\\\', '\\').replace('\\n', '\n').replace('\\t', '\t')
        try:
            if "." in val_str:
                return float(val_str)
            return int(val_str)
        except ValueError:
            pass

        try:
            return self.current_scope.get(val_str)
        except KeyError:
            pass

        raise RuntimeErrorObject(
            "RUN004", self.curr_line,
            f"Runtime error: variable '{val_str}' is undefined",
            {"var": val_str}
        )

    def _stringify(self, val):
        if val is True:
            return "true"
        if val is False:
            return "false"
        if val is None:
            return "null"
        return str(val)


def run_tac(tac_lines):
    vm = TACInterpreter(tac_lines)
    return vm.run()
