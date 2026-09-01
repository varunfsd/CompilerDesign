"""Abstract Syntax Tree (AST) node definitions for CraftLang."""

from dataclasses import dataclass
from typing import List, Optional, Any, Dict


@dataclass
class ASTNode:
    """Base AST Node with line and column information."""
    line: int
    column: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to a serializable dictionary for UI tree visualization."""
        raise NotImplementedError


@dataclass
class Program(ASTNode):
    """Root node of a CraftLang program."""
    declarations: List[ASTNode]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "Program",
            "line": self.line,
            "column": self.column,
            "declarations": [d.to_dict() for d in self.declarations],
        }


@dataclass
class Param(ASTNode):
    """Function formal parameter."""
    name: str
    type_name: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "Param",
            "name": self.name,
            "type_name": self.type_name,
            "line": self.line,
            "column": self.column,
        }


@dataclass
class Block(ASTNode):
    """Block of statements enclosed in braces."""
    statements: List[ASTNode]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "Block",
            "line": self.line,
            "column": self.column,
            "statements": [s.to_dict() for s in self.statements],
        }


@dataclass
class FunctionDef(ASTNode):
    """Function declaration node."""
    name: str
    params: List[Param]
    return_type: str
    body: Block

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "FunctionDef",
            "name": self.name,
            "params": [p.to_dict() for p in self.params],
            "return_type": self.return_type,
            "body": self.body.to_dict(),
            "line": self.line,
            "column": self.column,
        }


@dataclass
class VarDecl(ASTNode):
    """Variable declaration: let x: type = init;"""
    name: str
    type_name: str
    initializer: Optional[ASTNode]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "VarDecl",
            "name": self.name,
            "type_name": self.type_name,
            "initializer": self.initializer.to_dict() if self.initializer else None,
            "line": self.line,
            "column": self.column,
        }


@dataclass
class Assign(ASTNode):
    """Variable assignment: x = expr;"""
    name: str
    value: ASTNode

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "Assign",
            "name": self.name,
            "value": self.value.to_dict(),
            "line": self.line,
            "column": self.column,
        }


@dataclass
class IfStmt(ASTNode):
    """If statement with optional else branch."""
    condition: ASTNode
    then_branch: Block
    else_branch: Optional[Block]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "IfStmt",
            "condition": self.condition.to_dict(),
            "then_branch": self.then_branch.to_dict(),
            "else_branch": self.else_branch.to_dict() if self.else_branch else None,
            "line": self.line,
            "column": self.column,
        }


@dataclass
class WhileStmt(ASTNode):
    """While loop statement."""
    condition: ASTNode
    body: Block

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "WhileStmt",
            "condition": self.condition.to_dict(),
            "body": self.body.to_dict(),
            "line": self.line,
            "column": self.column,
        }


@dataclass
class ReturnStmt(ASTNode):
    """Return statement."""
    value: Optional[ASTNode]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "ReturnStmt",
            "value": self.value.to_dict() if self.value else None,
            "line": self.line,
            "column": self.column,
        }


@dataclass
class PrintStmt(ASTNode):
    """Print statement: print(arg1, arg2, ...);"""
    args: List[ASTNode]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "PrintStmt",
            "args": [a.to_dict() for a in self.args],
            "line": self.line,
            "column": self.column,
        }


@dataclass
class ExprStmt(ASTNode):
    """Expression statement (e.g. standalone function call)."""
    expr: ASTNode

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "ExprStmt",
            "expr": self.expr.to_dict(),
            "line": self.line,
            "column": self.column,
        }


@dataclass
class BinaryOp(ASTNode):
    """Binary operation: left op right."""
    left: ASTNode
    op: str
    right: ASTNode

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "BinaryOp",
            "op": self.op,
            "left": self.left.to_dict(),
            "right": self.right.to_dict(),
            "line": self.line,
            "column": self.column,
        }


@dataclass
class UnaryOp(ASTNode):
    """Unary operation: op operand (-x, !flag)."""
    op: str
    operand: ASTNode

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "UnaryOp",
            "op": self.op,
            "operand": self.operand.to_dict(),
            "line": self.line,
            "column": self.column,
        }


@dataclass
class Literal(ASTNode):
    """Constant literal (number, boolean, string)."""
    value: Any
    type_name: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "Literal",
            "value": self.value,
            "type_name": self.type_name,
            "line": self.line,
            "column": self.column,
        }


@dataclass
class Identifier(ASTNode):
    """Variable or reference identifier."""
    name: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "Identifier",
            "name": self.name,
            "line": self.line,
            "column": self.column,
        }


@dataclass
class CallExpr(ASTNode):
    """Function call expression: callee(arg1, arg2)."""
    callee: str
    args: List[ASTNode]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_type": "CallExpr",
            "callee": self.callee,
            "args": [a.to_dict() for a in self.args],
            "line": self.line,
            "column": self.column,
        }
