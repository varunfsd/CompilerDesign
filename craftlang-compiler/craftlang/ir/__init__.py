"""CraftLang Intermediate Representation (TAC) package."""

from .instructions import OpCode, TACInstruction
from .basic_block import BasicBlock, BasicBlockBuilder
from .cfg import ControlFlowGraph, CFGBuilder
from .tac_generator import TACGenerator

__all__ = [
    "OpCode",
    "TACInstruction",
    "BasicBlock",
    "BasicBlockBuilder",
    "ControlFlowGraph",
    "CFGBuilder",
    "TACGenerator",
]
