"""Target Code Generation: Educational x86-64 Assembly Emitter."""

from typing import List, Dict, Any
from ..ir.instructions import TACInstruction, OpCode


class AssemblyEmitter:
    """Emits clean, well-commented x86-64 assembly with register and stack frame management."""

    def __init__(self):
        self.string_literals: Dict[str, str] = {}
        self.str_counter: int = 0
        self.var_offsets: Dict[str, int] = {}
        self.current_offset: int = -8

    def _get_operand(self, arg: Any) -> str:
        """Returns the assembly representation of an operand (register, immediate, or stack slot)."""
        if isinstance(arg, int):
            return f"${arg}"
        if isinstance(arg, bool):
            return "$1" if arg else "$0"
        if isinstance(arg, str):
            if arg not in self.var_offsets:
                self.var_offsets[arg] = self.current_offset
                self.current_offset -= 8
            offset = self.var_offsets[arg]
            return f"{offset}(%rbp)"
        return "$0"

    def emit(self, instructions: List[TACInstruction]) -> str:
        """Translates TAC instructions into readable x86-64 assembly."""
        self.string_literals = {}
        self.str_counter = 0
        self.var_offsets = {}
        self.current_offset = -8

        # Collect strings
        for inst in instructions:
            for arg in (inst.arg1, inst.arg2):
                if isinstance(arg, str) and (arg.startswith('"') or '\n' in arg or ' ' in arg):
                    clean = arg.strip('"')
                    if clean not in self.string_literals:
                        lbl = f".LC{self.str_counter}"
                        self.string_literals[clean] = lbl
                        self.str_counter += 1

        text_lines: List[str] = []
        text_lines.append(".text")
        text_lines.append(".globl main")

        in_function = False
        current_fn_name = ""
        param_counter = 0
        param_regs = ["%rdi", "%rsi", "%rdx", "%rcx", "%r8", "%r9"]

        for inst in instructions:
            if inst.op == OpCode.FUNC_START:
                fn_name = str(inst.arg1)
                in_function = True
                current_fn_name = fn_name
                self.var_offsets = {}
                self.current_offset = -8
                param_counter = 0

                text_lines.append("")
                text_lines.append(f"# ===== Function {fn_name} =====")
                text_lines.append(f"{fn_name}:")
                text_lines.append("    pushq   %rbp              # Save base pointer")
                text_lines.append("    movq    %rsp, %rbp        # Set new base pointer")
                text_lines.append("    subq    $128, %rsp        # Allocate local stack space")
                continue

            if inst.op == OpCode.FUNC_END:
                text_lines.append(f".L_{current_fn_name}_epilogue:")
                text_lines.append("    movq    %rbp, %rsp        # Restore stack pointer")
                text_lines.append("    popq    %rbp              # Restore base pointer")
                text_lines.append("    retq                      # Return to caller")
                in_function = False
                continue

            if not in_function:
                in_function = True
                current_fn_name = "main"
                text_lines.append("")
                text_lines.append("main:")
                text_lines.append("    pushq   %rbp")
                text_lines.append("    movq    %rsp, %rbp")
                text_lines.append("    subq    $128, %rsp")

            # Instruction lowering
            if inst.op == OpCode.LABEL:
                text_lines.append(f".L_{inst.arg1}:")

            elif inst.op == OpCode.ASSIGN:
                src = self._get_operand(inst.arg1)
                dst = self._get_operand(inst.result)
                text_lines.append(f"    movq    {src}, %rax        # {inst.result} = {inst.arg1}")
                text_lines.append(f"    movq    %rax, {dst}")

            elif inst.op == OpCode.ADD:
                src1 = self._get_operand(inst.arg1)
                src2 = self._get_operand(inst.arg2)
                dst = self._get_operand(inst.result)
                text_lines.append(f"    movq    {src1}, %rax")
                text_lines.append(f"    addq    {src2}, %rax       # {inst.result} = {inst.arg1} + {inst.arg2}")
                text_lines.append(f"    movq    %rax, {dst}")

            elif inst.op == OpCode.SUB:
                src1 = self._get_operand(inst.arg1)
                src2 = self._get_operand(inst.arg2)
                dst = self._get_operand(inst.result)
                text_lines.append(f"    movq    {src1}, %rax")
                text_lines.append(f"    subq    {src2}, %rax       # {inst.result} = {inst.arg1} - {inst.arg2}")
                text_lines.append(f"    movq    %rax, {dst}")

            elif inst.op == OpCode.MUL:
                src1 = self._get_operand(inst.arg1)
                src2 = self._get_operand(inst.arg2)
                dst = self._get_operand(inst.result)
                text_lines.append(f"    movq    {src1}, %rax")
                text_lines.append(f"    imulq   {src2}, %rax       # {inst.result} = {inst.arg1} * {inst.arg2}")
                text_lines.append(f"    movq    %rax, {dst}")

            elif inst.op in (OpCode.DIV, OpCode.MOD):
                src1 = self._get_operand(inst.arg1)
                src2 = self._get_operand(inst.arg2)
                dst = self._get_operand(inst.result)
                text_lines.append(f"    movq    {src1}, %rax")
                text_lines.append("    cqto                      # Sign-extend %rax into %rdx:%rax")
                text_lines.append(f"    movq    {src2}, %rcx")
                text_lines.append("    idivq   %rcx")
                target_reg = "%rax" if inst.op == OpCode.DIV else "%rdx"
                text_lines.append(f"    movq    {target_reg}, {dst}")

            elif inst.op in (OpCode.EQ, OpCode.NE, OpCode.LT, OpCode.LE, OpCode.GT, OpCode.GE):
                src1 = self._get_operand(inst.arg1)
                src2 = self._get_operand(inst.arg2)
                dst = self._get_operand(inst.result)
                set_map = {
                    OpCode.EQ: "sete",
                    OpCode.NE: "setne",
                    OpCode.LT: "setl",
                    OpCode.LE: "setle",
                    OpCode.GT: "setg",
                    OpCode.GE: "setge",
                }
                set_inst = set_map[inst.op]
                text_lines.append(f"    movq    {src1}, %rax")
                text_lines.append(f"    cmpq    {src2}, %rax")
                text_lines.append(f"    {set_inst}    %al")
                text_lines.append("    movzbq  %al, %rax")
                text_lines.append(f"    movq    %rax, {dst}")

            elif inst.op == OpCode.NEG:
                src = self._get_operand(inst.arg1)
                dst = self._get_operand(inst.result)
                text_lines.append(f"    movq    {src}, %rax")
                text_lines.append("    negq    %rax")
                text_lines.append(f"    movq    %rax, {dst}")

            elif inst.op == OpCode.NOT:
                src = self._get_operand(inst.arg1)
                dst = self._get_operand(inst.result)
                text_lines.append(f"    movq    {src}, %rax")
                text_lines.append("    xorq    $1, %rax")
                text_lines.append(f"    movq    %rax, {dst}")

            elif inst.op == OpCode.JUMP:
                text_lines.append(f"    jmp     .L_{inst.arg1}")

            elif inst.op == OpCode.JUMP_IF_FALSE:
                cond = self._get_operand(inst.arg1)
                text_lines.append(f"    movq    {cond}, %rax")
                text_lines.append("    cmpq    $0, %rax")
                text_lines.append(f"    je      .L_{inst.arg2}")

            elif inst.op == OpCode.JUMP_IF_TRUE:
                cond = self._get_operand(inst.arg1)
                text_lines.append(f"    movq    {cond}, %rax")
                text_lines.append("    cmpq    $0, %rax")
                text_lines.append(f"    jne     .L_{inst.arg2}")

            elif inst.op == OpCode.PARAM:
                src = self._get_operand(inst.arg1)
                if param_counter < len(param_regs):
                    reg = param_regs[param_counter]
                    text_lines.append(f"    movq    {src}, {reg}        # Pass arg {param_counter+1}")
                else:
                    text_lines.append(f"    pushq   {src}")
                param_counter += 1

            elif inst.op == OpCode.CALL:
                callee = str(inst.arg1)
                text_lines.append(f"    call    {callee}")
                param_counter = 0
                if inst.result:
                    dst = self._get_operand(inst.result)
                    text_lines.append(f"    movq    %rax, {dst}        # Store call return value")

            elif inst.op == OpCode.RETURN:
                if inst.arg1 is not None:
                    src = self._get_operand(inst.arg1)
                    text_lines.append(f"    movq    {src}, %rax        # Set return value")
                else:
                    text_lines.append("    movq    $0, %rax")
                text_lines.append(f"    jmp     .L_{current_fn_name}_epilogue")

            elif inst.op == OpCode.PRINT:
                val = str(inst.arg1).strip('"')
                if val in self.string_literals:
                    lbl = self.string_literals[val]
                    text_lines.append(f"    leaq    {lbl}(%rip), %rdi  # Load string address")
                    text_lines.append("    movq    $0, %rax")
                    text_lines.append("    call    printf")
                else:
                    src = self._get_operand(inst.arg1)
                    text_lines.append(f"    leaq    .LC_int_fmt(%rip), %rdi")
                    text_lines.append(f"    movq    {src}, %rsi")
                    text_lines.append("    movq    $0, %rax")
                    text_lines.append("    call    printf")

        # Assemble Final Assembly Source
        rodata = [
            ".section .rodata",
            '.LC_int_fmt:',
            '    .string "%d\\n"',
        ]
        for s_val, s_lbl in self.string_literals.items():
            rodata.append(f'{s_lbl}:')
            rodata.append(f'    .string "{s_val}\\n"')

        return "\n".join(rodata + [""] + text_lines)
