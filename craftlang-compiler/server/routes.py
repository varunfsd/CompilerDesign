"""FastAPI REST API route handlers for CraftLang Compiler."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from craftlang.compiler import CraftLangCompiler
from .examples import EXAMPLES

router = APIRouter(prefix="/api")
compiler = CraftLangCompiler()


class CompileRequest(BaseModel):
    source: str = Field(..., description="CraftLang source code string")
    execute: bool = Field(default=True, description="Whether to run TAC in the virtual machine")


class CompileResponse(BaseModel):
    success: bool
    source_code: str
    tokens: List[Dict[str, Any]]
    ast_json: Dict[str, Any]
    ast_mermaid: str
    symbol_table: Dict[str, Any]
    symbols_flat: List[Dict[str, Any]]
    tac_raw: List[Dict[str, Any]]
    tac_raw_text: str
    cfg_raw_mermaid: str
    optimization_steps: List[Dict[str, Any]]
    tac_optimized: List[Dict[str, Any]]
    tac_optimized_text: str
    cfg_optimized_mermaid: str
    llvm_ir: str
    assembly: str
    execution_result: Optional[Dict[str, Any]] = None
    diagnostics: List[Dict[str, Any]]
    compilation_time_ms: float


@router.post("/compile", response_model=CompileResponse)
async def compile_code(req: CompileRequest):
    """Compiles CraftLang source code through all pipeline stages."""
    result = compiler.compile(req.source, execute=req.execute)
    return result.to_dict()


@router.get("/examples")
async def get_examples():
    """Returns curated educational sample programs."""
    return {"examples": EXAMPLES}
