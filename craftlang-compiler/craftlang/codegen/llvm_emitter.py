"""Target Code Generation: Standard LLVM IR Emitter."""

from typing import List, Dict, Any, Optional
from ..ir.instructions import TACInstruction, OpCode


class LLVMEmitter:
    """Emits clean, standard LLVM Intermediate Representation (LLVM IR)."""

    def __init__(self):
        self.string_literals: Dict[str, str] = {}
        self.str_counter: int = 0

    def _escape_llvm_string(self, text: str) -> str:
        # LLVM IR string escape: \0A for newline, \00 for null byte
        res = []
        for ch in text:
            if ch == '\n':
                res.append('\\0A')
            elif ch == '\t':
                res.append('\\09')
            elif ch == '"':
                res.append('\\22')
            elif ch == '\\':
                res.append('\\5C')
            elif ord(ch) < 32 or ord(ch) > 126:
                res.append(f'\\{ord(ch):02X}')
            else:
                res.append(ch)
        return "".join(res)

    def emit(self, instructions: List[TACInstruction]) -> str:
        """Translates TAC instructions into LLVM IR."""
        self.string_literals = {}
        self.str_counter = 0

        # Pass 1: Collect string literals for global constants
        for inst in instructions:
            for arg in (inst.arg1, inst.arg2):
                if isinstance(arg, str) and (arg.startswith('"') or '\n' in arg or ' ' in arg):
                    clean = arg.strip('"')
                    if clean not in self.string_literals:
                        var_name = f"@.str.{self.str_counter}"
                        self.string_literals[clean] = var_name
                        self.str_counter += 1

        body_lines: List[str] = []
        in_function = False
        current_fn_name = ""
        param_stack: List[str] = []
        allocated_vars = set()

        for inst in instructions:
            if inst.op == OpCode.FUNC_START:
                fn_name = str(inst.arg1)
                in_function = True
                current_fn_name = fn_name
                ret_type = "i32" if fn_name == "main" else "i32"
                body_lines.append("")
                body_lines.append(f"; Function: {fn_name}")
                body_lines.append(f"define {ret_type} @{fn_name}() {{")
                body_lines.append("entry:")
                allocated_vars.clear()
                continue

            if inst.op == OpCode.FUNC_END:
                if not body_lines[-1].strip().startswith("ret ") and not body_lines[-1].strip().startswith("br "):
                    ret_val = "0" if current_fn_name == "main" else "0"
                    body_lines.append(f"  ret i32 {ret_val}")
                body_lines.append("}")
                in_function = False
                continue

            if not in_function:
                # Wrap top-level instructions inside main
                in_function = True
                current_fn_name = "main"
                body_lines.append("")
                body_lines.append("define i32 @main() {")
                body_lines.append("entry:")

            # Instructions translation
            if inst.op == OpCode.LABEL:
                lbl = str(inst.arg1)
                # LLVM label
                body_lines.append(f"{lbl}:")

            elif inst.op == OpCode.ASSIGN:
                res = inst.result
                val = self._format_operand(inst.arg1)
                body_lines.append(f"  %{res} = add i32 0, {val}")

            elif inst.op in (OpCode.ADD, OpCode.SUB, OpCode.MUL, OpCode.DIV, OpCode.MOD):
                llvm_op_map = {
                    OpCode.ADD: "add nsw i32",
                    OpCode.SUB: "sub nsw i32",
                    OpCode.MUL: "mul nsw i32",
                    OpCode.DIV: "sdiv i32",
                    OpCode.MOD: "srem i32",
                }
                op_str = llvm_op_map[inst.op]
                a1 = self._format_operand(inst.arg1)
                a2 = self._format_operand(inst.arg2)
                body_lines.append(f"  %{inst.result} = {op_str} {a1}, {a2}")

            elif inst.op in (OpCode.EQ, OpCode.NE, OpCode.LT, OpCode.LE, OpCode.GT, OpCode.GE):
                llvm_cmp_map = {
                    OpCode.EQ: "icmp eq i32",
                    OpCode.NE: "icmp ne i32",
                    OpCode.LT: "icmp slt i32",
                    OpCode.LE: "icmp sle i32",
                    OpCode.GT: "icmp sgt i32",
                    OpCode.GE: "icmp sge i32",
                }
                cmp_str = llvm_cmp_map[inst.op]
                a1 = self._format_operand(inst.arg1)
                a2 = self._format_operand(inst.arg2)
                body_lines.append(f"  %{inst.result} = {cmp_str} {a1}, {a2}")

            elif inst.op == OpCode.AND:
                a1 = self._format_operand(inst.arg1)
                a2 = self._format_operand(inst.arg2)
                body_lines.append(f"  %{inst.result} = and i1 {a1}, {a2}")

            elif inst.op == OpCode.OR:
                a1 = self._format_operand(inst.arg1)
                a2 = self._format_operand(inst.arg2)
                body_lines.append(f"  %{inst.result} = or i1 {a1}, {a2}")

            elif inst.op == OpCode.NEG:
                a1 = self._format_operand(inst.arg1)
                body_lines.append(f"  %{inst.result} = sub nsw i32 0, {a1}")

            elif inst.op == OpCode.NOT:
                a1 = self._format_operand(inst.arg1)
                body_lines.append(f"  %{inst.result} = xor i1 {a1}, true")

            elif inst.op == OpCode.JUMP:
                body_lines.append(f"  br label %{inst.arg1}")

            elif inst.op == OpCode.JUMP_IF_TRUE:
                cond = self._format_operand(inst.arg1)
                # Next fallback block
                body_lines.append(f"  br i1 {cond}, label %{inst.arg2}, label %fallback")

            elif inst.op == OpCode.JUMP_IF_FALSE:
                cond = self._format_operand(inst.arg1)
                body_lines.append(f"  br i1 {cond}, label %next, label %{inst.arg2}")

            elif inst.op == OpCode.PARAM:
                param_stack.append(self._format_operand(inst.arg1))

            elif inst.op == OpCode.CALL:
                callee = str(inst.arg1)
                args_formatted = ", ".join(f"i32 {p}" for p in param_stack)
                param_stack.clear()
                if inst.result:
                    body_lines.append(f"  %{inst.result} = call i32 @{callee}({args_formatted})")
                else:
                    body_lines.append(f"  call i32 @{callee}({args_formatted})")

            elif inst.op == OpCode.RETURN:
                if inst.arg1 is not None:
                    val = self._format_operand(inst.arg1)
                    body_lines.append(f"  ret i32 {val}")
                else:
                    body_lines.append("  ret void" if current_fn_name != "main" else "  ret i32 0")

            elif inst.op == OpCode.PRINT:
                val = str(inst.arg1).strip('"')
                if val in self.string_literals:
                    var_name = self.string_literals[val]
                    length = len(val.encode('utf-8')) + 1
                    body_lines.append(f"  call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([{length} x i8], [{length} x i8]* {var_name}, i32 0, i32 0))")
                else:
                    arg_val = self._format_operand(inst.arg1)
                    body_lines.append(f"  call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.fmt_int, i32 0, i32 0), i32 {arg_val})")

        if in_function and (not body_lines[-1].strip().startswith("ret ") and not body_lines[-1].strip().startswith("br ")):
            body_lines.append("  ret i32 0")
            body_lines.append("}")

        # Assemble Full LLVM Module
        header = [
            "; ModuleID = 'craftlang_module'",
            'source_filename = "craftlang_source.cl"',
            'target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"',
            'target triple = "x86_64-pc-linux-gnu"',
            "",
            "; External format strings & libc declarations",
            '@.fmt_int = private unnamed_addr constant [4 x i8] c"%d\\0A\\00", align 1',
        ]

        for s_val, s_var in self.string_literals.items():
            escaped = self._escape_llvm_string(s_val + "\n")
            length = len(s_val.encode('utf-8')) + 2
            header.append(f'{s_var} = private unnamed_addr constant [{length} x i8] c"{escaped}\\00", align 1')

        header.append("")
        header.append("declare i32 @printf(i8*, ...)")

        return "\n".join(header + body_lines)

    def _format_operand(self, arg: Any) -> str:
        if isinstance(arg, bool):
            return "true" if arg else "false"
        if isinstance(arg, int):
            return str(arg)
        if isinstance(arg, float):
            return str(arg)
        if isinstance(arg, str):
            if arg.startswith('"'):
                return arg
            return f"%{arg}"
        return str(arg)
