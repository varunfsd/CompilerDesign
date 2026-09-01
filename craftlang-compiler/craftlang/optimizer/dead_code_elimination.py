"""Dead Code Elimination Optimization Pass."""

from typing import List, Tuple, Set
from ..ir.instructions import TACInstruction, OpCode


class DeadCodeEliminationPass:
    """Eliminates unreachable instructions, unused labels, and dead variable/temporary assignments."""

    def __init__(self):
        self.name = "Dead Code Elimination"
        self.description = "Removes unreachable blocks after unconditional jumps, unused labels, and dead assignments."

    def run(self, instructions: List[TACInstruction]) -> Tuple[List[TACInstruction], List[str]]:
        changes: List[str] = []

        # Step 1: Remove unreachable code after JUMP or RETURN until next LABEL/FUNC_END
        reachable_insts: List[TACInstruction] = []
        is_unreachable = False

        for inst in instructions:
            if inst.op in (OpCode.LABEL, OpCode.FUNC_START, OpCode.FUNC_END):
                is_unreachable = False
                reachable_insts.append(inst)
                continue

            if is_unreachable:
                changes.append(f"Eliminated unreachable instruction: `{inst.format().strip()}`")
                continue

            reachable_insts.append(inst)

            if inst.op in (OpCode.JUMP, OpCode.RETURN):
                is_unreachable = True

        # Step 2: Identify used variables and referenced labels
        used_variables: Set[str] = set()
        targeted_labels: Set[str] = set()

        for inst in reachable_insts:
            # Check jump targets
            if inst.op == OpCode.JUMP:
                targeted_labels.add(str(inst.arg1))
            elif inst.op in (OpCode.JUMP_IF_TRUE, OpCode.JUMP_IF_FALSE):
                targeted_labels.add(str(inst.arg2))

            # Check variable usages
            for arg in (inst.arg1, inst.arg2):
                if isinstance(arg, str) and not (arg.startswith('"') and arg.endswith('"')):
                    used_variables.add(arg)

        # Step 3: Filter out dead temporary assignments and unreferenced labels
        final_insts: List[TACInstruction] = []

        for inst in reachable_insts:
            # Unreferenced label (excluding function start/end)
            if inst.op == OpCode.LABEL:
                lbl_name = str(inst.arg1)
                if lbl_name not in targeted_labels:
                    changes.append(f"Removed unused label `{lbl_name}:`")
                    continue

            # Dead assignment (e.g. dead = 100 or t0 = 5 where result is never read)
            if inst.op in (OpCode.ASSIGN, OpCode.ADD, OpCode.SUB, OpCode.MUL, OpCode.DIV, OpCode.MOD,
                           OpCode.EQ, OpCode.NE, OpCode.LT, OpCode.LE, OpCode.GT, OpCode.GE,
                           OpCode.AND, OpCode.OR, OpCode.NOT, OpCode.NEG):
                if inst.result and inst.result not in used_variables and inst.result != "main":
                    changes.append(f"Eliminated unused assignment `{inst.format().strip()}`")
                    continue

            final_insts.append(inst)

        return final_insts, changes
