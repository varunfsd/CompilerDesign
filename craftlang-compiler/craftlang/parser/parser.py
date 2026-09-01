"""Recursive-descent parser with operator precedence climbing for CraftLang."""

from typing import List, Optional, Tuple, Any
from ..lexer.tokens import TokenType, Token
from ..errors import ParserError
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


class Parser:
    """Parses a stream of CraftLang tokens into an Abstract Syntax Tree (AST)."""

    def __init__(self, tokens: List[Token], source: Optional[str] = None):
        self.tokens: List[Token] = tokens
        self.pos: int = 0
        self.source_lines: List[str] = source.splitlines() if source else []

    def _get_source_line(self, line_num: int) -> Optional[str]:
        idx = line_num - 1
        if 0 <= idx < len(self.source_lines):
            return self.source_lines[idx]
        return None

    def _peek(self, offset: int = 0) -> Token:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]  # Return EOF token

    def _current(self) -> Token:
        return self._peek(0)

    def _is_at_end(self) -> bool:
        return self._current().type == TokenType.EOF

    def _advance(self) -> Token:
        tok = self._current()
        if not self._is_at_end():
            self.pos += 1
        return tok

    def _check(self, tok_type: TokenType) -> bool:
        if self._is_at_end():
            return False
        return self._current().type == tok_type

    def _match(self, *types: TokenType) -> bool:
        for t in types:
            if self._check(t):
                self._advance()
                return True
        return False

    def _consume(self, tok_type: TokenType, err_msg: str) -> Token:
        if self._check(tok_type):
            return self._advance()
        current = self._current()
        raise ParserError(
            f"{err_msg}. Got '{current.raw or current.type.name}' instead.",
            line=current.line,
            column=current.column,
            length=max(1, current.length),
            source_line=self._get_source_line(current.line),
        )

    # -------------------------------------------------------------
    # Entry Point
    # -------------------------------------------------------------
    def parse(self) -> Program:
        """Parses the entire token stream into a Program AST node."""
        declarations: List[ASTNode] = []
        first_tok = self._current()
        start_line = first_tok.line if first_tok else 1
        start_col = first_tok.column if first_tok else 1

        while not self._is_at_end():
            decl = self._parse_declaration()
            if decl is not None:
                declarations.append(decl)

        return Program(line=start_line, column=start_col, declarations=declarations)

    # -------------------------------------------------------------
    # Declarations
    # -------------------------------------------------------------
    def _parse_declaration(self) -> ASTNode:
        if self._check(TokenType.FN):
            return self._parse_function_def()
        if self._check(TokenType.LET):
            return self._parse_var_decl()
        return self._parse_statement()

    def _parse_function_def(self) -> FunctionDef:
        fn_tok = self._consume(TokenType.FN, "Expected 'fn' keyword")
        name_tok = self._consume(TokenType.IDENTIFIER, "Expected function name")
        
        self._consume(TokenType.LPAREN, "Expected '(' after function name")
        params: List[Param] = []
        if not self._check(TokenType.RPAREN):
            while True:
                p_name_tok = self._consume(TokenType.IDENTIFIER, "Expected parameter name")
                self._consume(TokenType.COLON, "Expected ':' after parameter name")
                p_type = self._parse_type()
                params.append(Param(line=p_name_tok.line, column=p_name_tok.column, name=p_name_tok.raw, type_name=p_type))
                if not self._match(TokenType.COMMA):
                    break
        self._consume(TokenType.RPAREN, "Expected ')' after parameters")

        return_type = "void"
        if self._match(TokenType.ARROW):
            return_type = self._parse_type()

        body = self._parse_block()
        return FunctionDef(
            line=fn_tok.line,
            column=fn_tok.column,
            name=name_tok.raw,
            params=params,
            return_type=return_type,
            body=body,
        )

    def _parse_var_decl(self) -> VarDecl:
        let_tok = self._consume(TokenType.LET, "Expected 'let'")
        name_tok = self._consume(TokenType.IDENTIFIER, "Expected variable name")
        self._consume(TokenType.COLON, "Expected ':' after variable name")
        type_name = self._parse_type()

        initializer: Optional[ASTNode] = None
        if self._match(TokenType.ASSIGN):
            initializer = self._parse_expression()

        self._consume(TokenType.SEMICOLON, "Expected ';' after variable declaration")
        return VarDecl(
            line=let_tok.line,
            column=let_tok.column,
            name=name_tok.raw,
            type_name=type_name,
            initializer=initializer,
        )

    def _parse_type(self) -> str:
        current = self._current()
        type_tokens = {
            TokenType.TYPE_INT: "int",
            TokenType.TYPE_FLOAT: "float",
            TokenType.TYPE_BOOL: "bool",
            TokenType.TYPE_STRING: "string",
            TokenType.TYPE_VOID: "void",
        }
        if current.type in type_tokens:
            self._advance()
            return type_tokens[current.type]
        raise ParserError(
            f"Expected type name (int, float, bool, string, void), got '{current.raw}'",
            line=current.line,
            column=current.column,
            length=max(1, current.length),
            source_line=self._get_source_line(current.line),
        )

    # -------------------------------------------------------------
    # Statements
    # -------------------------------------------------------------
    def _parse_statement(self) -> ASTNode:
        if self._check(TokenType.LBRACE):
            return self._parse_block()
        if self._check(TokenType.IF):
            return self._parse_if_stmt()
        if self._check(TokenType.WHILE):
            return self._parse_while_stmt()
        if self._check(TokenType.RETURN):
            return self._parse_return_stmt()
        if self._check(TokenType.PRINT):
            return self._parse_print_stmt()
        return self._parse_assignment_or_expr()

    def _parse_block(self) -> Block:
        lbrace = self._consume(TokenType.LBRACE, "Expected '{'")
        statements: List[ASTNode] = []
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            decl = self._parse_declaration()
            if decl is not None:
                statements.append(decl)
        self._consume(TokenType.RBRACE, "Expected '}' at end of block")
        return Block(line=lbrace.line, column=lbrace.column, statements=statements)

    def _parse_if_stmt(self) -> IfStmt:
        if_tok = self._consume(TokenType.IF, "Expected 'if'")
        has_paren = self._match(TokenType.LPAREN)
        condition = self._parse_expression()
        if has_paren:
            self._consume(TokenType.RPAREN, "Expected ')' after if condition")

        then_branch = self._parse_block()
        else_branch: Optional[Block] = None
        if self._match(TokenType.ELSE):
            if self._check(TokenType.IF):
                # else if chained
                nested_if = self._parse_if_stmt()
                else_branch = Block(line=nested_if.line, column=nested_if.column, statements=[nested_if])
            else:
                else_branch = self._parse_block()

        return IfStmt(
            line=if_tok.line,
            column=if_tok.column,
            condition=condition,
            then_branch=then_branch,
            else_branch=else_branch,
        )

    def _parse_while_stmt(self) -> WhileStmt:
        while_tok = self._consume(TokenType.WHILE, "Expected 'while'")
        has_paren = self._match(TokenType.LPAREN)
        condition = self._parse_expression()
        if has_paren:
            self._consume(TokenType.RPAREN, "Expected ')' after while condition")

        body = self._parse_block()
        return WhileStmt(
            line=while_tok.line,
            column=while_tok.column,
            condition=condition,
            body=body,
        )

    def _parse_return_stmt(self) -> ReturnStmt:
        ret_tok = self._consume(TokenType.RETURN, "Expected 'return'")
        value: Optional[ASTNode] = None
        if not self._check(TokenType.SEMICOLON):
            value = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "Expected ';' after return statement")
        return ReturnStmt(line=ret_tok.line, column=ret_tok.column, value=value)

    def _parse_print_stmt(self) -> PrintStmt:
        print_tok = self._consume(TokenType.PRINT, "Expected 'print'")
        self._consume(TokenType.LPAREN, "Expected '(' after 'print'")
        args: List[ASTNode] = []
        if not self._check(TokenType.RPAREN):
            while True:
                args.append(self._parse_expression())
                if not self._match(TokenType.COMMA):
                    break
        self._consume(TokenType.RPAREN, "Expected ')' after print arguments")
        self._consume(TokenType.SEMICOLON, "Expected ';' after print statement")
        return PrintStmt(line=print_tok.line, column=print_tok.column, args=args)

    def _parse_assignment_or_expr(self) -> ASTNode:
        # Check if this is an assignment: IDENTIFIER = expr;
        if self._check(TokenType.IDENTIFIER) and self._peek(1).type == TokenType.ASSIGN:
            name_tok = self._advance()
            self._advance()  # consume '='
            val_expr = self._parse_expression()
            self._consume(TokenType.SEMICOLON, "Expected ';' after assignment")
            return Assign(line=name_tok.line, column=name_tok.column, name=name_tok.raw, value=val_expr)

        expr = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "Expected ';' after expression")
        return ExprStmt(line=expr.line, column=expr.column, expr=expr)

    # -------------------------------------------------------------
    # Expressions (Precedence Climbing)
    # -------------------------------------------------------------
    def _parse_expression(self) -> ASTNode:
        return self._parse_logical_or()

    def _parse_logical_or(self) -> ASTNode:
        left = self._parse_logical_and()
        while self._match(TokenType.OR):
            op = "||"
            op_tok = self.tokens[self.pos - 1]
            right = self._parse_logical_and()
            left = BinaryOp(line=op_tok.line, column=op_tok.column, left=left, op=op, right=right)
        return left

    def _parse_logical_and(self) -> ASTNode:
        left = self._parse_equality()
        while self._match(TokenType.AND):
            op = "&&"
            op_tok = self.tokens[self.pos - 1]
            right = self._parse_equality()
            left = BinaryOp(line=op_tok.line, column=op_tok.column, left=left, op=op, right=right)
        return left

    def _parse_equality(self) -> ASTNode:
        left = self._parse_relational()
        while self._match(TokenType.EQ_EQ, TokenType.BANG_EQ):
            op_tok = self.tokens[self.pos - 1]
            op = "==" if op_tok.type == TokenType.EQ_EQ else "!="
            right = self._parse_relational()
            left = BinaryOp(line=op_tok.line, column=op_tok.column, left=left, op=op, right=right)
        return left

    def _parse_relational(self) -> ASTNode:
        left = self._parse_additive()
        while self._match(TokenType.LT, TokenType.LTE, TokenType.GT, TokenType.GTE):
            op_tok = self.tokens[self.pos - 1]
            op_map = {
                TokenType.LT: "<",
                TokenType.LTE: "<=",
                TokenType.GT: ">",
                TokenType.GTE: ">=",
            }
            op = op_map[op_tok.type]
            right = self._parse_additive()
            left = BinaryOp(line=op_tok.line, column=op_tok.column, left=left, op=op, right=right)
        return left

    def _parse_additive(self) -> ASTNode:
        left = self._parse_multiplicative()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op_tok = self.tokens[self.pos - 1]
            op = "+" if op_tok.type == TokenType.PLUS else "-"
            right = self._parse_multiplicative()
            left = BinaryOp(line=op_tok.line, column=op_tok.column, left=left, op=op, right=right)
        return left

    def _parse_multiplicative(self) -> ASTNode:
        left = self._parse_unary()
        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op_tok = self.tokens[self.pos - 1]
            op_map = {
                TokenType.STAR: "*",
                TokenType.SLASH: "/",
                TokenType.PERCENT: "%",
            }
            op = op_map[op_tok.type]
            right = self._parse_unary()
            left = BinaryOp(line=op_tok.line, column=op_tok.column, left=left, op=op, right=right)
        return left

    def _parse_unary(self) -> ASTNode:
        if self._match(TokenType.MINUS, TokenType.BANG):
            op_tok = self.tokens[self.pos - 1]
            op = "-" if op_tok.type == TokenType.MINUS else "!"
            operand = self._parse_unary()
            return UnaryOp(line=op_tok.line, column=op_tok.column, op=op, operand=operand)
        return self._parse_primary()

    def _parse_primary(self) -> ASTNode:
        tok = self._current()

        if self._match(TokenType.INT_LIT):
            return Literal(line=tok.line, column=tok.column, value=tok.value, type_name="int")

        if self._match(TokenType.FLOAT_LIT):
            return Literal(line=tok.line, column=tok.column, value=tok.value, type_name="float")

        if self._match(TokenType.STRING_LIT):
            return Literal(line=tok.line, column=tok.column, value=tok.value, type_name="string")

        if self._match(TokenType.BOOL_LIT):
            return Literal(line=tok.line, column=tok.column, value=tok.value, type_name="bool")

        if self._match(TokenType.IDENTIFIER):
            name = tok.raw
            # Check for function call
            if self._match(TokenType.LPAREN):
                args: List[ASTNode] = []
                if not self._check(TokenType.RPAREN):
                    while True:
                        args.append(self._parse_expression())
                        if not self._match(TokenType.COMMA):
                            break
                self._consume(TokenType.RPAREN, "Expected ')' after function arguments")
                return CallExpr(line=tok.line, column=tok.column, callee=name, args=args)
            return Identifier(line=tok.line, column=tok.column, name=name)

        if self._match(TokenType.LPAREN):
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr

        raise ParserError(
            f"Unexpected token in expression: '{tok.raw or tok.type.name}'",
            line=tok.line,
            column=tok.column,
            length=max(1, tok.length),
            source_line=self._get_source_line(tok.line),
        )
