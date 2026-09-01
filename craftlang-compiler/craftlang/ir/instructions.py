"""Three-Address Code (TAC) instruction set and Quadruple definitions."""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, Any, Dict


class OpCode(Enum):
    # Data Movement
    ASSIGN = auto()         # result = arg1

    # Arithmetic
    ADD = auto()            # result = arg1 + arg2
    SUB = auto()            # result = arg1 - arg2
    MUL = auto()            # result = arg1 * arg2
    DIV = auto()            # result = arg1 / arg2
    MOD = auto()            # result = arg1 % arg2
    NEG = auto()            # result = -arg1

    # Logical
    AND = auto()            # result = arg1 && arg2
    OR = auto()             # result = arg1 || arg2
    NOT = auto()            # result = !arg1

    # Relational
    EQ = auto()             # result = (arg1 == arg2)
    NE = auto()             # result = (arg1 != arg2)
    LT = auto()             # result = (arg1 < arg2)
    LE = auto()             # result = (arg1 <= arg2)
    GT = auto()             # result = (arg1 > arg2)
    GE = auto()             # result = (arg1 >= arg2)

    # Control Flow
    LABEL = auto()          # LABEL arg1:
    JUMP = auto()           # goto arg1
    JUMP_IF_TRUE = auto()   # if arg1 goto arg2
    JUMP_IF_FALSE = auto()  # if_false arg1 goto arg2

    # Functions & Calls
    FUNC_START = auto()     # func_begin arg1
    FUNC_END = auto()       # func_end arg1
    PARAM = auto()          # param arg1
    CALL = auto()           # result = call arg1, arg2 (arg1=callee, arg2=num_args)
    RETURN = auto()         # return arg1

    # I/O
    PRINT = auto()          # print arg1


@dataclass
class TACInstruction:
    """Represents a single Three-Address Code Quadruple."""
    op: OpCode
    arg1: Optional[Any] = None
    arg2: Optional[Any] = None
    result: Optional[str] = None
    comment: Optional[str] = None

    def __repr__(self) -> str:
        return self.format()

    def format(self) -> str:
        """Formats the instruction as standard readable Three-Address Code."""
        c = f"  # {self.comment}" if self.comment else ""

        if self.op == OpCode.LABEL:
            return f"{self.arg1}:{c}"

        if self.op == OpCode.ASSIGN:
            return f"  {self.result} = {self.arg1}{c}"

        if self.op in (OpCode.ADD, OpCode.SUB, OpCode.MUL, OpCode.DIV, OpCode.MOD,
                       OpCode.AND, OpCode.OR,
                       OpCode.EQ, OpCode.NE, OpCode.LT, OpCode.LE, OpCode.GT, OpCode.GE):
            op_symbols = {
                OpCode.ADD: "+", OpCode.SUB: "-", OpCode.MUL: "*", OpCode.DIV: "/", OpCode.MOD: "%",
                OpCode.AND: "&&", OpCode.OR: "||",
                OpCode.EQ: "==", OpCode.NE: "!=", OpCode.LT: "<", OpCode.LE: "<=",
                OpCode.GT: ">", OpCode.GE: ">=",
            }
            sym = op_symbols[self.op]
            return f"  {self.result} = {self.arg1} {sym} {self.arg2}{c}"

        if self.op == OpCode.NEG:
            return f"  {self.result} = -{self.arg1}{c}"

        if self.op == OpCode.NOT:
            return f"  {self.result} = !{self.arg1}{c}"

        if self.op == OpCode.JUMP:
            return f"  goto {self.arg1}{c}"

        if self.op == OpCode.JUMP_IF_TRUE:
            return f"  if {self.arg1} goto {self.arg2}{c}"

        if self.op == OpCode.JUMP_IF_FALSE:
            return f"  if_false {self.arg1} goto {self.arg2}{c}"

        if self.op == OpCode.FUNC_START:
            return f"func {self.arg1}:{c}"

        if self.op == OpCode.FUNC_END:
            return f"end_func {self.arg1}{c}"

        if self.op == OpCode.PARAM:
            return f"  param {self.arg1}{c}"

        if self.op == OpCode.CALL:
            if self.result:
                return f"  {self.result} = call {self.arg1}, {self.arg2}{c}"
            return f"  call {self.arg1}, {self.arg2}{c}"

        if self.op == OpCode.RETURN:
            if self.arg1 is not None:
                return f"  return {self.arg1}{c}"
            return f"  return{c}"

        if self.op == OpCode.PRINT:
            return f"  print {self.arg1}{c}"

        return f"  {self.op.name} {self.arg1} {self.arg2} -> {self.result}{c}"

    def to_dict(self) -> Dict[str, Any]:
        """Serializes instruction to dictionary for frontend inspection."""
        return {
            "op": self.op.name,
            "arg1": str(self.arg1) if self.arg1 is not None else None,
            "arg2": str(self.arg2) if self.arg2 is not None else None,
            "result": self.result,
            "formatted": self.format().strip(),
            "comment": self.comment,
        }
