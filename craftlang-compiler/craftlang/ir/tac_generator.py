"""AST to Three-Address Code (TAC) Lowering Generator."""

from typing import List, Optional, Any
from ..parser.ast_nodes import (
    ASTNode,
    Program,
    FunctionDef,
    Param,
    VarDecl,
    Assign,
    IfStmt,
    WhileStmt,
    ReturnStmt,
    PrintStmt,
    Block,
    ExprStmt,
    BinaryOp,
    UnaryOp,
    Literal,
    Identifier,
    CallExpr,
)
from .instructions import TACInstruction, OpCode


class TACGenerator:
    """Lowers CraftLang AST into Three-Address Code (TAC) Quadruples."""

    def __init__(self):
        self.instructions: List[TACInstruction] = []
        self.temp_counter: int = 0
        self.label_counter: int = 0

    def new_temp(self) -> str:
        """Allocates a fresh temporary variable name."""
        name = f"t{self.temp_counter}"
        self.temp_counter += 1
        return name

    def new_label(self, prefix: str = "L") -> str:
        """Allocates a fresh jump label."""
        name = f"{prefix}{self.label_counter}"
        self.label_counter += 1
        return name

    def emit(self, op: OpCode, arg1: Optional[Any] = None, arg2: Optional[Any] = None,
             result: Optional[str] = None, comment: Optional[str] = None) -> TACInstruction:
        """Emits a single TAC instruction."""
        inst = TACInstruction(op=op, arg1=arg1, arg2=arg2, result=result, comment=comment)
        self.instructions.append(inst)
        return inst

    def generate(self, program: Program) -> List[TACInstruction]:
        """Lowers the entire program AST into TAC instructions."""
        self.instructions = []
        self.temp_counter = 0
        self.label_counter = 0

        top_level_stmts: List[ASTNode] = []
        functions: List[FunctionDef] = []

        for decl in program.declarations:
            if isinstance(decl, FunctionDef):
                functions.append(decl)
            else:
                top_level_stmts.append(decl)

        has_main = any(f.name == "main" for f in functions)

        if top_level_stmts and not has_main:
            self.emit(OpCode.FUNC_START, arg1="main")
            for stmt in top_level_stmts:
                self._generate_stmt(stmt)
            self.emit(OpCode.RETURN)
            self.emit(OpCode.FUNC_END, arg1="main")
        elif top_level_stmts:
            for stmt in top_level_stmts:
                self._generate_stmt(stmt)

        for func in functions:
            self._generate_function(func)

        return self.instructions

    def _generate_function(self, func: FunctionDef) -> None:
        self.emit(OpCode.FUNC_START, arg1=func.name)

        # Bind incoming parameter arguments to parameter variable names
        for i, param in enumerate(func.params):
            self.emit(OpCode.ASSIGN, arg1=f"param_{i}", result=param.name, comment=f"bind param {param.name}")

        for stmt in func.body.statements:
            self._generate_stmt(stmt)

        # Ensure trailing return for void functions
        if not self.instructions or self.instructions[-1].op != OpCode.RETURN:
            self.emit(OpCode.RETURN)

        self.emit(OpCode.FUNC_END, arg1=func.name)

    def _generate_stmt(self, stmt: ASTNode) -> None:
        if isinstance(stmt, VarDecl):
            if stmt.initializer:
                val = self._generate_expr(stmt.initializer)
                self.emit(OpCode.ASSIGN, arg1=val, result=stmt.name)

        elif isinstance(stmt, Assign):
            val = self._generate_expr(stmt.value)
            self.emit(OpCode.ASSIGN, arg1=val, result=stmt.name)

        elif isinstance(stmt, Block):
            for s in stmt.statements:
                self._generate_stmt(s)

        elif isinstance(stmt, IfStmt):
            cond = self._generate_expr(stmt.condition)
            if stmt.else_branch:
                else_lbl = self.new_label("L_else_")
                end_lbl = self.new_label("L_end_if_")
                self.emit(OpCode.JUMP_IF_FALSE, arg1=cond, arg2=else_lbl)
                self._generate_stmt(stmt.then_branch)
                self.emit(OpCode.JUMP, arg1=end_lbl)
                self.emit(OpCode.LABEL, arg1=else_lbl)
                self._generate_stmt(stmt.else_branch)
                self.emit(OpCode.LABEL, arg1=end_lbl)
            else:
                end_lbl = self.new_label("L_end_if_")
                self.emit(OpCode.JUMP_IF_FALSE, arg1=cond, arg2=end_lbl)
                self._generate_stmt(stmt.then_branch)
                self.emit(OpCode.LABEL, arg1=end_lbl)

        elif isinstance(stmt, WhileStmt):
            start_lbl = self.new_label("L_while_start_")
            end_lbl = self.new_label("L_while_end_")
            self.emit(OpCode.LABEL, arg1=start_lbl)
            cond = self._generate_expr(stmt.condition)
            self.emit(OpCode.JUMP_IF_FALSE, arg1=cond, arg2=end_lbl)
            self._generate_stmt(stmt.body)
            self.emit(OpCode.JUMP, arg1=start_lbl)
            self.emit(OpCode.LABEL, arg1=end_lbl)

        elif isinstance(stmt, ReturnStmt):
            if stmt.value:
                val = self._generate_expr(stmt.value)
                self.emit(OpCode.RETURN, arg1=val)
            else:
                self.emit(OpCode.RETURN)

        elif isinstance(stmt, PrintStmt):
            for arg in stmt.args:
                val = self._generate_expr(arg)
                self.emit(OpCode.PRINT, arg1=val)

        elif isinstance(stmt, ExprStmt):
            self._generate_expr(stmt.expr)

    def _generate_expr(self, expr: ASTNode) -> Any:
        if isinstance(expr, Literal):
            if isinstance(expr.value, str):
                return f'"{expr.value}"'
            return expr.value

        if isinstance(expr, Identifier):
            return expr.name

        if isinstance(expr, BinaryOp):
            left_val = self._generate_expr(expr.left)
            right_val = self._generate_expr(expr.right)
            temp = self.new_temp()

            op_map = {
                "+": OpCode.ADD,
                "-": OpCode.SUB,
                "*": OpCode.MUL,
                "/": OpCode.DIV,
                "%": OpCode.MOD,
                "==": OpCode.EQ,
                "!=": OpCode.NE,
                "<": OpCode.LT,
                "<=": OpCode.LE,
                ">": OpCode.GT,
                ">=": OpCode.GE,
                "&&": OpCode.AND,
                "||": OpCode.OR,
            }
            op_code = op_map.get(expr.op, OpCode.ADD)
            self.emit(op_code, arg1=left_val, arg2=right_val, result=temp)
            return temp

        if isinstance(expr, UnaryOp):
            opnd_val = self._generate_expr(expr.operand)
            temp = self.new_temp()
            if expr.op == "-":
                self.emit(OpCode.NEG, arg1=opnd_val, result=temp)
            elif expr.op == "!":
                self.emit(OpCode.NOT, arg1=opnd_val, result=temp)
            return temp

        if isinstance(expr, CallExpr):
            arg_vals = [self._generate_expr(a) for a in expr.args]
            for val in arg_vals:
                self.emit(OpCode.PARAM, arg1=val)
            temp = self.new_temp()
            self.emit(OpCode.CALL, arg1=expr.callee, arg2=len(arg_vals), result=temp)
            return temp

        return None
