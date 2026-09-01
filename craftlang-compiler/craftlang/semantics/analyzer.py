"""Semantic Analyzer and Type Checker for CraftLang."""

from typing import List, Optional, Dict, Any
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
from ..errors import SemanticError, Diagnostic
from .types import (
    Type,
    INT_TYPE,
    FLOAT_TYPE,
    BOOL_TYPE,
    STRING_TYPE,
    VOID_TYPE,
    UNKNOWN_TYPE,
    FunctionType,
    from_type_name,
    check_assignment_compatibility,
    get_binary_result_type,
)
from .symbol_table import Symbol, SymbolTable


class SemanticAnalyzer:
    """Performs scoped symbol resolution, type checking, and semantic validation."""

    def __init__(self, source: Optional[str] = None):
        self.source_lines: List[str] = source.splitlines() if source else []
        self.global_scope = SymbolTable(name="global", level=0)
        self.current_scope: SymbolTable = self.global_scope
        self.current_function: Optional[FunctionDef] = None
        self.diagnostics: List[Diagnostic] = []
        self.node_types: Dict[int, Type] = {}  # id(node) -> evaluated Type

    def _get_source_line(self, line_num: int) -> Optional[str]:
        idx = line_num - 1
        if 0 <= idx < len(self.source_lines):
            return self.source_lines[idx]
        return None

    def _error(self, message: str, node: ASTNode, length: int = 1) -> None:
        raise SemanticError(
            message=message,
            line=node.line,
            column=node.column,
            length=length,
            source_line=self._get_source_line(node.line),
        )

    def analyze(self, program: Program) -> SymbolTable:
        """Analyzes the AST and populates symbol tables and type annotations."""
        # 1. Pre-register all function signatures in global scope
        for decl in program.declarations:
            if isinstance(decl, FunctionDef):
                param_types = [from_type_name(p.type_name) for p in decl.params]
                ret_type = from_type_name(decl.return_type)
                fn_type = FunctionType(param_types=param_types, return_type=ret_type)

                sym = Symbol(
                    name=decl.name,
                    type=fn_type,
                    category="function",
                    line=decl.line,
                    column=decl.column,
                    scope_level=0,
                    scope_name="global",
                )
                if not self.global_scope.define(sym):
                    self._error(f"Function '{decl.name}' is already defined in global scope.", decl, len(decl.name))

        # 2. Analyze all top-level declarations and function bodies
        for decl in program.declarations:
            self._visit(decl)

        return self.global_scope

    def _visit(self, node: ASTNode) -> Type:
        method_name = f"_visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self._unhandled_node)
        evaluated_type = visitor(node)
        if evaluated_type:
            self.node_types[id(node)] = evaluated_type
        return evaluated_type or VOID_TYPE

    def _unhandled_node(self, node: ASTNode) -> Type:
        self._error(f"Unhandled AST node type in semantic analysis: {type(node).__name__}", node)
        return UNKNOWN_TYPE

    # -------------------------------------------------------------
    # Declarations & Functions
    # -------------------------------------------------------------
    def _visit_Program(self, node: Program) -> Type:
        for decl in node.declarations:
            self._visit(decl)
        return VOID_TYPE

    def _visit_FunctionDef(self, node: FunctionDef) -> Type:
        prev_function = self.current_function
        self.current_function = node

        # Create function scope
        fn_scope = SymbolTable(name=f"fn_{node.name}", parent=self.global_scope, level=1)
        prev_scope = self.current_scope
        self.current_scope = fn_scope

        # Define parameters in function scope
        for param in node.params:
            p_type = from_type_name(param.type_name)
            sym = Symbol(
                name=param.name,
                type=p_type,
                category="parameter",
                line=param.line,
                column=param.column,
                scope_level=fn_scope.level,
                scope_name=fn_scope.name,
            )
            if not self.current_scope.define(sym):
                self._error(f"Duplicate parameter '{param.name}' in function '{node.name}'.", param, len(param.name))

        # Visit function body block
        self._visit_block_statements(node.body.statements)

        # Restore scope and function context
        self.current_scope = prev_scope
        self.current_function = prev_function
        return VOID_TYPE

    def _visit_VarDecl(self, node: VarDecl) -> Type:
        declared_type = from_type_name(node.type_name)
        if declared_type == UNKNOWN_TYPE or declared_type == VOID_TYPE:
            self._error(f"Invalid type '{node.type_name}' for variable declaration.", node, len(node.type_name))

        if node.initializer:
            init_type = self._visit(node.initializer)
            if not check_assignment_compatibility(declared_type, init_type):
                self._error(
                    f"Type mismatch: cannot assign value of type '{init_type}' to variable '{node.name}' of type '{declared_type}'.",
                    node,
                    len(node.name),
                )

        sym = Symbol(
            name=node.name,
            type=declared_type,
            category="variable",
            line=node.line,
            column=node.column,
            scope_level=self.current_scope.level,
            scope_name=self.current_scope.name,
        )
        if not self.current_scope.define(sym):
            self._error(
                f"Variable '{node.name}' is already declared in the current scope '{self.current_scope.name}'.",
                node,
                len(node.name),
            )
        return declared_type

    def _visit_Assign(self, node: Assign) -> Type:
        sym = self.current_scope.lookup(node.name)
        if sym is None:
            self._error(f"Cannot assign to undeclared identifier '{node.name}'.", node, len(node.name))

        if sym.category in ("function", "builtin"):
            self._error(f"Cannot assign to function '{node.name}'.", node, len(node.name))

        val_type = self._visit(node.value)
        if not check_assignment_compatibility(sym.type, val_type):
            self._error(
                f"Type mismatch: cannot assign '{val_type}' to variable '{node.name}' of type '{sym.type}'.",
                node,
                len(node.name),
            )
        return sym.type

    # -------------------------------------------------------------
    # Statements & Control Flow
    # -------------------------------------------------------------
    def _visit_Block(self, node: Block) -> Type:
        block_scope = SymbolTable(
            name=f"block_{self.current_scope.level + 1}",
            parent=self.current_scope,
            level=self.current_scope.level + 1,
        )
        prev_scope = self.current_scope
        self.current_scope = block_scope

        self._visit_block_statements(node.statements)

        self.current_scope = prev_scope
        return VOID_TYPE

    def _visit_block_statements(self, statements: List[ASTNode]) -> None:
        for stmt in statements:
            self._visit(stmt)

    def _visit_IfStmt(self, node: IfStmt) -> Type:
        cond_type = self._visit(node.condition)
        if cond_type != BOOL_TYPE:
            self._error(f"'if' condition must be of type 'bool', got '{cond_type}'.", node.condition)

        self._visit(node.then_branch)
        if node.else_branch:
            self._visit(node.else_branch)
        return VOID_TYPE

    def _visit_WhileStmt(self, node: WhileStmt) -> Type:
        cond_type = self._visit(node.condition)
        if cond_type != BOOL_TYPE:
            self._error(f"'while' condition must be of type 'bool', got '{cond_type}'.", node.condition)

        self._visit(node.body)
        return VOID_TYPE

    def _visit_ReturnStmt(self, node: ReturnStmt) -> Type:
        if self.current_function is None:
            # Top-level return
            expected_ret_type = VOID_TYPE
        else:
            expected_ret_type = from_type_name(self.current_function.return_type)

        if node.value is None:
            if expected_ret_type != VOID_TYPE:
                self._error(
                    f"Function '{self.current_function.name}' expects a return value of type '{expected_ret_type}'.",
                    node,
                )
            return VOID_TYPE

        actual_type = self._visit(node.value)
        if not check_assignment_compatibility(expected_ret_type, actual_type):
            fn_name = self.current_function.name if self.current_function else "top-level"
            self._error(
                f"Return type mismatch in '{fn_name}': expected '{expected_ret_type}', but returning '{actual_type}'.",
                node,
            )
        return actual_type

    def _visit_PrintStmt(self, node: PrintStmt) -> Type:
        for arg in node.args:
            self._visit(arg)
        return VOID_TYPE

    def _visit_ExprStmt(self, node: ExprStmt) -> Type:
        return self._visit(node.expr)

    # -------------------------------------------------------------
    # Expressions
    # -------------------------------------------------------------
    def _visit_BinaryOp(self, node: BinaryOp) -> Type:
        left_type = self._visit(node.left)
        right_type = self._visit(node.right)

        result_type = get_binary_result_type(left_type, node.op, right_type)
        if result_type is None:
            self._error(
                f"Operator '{node.op}' cannot be applied to operands of types '{left_type}' and '{right_type}'.",
                node,
                len(node.op),
            )
        return result_type

    def _visit_UnaryOp(self, node: UnaryOp) -> Type:
        opnd_type = self._visit(node.operand)
        if node.op == "-":
            if not opnd_type.is_numeric():
                self._error(f"Unary '-' operator requires numeric operand, got '{opnd_type}'.", node)
            return opnd_type
        if node.op == "!":
            if opnd_type != BOOL_TYPE:
                self._error(f"Logical '!' operator requires boolean operand, got '{opnd_type}'.", node)
            return BOOL_TYPE
        self._error(f"Unknown unary operator '{node.op}'.", node)
        return UNKNOWN_TYPE

    def _visit_Literal(self, node: Literal) -> Type:
        return from_type_name(node.type_name)

    def _visit_Identifier(self, node: Identifier) -> Type:
        sym = self.current_scope.lookup(node.name)
        if sym is None:
            self._error(f"Undeclared identifier '{node.name}'.", node, len(node.name))
        return sym.type

    def _visit_CallExpr(self, node: CallExpr) -> Type:
        sym = self.current_scope.lookup_function(node.callee)
        if sym is None:
            # Check if identifier exists as non-function
            general_sym = self.current_scope.lookup(node.callee)
            if general_sym:
                self._error(f"'{node.callee}' is a {general_sym.category}, not a callable function.", node)
            self._error(f"Call to undefined function '{node.callee}()'.", node, len(node.callee))

        fn_type = sym.type
        if not isinstance(fn_type, FunctionType):
            self._error(f"'{node.callee}' is not callable.", node)

        if len(node.args) != len(fn_type.param_types):
            self._error(
                f"Function '{node.callee}' expects {len(fn_type.param_types)} arguments, but {len(node.args)} were provided.",
                node,
            )

        for i, (arg_node, param_type) in enumerate(zip(node.args, fn_type.param_types)):
            arg_type = self._visit(arg_node)
            if not check_assignment_compatibility(param_type, arg_type):
                self._error(
                    f"Argument {i+1} of '{node.callee}' expects type '{param_type}', got '{arg_type}'.",
                    arg_node,
                )

        return fn_type.return_type
