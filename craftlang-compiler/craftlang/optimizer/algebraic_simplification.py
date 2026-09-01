"""Algebraic Simplification Optimization Pass."""

from typing import List, Tuple, Any
from ..ir.instructions import TACInstruction, OpCode


class AlgebraicSimplificationPass:
    """Applies algebraic identity simplifications to eliminate redundant operations."""

    def __init__(self):
        self.name = "Algebraic Simplification"
        self.description = "Simplifies arithmetic and logical identity patterns (e.g. x + 0, x * 1, x * 0, x && true)."

    def _is_num(self, val: Any, target: int) -> bool:
        return isinstance(val, (int, float)) and not isinstance(val, bool) and val == target

    def run(self, instructions: List[TACInstruction]) -> Tuple[List[TACInstruction], List[str]]:
        optimized: List[TACInstruction] = []
        changes: List[str] = []

        for inst in instructions:
            orig = inst.format().strip()
            a1 = inst.arg1
            a2 = inst.arg2
            res = inst.result

            # 1. Addition: x + 0 -> x, 0 + x -> x
            if inst.op == OpCode.ADD:
                if self._is_num(a2, 0):
                    new_inst = TACInstruction(OpCode.ASSIGN, arg1=a1, result=res, comment=f"simplified: {orig}")
                    optimized.append(new_inst)
                    changes.append(f"Simplified `{orig}` to `{new_inst.format().strip()}` (x + 0 = x)")
                    continue
                if self._is_num(a1, 0):
                    new_inst = TACInstruction(OpCode.ASSIGN, arg1=a2, result=res, comment=f"simplified: {orig}")
                    optimized.append(new_inst)
                    changes.append(f"Simplified `{orig}` to `{new_inst.format().strip()}` (0 + x = x)")
                    continue

            # 2. Subtraction: x - 0 -> x
            elif inst.op == OpCode.SUB:
                if self._is_num(a2, 0):
                    new_inst = TACInstruction(OpCode.ASSIGN, arg1=a1, result=res, comment=f"simplified: {orig}")
                    optimized.append(new_inst)
                    changes.append(f"Simplified `{orig}` to `{new_inst.format().strip()}` (x - 0 = x)")
                    continue

            # 3. Multiplication: x * 1 -> x, 1 * x -> x, x * 0 -> 0, 0 * x -> 0
            elif inst.op == OpCode.MUL:
                if self._is_num(a2, 1):
                    new_inst = TACInstruction(OpCode.ASSIGN, arg1=a1, result=res, comment=f"simplified: {orig}")
                    optimized.append(new_inst)
                    changes.append(f"Simplified `{orig}` to `{new_inst.format().strip()}` (x * 1 = x)")
                    continue
                if self._is_num(a1, 1):
                    new_inst = TACInstruction(OpCode.ASSIGN, arg1=a2, result=res, comment=f"simplified: {orig}")
                    optimized.append(new_inst)
                    changes.append(f"Simplified `{orig}` to `{new_inst.format().strip()}` (1 * x = x)")
                    continue
                if self._is_num(a1, 0) or self._is_num(a2, 0):
                    new_inst = TACInstruction(OpCode.ASSIGN, arg1=0, result=res, comment=f"simplified: {orig}")
                    optimized.append(new_inst)
                    changes.append(f"Simplified `{orig}` to `{new_inst.format().strip()}` (x * 0 = 0)")
                    continue

            # 4. Division: x / 1 -> x
            elif inst.op == OpCode.DIV:
                if self._is_num(a2, 1):
                    new_inst = TACInstruction(OpCode.ASSIGN, arg1=a1, result=res, comment=f"simplified: {orig}")
                    optimized.append(new_inst)
                    changes.append(f"Simplified `{orig}` to `{new_inst.format().strip()}` (x / 1 = x)")
                    continue

            # 5. Logical AND: x && true -> x, true && x -> x, x && false -> false, false && x -> false
            elif inst.op == OpCode.AND:
                if a2 is True:
                    new_inst = TACInstruction(OpCode.ASSIGN, arg1=a1, result=res, comment=f"simplified: {orig}")
                    optimized.append(new_inst)
                    changes.append(f"Simplified `{orig}` to `{new_inst.format().strip()}` (x && true = x)")
                    continue
                if a1 is True:
                    new_inst = TACInstruction(OpCode.ASSIGN, arg1=a2, result=res, comment=f"simplified: {orig}")
                    optimized.append(new_inst)
                    changes.append(f"Simplified `{orig}` to `{new_inst.format().strip()}` (true && x = x)")
                    continue
                if a1 is False or a2 is False:
                    new_inst = TACInstruction(OpCode.ASSIGN, arg1=False, result=res, comment=f"simplified: {orig}")
                    optimized.append(new_inst)
                    changes.append(f"Simplified `{orig}` to `{new_inst.format().strip()}` (x && false = false)")
                    continue

            # 6. Logical OR: x || false -> x, false || x -> x, x || true -> true, true || x -> true
            elif inst.op == OpCode.OR:
                if a2 is False:
                    new_inst = TACInstruction(OpCode.ASSIGN, arg1=a1, result=res, comment=f"simplified: {orig}")
                    optimized.append(new_inst)
                    changes.append(f"Simplified `{orig}` to `{new_inst.format().strip()}` (x || false = x)")
                    continue
                if a1 is False:
                    new_inst = TACInstruction(OpCode.ASSIGN, arg1=a2, result=res, comment=f"simplified: {orig}")
                    optimized.append(new_inst)
                    changes.append(f"Simplified `{orig}` to `{new_inst.format().strip()}` (false || x = x)")
                    continue
                if a1 is True or a2 is True:
                    new_inst = TACInstruction(OpCode.ASSIGN, arg1=True, result=res, comment=f"simplified: {orig}")
                    optimized.append(new_inst)
                    changes.append(f"Simplified `{orig}` to `{new_inst.format().strip()}` (x || true = true)")
                    continue

            optimized.append(inst)

        return optimized, changes
