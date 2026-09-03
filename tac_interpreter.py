"""
TAC Virtual Machine / Interpreter for EduLang.

Executes generated Three-Address Code (TAC) instructions directly.
Collects stdout output, variable state snapshots, and step-by-step execution trace.
Raises structured RuntimeErrorObject for division by zero, modulo by zero, infinite loop, or runtime errors.
"""


class RuntimeErrorObject(Exception):
    """Structured runtime error object matching the compiler's diagnostic format."""
    def __init__(self, code, line, technical, context=None):
        self.phase = "Runtime"
        self.code = code
        self.line = line
        self.technical = technical
        self.context = context or {}
        super().__init__(technical)


class TACInterpreter:
    """
    Virtual Machine that executes TAC instruction streams.
    """
    def __init__(self, tac_lines, step_limit=200000, max_trace_steps=500):
        self.tac_lines = [str(line).strip() for line in tac_lines if str(line).strip()]
        self.step_limit = step_limit
        self.max_trace_steps = max_trace_steps
        self.env = {}
        self.output = []
        self.trace = []
        self.pc = 0
        self.steps = 0
        self.labels = {}
        self._build_label_table()

    def _build_label_table(self):
        for idx, line in enumerate(self.tac_lines):
            if line.endswith(":") and not ("=" in line or "GOTO" in line or "PRINT" in line):
                label_name = line[:-1].strip()
                self.labels[label_name] = idx

    def run(self):
        while self.pc < len(self.tac_lines):
            self.steps += 1
            if self.steps > self.step_limit:
                raise RuntimeErrorObject(
                    "RUN003", None,
                    "Program exceeded maximum execution steps (possible infinite loop)",
                    {"limit": self.step_limit}
                )

            line = self.tac_lines[self.pc]
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
        user_vars = {k: v for k, v in self.env.items() if not k.startswith("t")}
        return self.output, user_vars, self.trace

    def _exec_instruction(self, line, prev_pc_idx):
        step_desc = ""

        if line.startswith("PRINT "):
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
                raise RuntimeErrorObject("RUN004", None, f"Unknown label '{target}'", {"label": target})

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
                    raise RuntimeErrorObject("RUN004", None, f"Unknown label '{target}'", {"label": target})
            else:
                step_desc = f"Condition true -> Continue to next line"

        elif "=" in line:
            lhs, rhs = [p.strip() for p in line.split("=", 1)]
            val = self._eval_rhs(rhs)
            self.env[lhs] = val
            step_desc = f"{lhs} = {self._stringify(val)}"

        else:
            raise RuntimeErrorObject("RUN004", None, f"Unknown TAC instruction: '{line}'", {"instruction": line})

        if len(self.trace) < self.max_trace_steps:
            user_vars = {k: self._stringify(v) for k, v in self.env.items() if not k.startswith("t")}
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
                end = rhs.find('"', i + 1)
                if end == -1:
                    end = len(rhs) - 1
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
                raise RuntimeErrorObject("RUN004", None, f"Cannot negate non-numeric '{val_str}'", {"val": val_str})
            raise RuntimeErrorObject("RUN004", None, f"Unknown unary operator '{op}'", {"op": op})

        # Binary operations: e.g. "a + b", "x == y"
        if len(tokens) == 3:
            l_str, op, r_str = tokens
            left = self._eval_val(l_str)
            right = self._eval_val(r_str)
            return self._eval_binop(op, left, right)

        raise RuntimeErrorObject("RUN004", None, f"Malformed RHS expression '{rhs}'", {"expression": rhs})

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
                    "RUN001", None,
                    "Division by zero encountered during execution",
                    {"op": "/"}
                )
            if isinstance(l, float) or isinstance(r, float):
                return l / r
            q = l / r
            return int(q) if q >= 0 else -int(-q)
        if op == "%":
            if r == 0:
                raise RuntimeErrorObject(
                    "RUN002", None,
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

        raise RuntimeErrorObject("RUN004", None, f"Unknown binary operator '{op}'", {"op": op})

    def _eval_val(self, val_str):
        val_str = val_str.strip()
        if val_str == "true":
            return True
        if val_str == "false":
            return False
        if val_str == "<uninitialized>":
            return None
        if val_str.startswith('"') and val_str.endswith('"'):
            return val_str[1:-1]
        try:
            if "." in val_str:
                return float(val_str)
            return int(val_str)
        except ValueError:
            pass

        if val_str in self.env:
            return self.env[val_str]

        raise RuntimeErrorObject(
            "RUN004", None,
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
