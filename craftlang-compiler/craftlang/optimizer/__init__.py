"""CraftLang Multi-Pass Optimization Engine."""

from .pass_manager import PassManager, OptimizationStep
from .constant_folding import ConstantFoldingPass
from .constant_propagation import ConstantPropagationPass
from .algebraic_simplification import AlgebraicSimplificationPass
from .dead_code_elimination import DeadCodeEliminationPass

__all__ = [
    "PassManager",
    "OptimizationStep",
    "ConstantFoldingPass",
    "ConstantPropagationPass",
    "AlgebraicSimplificationPass",
    "DeadCodeEliminationPass",
]
