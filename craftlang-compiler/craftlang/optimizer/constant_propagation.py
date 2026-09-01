"""Constant Propagation Optimization Pass."""

from typing import List, Tuple, Dict, Any
from ..ir.instructions import TACInstruction, OpCode


class ConstantPropagationPass:
    """Propagates known constant values assigned to variables and temporaries."""

    def __init__(self):
        self.name = "Constant Propagation"
        self.description = "Replaces variable uses with their known constant values throughout straight-line basic blocks."

    def _is_literal(self, val: Any) -> bool:
        """Checks if a value is an integer, float, boolean, or string literal."""
        if isinstance(val, (int, float, bool)):
            return True
        if isinstance(val, str) and len(val) >= 2 and val.startswith('"') and val.endswith('"'):
            return True
        return False

    def _is_identifier(self, val: Any) -> bool:
        """Checks if a value is a variable or temporary name."""
        if isinstance(val, str):
            return not (len(val) >= 2 and val.startswith('"') and val.endswith('"'))
        return False

    def run(self, instructions: List[TACInstruction]) -> Tuple[List[TACInstruction], List[str]]:
        optimized: List[TACInstruction] = []
        changes: List[str] = []
        known_constants: Dict[str, Any] = {}

        for inst in instructions:
            # Control flow boundaries and loops invalidate forward propagation assumptions
            if inst.op in (OpCode.LABEL, OpCode.FUNC_START, OpCode.FUNC_END):
                known_constants.clear()
                optimized.append(inst)
                continue

            arg1 = inst.arg1
            arg2 = inst.arg2
            modified = False

            # Replace arg1 if it's an identifier with a known constant literal value
            if self._is_identifier(arg1) and arg1 in known_constants:
                val = known_constants[arg1]
                changes.append(f"Propagated constant `{arg1} = {val!r}` into `{inst.format().strip()}`")
                arg1 = val
                modified = True

            # Replace arg2 if it's an identifier with a known constant literal value
            if self._is_identifier(arg2) and arg2 in known_constants:
                val = known_constants[arg2]
                changes.append(f"Propagated constant `{arg2} = {val!r}` into `{inst.format().strip()}`")
                arg2 = val
                modified = True

            new_inst = TACInstruction(
                op=inst.op,
                arg1=arg1,
                arg2=arg2,
                result=inst.result,
                comment=inst.comment,
            ) if modified else inst

            # Update known constants dictionary
            if new_inst.op == OpCode.ASSIGN and new_inst.result:
                if self._is_literal(new_inst.arg1):
                    known_constants[new_inst.result] = new_inst.arg1
                else:
                    known_constants.pop(new_inst.result, None)

            elif new_inst.result:
                # If an operation defines a result, it is not yet a known literal constant
                known_constants.pop(new_inst.result, None)

            optimized.append(new_inst)

        return optimized, changes
