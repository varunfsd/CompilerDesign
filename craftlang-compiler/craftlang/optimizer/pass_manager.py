"""Pass Manager for orchestrating compiler optimization passes and tracking step-by-step diffs."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple
from ..ir.instructions import TACInstruction


@dataclass
class OptimizationStep:
    """Records the effects and transformations of an individual optimization pass."""
    pass_name: str
    description: str
    before_code: List[str]
    after_code: List[str]
    changes_made: List[str] = field(default_factory=list)
    has_changed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pass_name": self.pass_name,
            "description": self.description,
            "before_code": self.before_code,
            "after_code": self.after_code,
            "changes_made": self.changes_made,
            "has_changed": self.has_changed,
        }


class PassManager:
    """Manages sequential execution of IR optimization passes and collects educational step traces."""

    def __init__(self):
        self.steps: List[OptimizationStep] = []

    def optimize(self, instructions: List[TACInstruction], iterations: int = 2) -> Tuple[List[TACInstruction], List[OptimizationStep]]:
        """Runs optimization pipeline until convergence or max iterations."""
        from .constant_propagation import ConstantPropagationPass
        from .constant_folding import ConstantFoldingPass
        from .algebraic_simplification import AlgebraicSimplificationPass
        from .dead_code_elimination import DeadCodeEliminationPass

        current_instructions = [inst for inst in instructions]
        self.steps = []

        passes = [
            ConstantPropagationPass(),
            ConstantFoldingPass(),
            AlgebraicSimplificationPass(),
            DeadCodeEliminationPass(),
        ]

        for it in range(iterations):
            any_change_in_iteration = False
            for opt_pass in passes:
                before_formatted = [i.format() for i in current_instructions]
                optimized_instructions, changes = opt_pass.run(current_instructions)
                after_formatted = [i.format() for i in optimized_instructions]

                has_changed = (before_formatted != after_formatted) or len(changes) > 0
                if has_changed:
                    any_change_in_iteration = True

                self.steps.append(OptimizationStep(
                    pass_name=f"{opt_pass.name} (Pass {it+1})",
                    description=opt_pass.description,
                    before_code=before_formatted,
                    after_code=after_formatted,
                    changes_made=changes,
                    has_changed=has_changed,
                ))

                current_instructions = optimized_instructions

            # Early exit if fixed point reached
            if not any_change_in_iteration:
                break

        return current_instructions, self.steps
