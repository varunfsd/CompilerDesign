"""AST Visualizer: Generates Mermaid diagrams, Text trees, and JSON graphs from CraftLang AST."""

from typing import Dict, Any, List
from .ast_nodes import (
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


class ASTVisualizer:
    """Provides methods to visualize CraftLang AST in various formats."""

    @classmethod
    def to_mermaid(cls, root: ASTNode) -> str:
        """Converts an AST node hierarchy into a clean Mermaid flowchart string."""
        lines = ["graph TD"]
        node_counter = 0

        def escape_label(label: str) -> str:
            return label.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')

        def traverse(node: ASTNode, parent_id: str = "") -> str:
            nonlocal node_counter
            node_counter += 1
            cur_id = f"node_{node_counter}"

            if isinstance(node, Program):
                label = 'Program'
                lines.append(f'    {cur_id}["{label}"]')
                for child in node.declarations:
                    child_id = traverse(child, cur_id)
                    lines.append(f'    {cur_id} --> {child_id}')

            elif isinstance(node, FunctionDef):
                label = f'fn {escape_label(node.name)}() -&gt; {node.return_type}'
                lines.append(f'    {cur_id}["{label}"]')
                for param in node.params:
                    p_id = traverse(param, cur_id)
                    lines.append(f'    {cur_id} -->|param| {p_id}')
                body_id = traverse(node.body, cur_id)
                lines.append(f'    {cur_id} -->|body| {body_id}')

            elif isinstance(node, Param):
                label = f'{escape_label(node.name)}: {node.type_name}'
                lines.append(f'    {cur_id}["{label}"]')

            elif isinstance(node, VarDecl):
                label = f'let {escape_label(node.name)}: {node.type_name}'
                lines.append(f'    {cur_id}["{label}"]')
                if node.initializer:
                    init_id = traverse(node.initializer, cur_id)
                    lines.append(f'    {cur_id} -->|init| {init_id}')

            elif isinstance(node, Assign):
                label = f'{escape_label(node.name)} = '
                lines.append(f'    {cur_id}["{label}"]')
                val_id = traverse(node.value, cur_id)
                lines.append(f'    {cur_id} -->|value| {val_id}')

            elif isinstance(node, IfStmt):
                label = 'if'
                lines.append(f'    {cur_id}["{label}"]')
                cond_id = traverse(node.condition, cur_id)
                lines.append(f'    {cur_id} -->|cond| {cond_id}')
                then_id = traverse(node.then_branch, cur_id)
                lines.append(f'    {cur_id} -->|then| {then_id}')
                if node.else_branch:
                    else_id = traverse(node.else_branch, cur_id)
                    lines.append(f'    {cur_id} -->|else| {else_id}')

            elif isinstance(node, WhileStmt):
                label = 'while'
                lines.append(f'    {cur_id}["{label}"]')
                cond_id = traverse(node.condition, cur_id)
                lines.append(f'    {cur_id} -->|cond| {cond_id}')
                body_id = traverse(node.body, cur_id)
                lines.append(f'    {cur_id} -->|body| {body_id}')

            elif isinstance(node, ReturnStmt):
                label = 'return'
                lines.append(f'    {cur_id}["{label}"]')
                if node.value:
                    val_id = traverse(node.value, cur_id)
                    lines.append(f'    {cur_id} --> {val_id}')

            elif isinstance(node, PrintStmt):
                label = 'print()'
                lines.append(f'    {cur_id}["{label}"]')
                for i, arg in enumerate(node.args):
                    arg_id = traverse(arg, cur_id)
                    lines.append(f'    {cur_id} -->|arg{i+1}| {arg_id}')

            elif isinstance(node, Block):
                label = '{ block }'
                lines.append(f'    {cur_id}["{label}"]')
                for stmt in node.statements:
                    stmt_id = traverse(stmt, cur_id)
                    lines.append(f'    {cur_id} --> {stmt_id}')

            elif isinstance(node, ExprStmt):
                label = 'ExprStmt'
                lines.append(f'    {cur_id}["{label}"]')
                expr_id = traverse(node.expr, cur_id)
                lines.append(f'    {cur_id} --> {expr_id}')

            elif isinstance(node, BinaryOp):
                label = f'Op: {escape_label(node.op)}'
                lines.append(f'    {cur_id}["{label}"]')
                left_id = traverse(node.left, cur_id)
                right_id = traverse(node.right, cur_id)
                lines.append(f'    {cur_id} -->|left| {left_id}')
                lines.append(f'    {cur_id} -->|right| {right_id}')

            elif isinstance(node, UnaryOp):
                label = f'Unary: {escape_label(node.op)}'
                lines.append(f'    {cur_id}["{label}"]')
                op_id = traverse(node.operand, cur_id)
                lines.append(f'    {cur_id} --> {op_id}')

            elif isinstance(node, Literal):
                label = f'{node.type_name}: {escape_label(str(node.value))}'
                lines.append(f'    {cur_id}["{label}"]')

            elif isinstance(node, Identifier):
                label = f'Id: {escape_label(node.name)}'
                lines.append(f'    {cur_id}["{label}"]')

            elif isinstance(node, CallExpr):
                label = f'Call: {escape_label(node.callee)}()'
                lines.append(f'    {cur_id}["{label}"]')
                for i, arg in enumerate(node.args):
                    arg_id = traverse(arg, cur_id)
                    lines.append(f'    {cur_id} -->|arg{i+1}| {arg_id}')

            else:
                label = type(node).__name__
                lines.append(f'    {cur_id}["{label}"]')

            return cur_id

        traverse(root)
        return "\n".join(lines)

    @classmethod
    def to_tree_json(cls, node: ASTNode) -> Dict[str, Any]:
        """Converts AST into hierarchical JSON tree format suitable for D3 or custom SVG renderers."""
        result: Dict[str, Any] = {
            "name": type(node).__name__,
            "line": node.line,
            "column": node.column,
            "children": [],
        }

        if isinstance(node, Program):
            result["name"] = "Program"
            result["children"] = [cls.to_tree_json(d) for d in node.declarations]
        elif isinstance(node, FunctionDef):
            result["name"] = f"fn {node.name}(): {node.return_type}"
            result["children"] = [cls.to_tree_json(p) for p in node.params] + [cls.to_tree_json(node.body)]
        elif isinstance(node, Param):
            result["name"] = f"param {node.name}: {node.type_name}"
        elif isinstance(node, VarDecl):
            result["name"] = f"let {node.name}: {node.type_name}"
            if node.initializer:
                result["children"] = [cls.to_tree_json(node.initializer)]
        elif isinstance(node, Assign):
            result["name"] = f"assign {node.name}"
            result["children"] = [cls.to_tree_json(node.value)]
        elif isinstance(node, IfStmt):
            result["name"] = "if"
            result["children"] = [cls.to_tree_json(node.condition), cls.to_tree_json(node.then_branch)]
            if node.else_branch:
                result["children"].append(cls.to_tree_json(node.else_branch))
        elif isinstance(node, WhileStmt):
            result["name"] = "while"
            result["children"] = [cls.to_tree_json(node.condition), cls.to_tree_json(node.body)]
        elif isinstance(node, ReturnStmt):
            result["name"] = "return"
            if node.value:
                result["children"] = [cls.to_tree_json(node.value)]
        elif isinstance(node, PrintStmt):
            result["name"] = "print"
            result["children"] = [cls.to_tree_json(a) for a in node.args]
        elif isinstance(node, Block):
            result["name"] = "block"
            result["children"] = [cls.to_tree_json(s) for s in node.statements]
        elif isinstance(node, ExprStmt):
            result["name"] = "expr_stmt"
            result["children"] = [cls.to_tree_json(node.expr)]
        elif isinstance(node, BinaryOp):
            result["name"] = f"op {node.op}"
            result["children"] = [cls.to_tree_json(node.left), cls.to_tree_json(node.right)]
        elif isinstance(node, UnaryOp):
            result["name"] = f"unary {node.op}"
            result["children"] = [cls.to_tree_json(node.operand)]
        elif isinstance(node, Literal):
            result["name"] = f"{node.type_name}: {node.value!r}"
        elif isinstance(node, Identifier):
            result["name"] = f"id: {node.name}"
        elif isinstance(node, CallExpr):
            result["name"] = f"call {node.callee}"
            result["children"] = [cls.to_tree_json(a) for a in node.args]

        return result
