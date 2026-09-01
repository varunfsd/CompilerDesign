"""Top-level Compiler Orchestrator for CraftLang."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import time

from .lexer.lexer import Lexer
from .parser.parser import Parser
from .parser.visualizer import ASTVisualizer
from .semantics.analyzer import SemanticAnalyzer
from .ir.tac_generator import TACGenerator
from .ir.cfg import CFGBuilder
from .optimizer.pass_manager import PassManager, OptimizationStep
from .codegen.llvm_emitter import LLVMEmitter
from .codegen.asm_emitter import AssemblyEmitter
from .vm.tac_interpreter import TACInterpreter, ExecutionResult
from .errors import CompilerError, Diagnostic


@dataclass
class CompilationResult:
    """Encapsulates the complete end-to-end compilation artifact data."""
    success: bool
    source_code: str
    tokens: List[Dict[str, Any]] = field(default_factory=list)
    ast_json: Dict[str, Any] = field(default_factory=dict)
    ast_mermaid: str = ""
    symbol_table: Dict[str, Any] = field(default_factory=dict)
    symbols_flat: List[Dict[str, Any]] = field(default_factory=list)
    tac_raw: List[Dict[str, Any]] = field(default_factory=list)
    tac_raw_text: str = ""
    cfg_raw_mermaid: str = ""
    optimization_steps: List[Dict[str, Any]] = field(default_factory=list)
    tac_optimized: List[Dict[str, Any]] = field(default_factory=list)
    tac_optimized_text: str = ""
    cfg_optimized_mermaid: str = ""
    llvm_ir: str = ""
    assembly: str = ""
    execution_result: Optional[Dict[str, Any]] = None
    diagnostics: List[Dict[str, Any]] = field(default_factory=list)
    compilation_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "source_code": self.source_code,
            "tokens": self.tokens,
            "ast_json": self.ast_json,
            "ast_mermaid": self.ast_mermaid,
            "symbol_table": self.symbol_table,
            "symbols_flat": self.symbols_flat,
            "tac_raw": self.tac_raw,
            "tac_raw_text": self.tac_raw_text,
            "cfg_raw_mermaid": self.cfg_raw_mermaid,
            "optimization_steps": self.optimization_steps,
            "tac_optimized": self.tac_optimized,
            "tac_optimized_text": self.tac_optimized_text,
            "cfg_optimized_mermaid": self.cfg_optimized_mermaid,
            "llvm_ir": self.llvm_ir,
            "assembly": self.assembly,
            "execution_result": self.execution_result,
            "diagnostics": self.diagnostics,
            "compilation_time_ms": self.compilation_time_ms,
        }


class CraftLangCompiler:
    """Orchestrates all compiler pipeline stages for CraftLang source code."""

    def __init__(self):
        self.pass_manager = PassManager()
        self.llvm_emitter = LLVMEmitter()
        self.asm_emitter = AssemblyEmitter()
        self.interpreter = TACInterpreter()

    def compile(self, source: str, execute: bool = True) -> CompilationResult:
        start_time = time.perf_counter()
        result = CompilationResult(success=False, source_code=source)

        try:
            # 1. Lexical Analysis
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            result.tokens = [t.to_dict() for t in tokens]

            # 2. Syntax Analysis & AST Construction
            parser = Parser(tokens, source=source)
            ast = parser.parse()
            result.ast_json = ASTVisualizer.to_tree_json(ast)
            result.ast_mermaid = ASTVisualizer.to_mermaid(ast)

            # 3. Semantic Analysis & Type Checking
            analyzer = SemanticAnalyzer(source=source)
            global_scope = analyzer.analyze(ast)
            result.symbol_table = global_scope.to_dict()
            result.symbols_flat = global_scope.get_all_symbols_flat()

            # 4. Intermediate Representation (Three-Address Code) Lowering
            tac_gen = TACGenerator()
            raw_tac = tac_gen.generate(ast)
            result.tac_raw = [inst.to_dict() for inst in raw_tac]
            result.tac_raw_text = "\n".join(inst.format() for inst in raw_tac)

            # Control Flow Graph for Raw TAC
            raw_cfg = CFGBuilder.build_from_instructions(raw_tac)
            result.cfg_raw_mermaid = raw_cfg.to_mermaid()

            # 5. Multi-Pass Optimization
            optimized_tac, opt_steps = self.pass_manager.optimize(raw_tac)
            result.optimization_steps = [step.to_dict() for step in opt_steps]
            result.tac_optimized = [inst.to_dict() for inst in optimized_tac]
            result.tac_optimized_text = "\n".join(inst.format() for inst in optimized_tac)

            # Control Flow Graph for Optimized TAC
            opt_cfg = CFGBuilder.build_from_instructions(optimized_tac)
            result.cfg_optimized_mermaid = opt_cfg.to_mermaid()

            # 6. Target Code Generation
            result.llvm_ir = self.llvm_emitter.emit(optimized_tac)
            result.assembly = self.asm_emitter.emit(optimized_tac)

            # 7. Virtual Machine / TAC Execution
            if execute:
                exec_res = self.interpreter.execute(optimized_tac)
                result.execution_result = exec_res.to_dict()

            result.success = True

        except CompilerError as ce:
            result.success = False
            result.diagnostics = [ce.diagnostic.to_dict()]
        except Exception as e:
            result.success = False
            diag = Diagnostic(
                stage="Compiler Pipeline",
                message=str(e),
                line=1,
                column=1,
                severity="FATAL",
            )
            result.diagnostics = [diag.to_dict()]

        elapsed = (time.perf_counter() - start_time) * 1000.0
        result.compilation_time_ms = round(elapsed, 2)
        return result
