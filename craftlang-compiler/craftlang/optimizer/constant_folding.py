"""Constant Folding Optimization Pass."""

from typing import List, Tuple, Any
from ..ir.instructions import TACInstruction, OpCode


class ConstantFoldingPass:
    """Evaluates operations with compile-time known literal operands."""

    def __init__(self):
        self.name = "Constant Folding"
        self.description = "Computes constant arithmetic, relational, and logical expressions at compile time."

    def _is_constant(self, val: Any) -> bool:
        """Determines if a value is a compile-time constant literal (not a variable name)."""
        if isinstance(val, (int, float, bool)):
            return True
        if isinstance(val, str) and len(val) >= 2 and val.startswith('"') and val.endswith('"'):
            return True
        return False

    def run(self, instructions: List[TACInstruction]) -> Tuple[List[TACInstruction], List[str]]:
        optimized: List[TACInstruction] = []
        changes: List[str] = []

        for inst in instructions:
            # Check for binary operations with two constant literals
            if inst.op in (OpCode.ADD, OpCode.SUB, OpCode.MUL, OpCode.DIV, OpCode.MOD,
                           OpCode.EQ, OpCode.NE, OpCode.LT, OpCode.LE, OpCode.GT, OpCode.GE,
                           OpCode.AND, OpCode.OR):
                a1 = inst.arg1
                a2 = inst.arg2

                if self._is_constant(a1) and self._is_constant(a2):
                    folded_val = self._fold_binary(inst.op, a1, a2)
                    if folded_val is not None:
                        orig = inst.format().strip()
                        new_inst = TACInstruction(
                            op=OpCode.ASSIGN,
                            arg1=folded_val,
                            result=inst.result,
                            comment=f"folded: {orig}",
                        )
                        optimized.append(new_inst)
                        changes.append(f"Folded `{orig}` into `{new_inst.format().strip()}`")
                        continue

            # Check for unary operations with constant literal
            elif inst.op in (OpCode.NEG, OpCode.NOT):
                a1 = inst.arg1
                if self._is_constant(a1):
                    folded_val = self._fold_unary(inst.op, a1)
                    if folded_val is not None:
                        orig = inst.format().strip()
                        new_inst = TACInstruction(
                            op=OpCode.ASSIGN,
                            arg1=folded_val,
                            result=inst.result,
                            comment=f"folded: {orig}",
                        )
                        optimized.append(new_inst)
                        changes.append(f"Folded `{orig}` into `{new_inst.format().strip()}`")
                        continue

            # Check for conditional jumps with constant conditions
            elif inst.op == OpCode.JUMP_IF_FALSE and self._is_constant(inst.arg1):
                cond_val = bool(inst.arg1)
                if cond_val is False:
                    # Condition is always False, jump ALWAYS happens
                    orig = inst.format().strip()
                    new_inst = TACInstruction(op=OpCode.JUMP, arg1=inst.arg2, comment="always jumps")
                    optimized.append(new_inst)
                    changes.append(f"Converted `{orig}` (always false) into unconditional jump `{new_inst.format().strip()}`")
                    continue
                elif cond_val is True:
                    # Condition is always True, jump NEVER happens
                    orig = inst.format().strip()
                    changes.append(f"Removed dead jump `{orig}` (condition always true)")
                    continue

            elif inst.op == OpCode.JUMP_IF_TRUE and self._is_constant(inst.arg1):
                cond_val = bool(inst.arg1)
                if cond_val is True:
                    # Condition is always True, jump ALWAYS happens
                    orig = inst.format().strip()
                    new_inst = TACInstruction(op=OpCode.JUMP, arg1=inst.arg2, comment="always jumps")
                    optimized.append(new_inst)
                    changes.append(f"Converted `{orig}` (always true) into unconditional jump `{new_inst.format().strip()}`")
                    continue
                elif cond_val is False:
                    # Condition is always False, jump NEVER happens
                    orig = inst.format().strip()
                    changes.append(f"Removed dead jump `{orig}` (condition always false)")
                    continue

            optimized.append(inst)

        return optimized, changes

    def _fold_binary(self, op: OpCode, a1: Any, a2: Any) -> Any:
        try:
            # Handle string literal stripping if needed
            if isinstance(a1, str) and a1.startswith('"') and a1.endswith('"'):
                a1_raw = a1[1:-1]
            else:
                a1_raw = a1

            if isinstance(a2, str) and a2.startswith('"') and a2.endswith('"'):
                a2_raw = a2[1:-1]
            else:
                a2_raw = a2

            if op == OpCode.ADD:
                if isinstance(a1, str) or isinstance(a2, str):
                    return f'"{a1_raw}{a2_raw}"'
                return a1 + a2
            if op == OpCode.SUB:
                return a1 - a2
            if op == OpCode.MUL:
                return a1 * a2
            if op == OpCode.DIV:
                if a2 == 0:
                    return None
                if isinstance(a1, int) and isinstance(a2, int):
                    return a1 // a2
                return a1 / a2
            if op == OpCode.MOD:
                if a2 == 0:
                    return None
                return a1 % a2
            if op == OpCode.EQ:
                return a1 == a2
            if op == OpCode.NE:
                return a1 != a2
            if op == OpCode.LT:
                return a1 < a2
            if op == OpCode.LE:
                return a1 <= a2
            if op == OpCode.GT:
                return a1 > a2
            if op == OpCode.GE:
                return a1 >= a2
            if op == OpCode.AND:
                return bool(a1) and bool(a2)
            if op == OpCode.OR:
                return bool(a1) or bool(a2)
        except Exception:
            return None
        return None

    def _fold_unary(self, op: OpCode, a1: Any) -> Any:
        try:
            if op == OpCode.NEG and isinstance(a1, (int, float)):
                return -a1
            if op == OpCode.NOT and isinstance(a1, bool):
                return not a1
        except Exception:
            return None
        return None
