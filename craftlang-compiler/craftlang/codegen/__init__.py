"""CraftLang Target Code Generation package (LLVM IR & Assembly)."""

from .llvm_emitter import LLVMEmitter
from .asm_emitter import AssemblyEmitter

__all__ = ["LLVMEmitter", "AssemblyEmitter"]
