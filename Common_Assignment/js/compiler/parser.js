/**
 * ScopeLab - Recursive Descent Parser with Error Recovery
 */

import { TokenType } from './tokens.js';
import {
    ProgramNode,
    GlobalVarDeclNode,
    FunctionDeclNode,
    ProcedureDeclNode,
    ParameterNode,
    BlockNode,
    VarDeclNode,
    AssignmentNode,
    ReturnNode,
    PrintNode,
    BinaryExprNode,
    IdentifierNode,
    LiteralNode
} from './ast.js';

export class Parser {
    constructor(tokens, recoveryManager) {
        this.tokens = tokens || [];
        this.cursor = 0;
        this.recoveryManager = recoveryManager;
        this.syntaxErrors = [];
    }

    parse() {
        this.cursor = 0;
        this.syntaxErrors = [];
        const declarations = [];

        while (!this.isAtEnd()) {
            try {
                const decl = this.parseTopLevelDeclaration();
                if (decl) {
                    declarations.push(decl);
                }
            } catch (err) {
                this.synchronizePanicMode(['function', 'procedure', 'global', 'int', 'float', 'string', ';', '}']);
            }
        }

        return {
            ast: new ProgramNode(declarations, 1, 1),
            syntaxErrors: this.syntaxErrors
        };
    }

    // --- Token Navigation Helpers ---

    isAtEnd() {
        return this.cursor >= this.tokens.length || this.peek().type === TokenType.EOF;
    }

    peek(offset = 0) {
        if (this.cursor + offset >= this.tokens.length) {
            return this.tokens[this.tokens.length - 1] || { type: TokenType.EOF, value: '', line: 1, column: 1 };
        }
        return this.tokens[this.cursor + offset];
    }

    previous() {
        return this.tokens[this.cursor - 1] || this.tokens[0];
    }

    advance() {
        if (!this.isAtEnd()) {
            this.cursor++;
        }
        return this.previous();
    }

    check(type, value = null) {
        if (this.isAtEnd()) return false;
        const tok = this.peek();
        if (tok.type !== type) return false;
        if (value !== null && tok.value !== value) return false;
        return true;
    }

    match(type, value = null) {
        if (this.check(type, value)) {
            this.advance();
            return true;
        }
        return false;
    }

    consume(type, value, errorMessage) {
        if (this.check(type, value)) {
            return this.advance();
        }

        const tok = this.peek();
        const err = {
            type: 'SYNTAX_ERROR',
            message: errorMessage || `Expected '${value || type}' but found '${tok.value}'`,
            line: tok.line,
            column: tok.column
        };
        this.syntaxErrors.push(err);

        // Phrase-level recovery attempt for missing semicolon
        if (value === ';' || type === TokenType.DELIMITER && value === ';') {
            this.recoveryManager.recordPhraseLevel(
                'Missing Semicolon Recovery',
                `Missing ';' detected after token '${this.previous().value}'.`,
                this.previous().line,
                this.previous().column,
                "Virtual ';' inserted for continued analysis."
            );
            // Return a virtual token
            return { type: TokenType.DELIMITER, value: ';', line: this.previous().line, column: this.previous().column };
        }

        // Phrase-level recovery attempt for missing closing brace
        if (value === '}' || type === TokenType.DELIMITER && value === '}') {
            this.recoveryManager.recordPhraseLevel(
                'Missing Closing Brace Recovery',
                `Missing '}' detected before token '${tok.value}'.`,
                tok.line,
                tok.column,
                "Virtual '}' inferred to close active block."
            );
            return { type: TokenType.DELIMITER, value: '}', line: tok.line, column: tok.column };
        }

        throw new Error(err.message);
    }

    // --- Synchronization & Recovery ---

    synchronizePanicMode(syncKeywords = [';', '}', 'function', 'procedure', 'global', 'int', 'float', 'string']) {
        const startTok = this.peek();
        let skipped = 0;

        while (!this.isAtEnd()) {
            const current = this.peek();
            if (syncKeywords.includes(current.value)) {
                if (current.value === ';') {
                    this.advance(); // consume ';' and resume
                }
                this.recoveryManager.recordPanicMode(
                    'Panic Mode Recovery',
                    `Syntax error at line ${startTok.line}:${startTok.column}. Resumed parsing.`,
                    startTok.line,
                    startTok.column,
                    current.value,
                    skipped
                );
                return;
            }
            this.advance();
            skipped++;
        }
    }

    // --- Grammar Parsers ---

    parseTopLevelDeclaration() {
        const tok = this.peek();

        // Global variable: global x = 10; or global int x = 10;
        if (tok.type === TokenType.KEYWORD && tok.value === 'global') {
            return this.parseGlobalVarDecl();
        }

        // Function: function calculate(a, b) { ... } or int function calculate(...)
        if (tok.type === TokenType.KEYWORD && tok.value === 'function') {
            return this.parseFunctionDecl();
        }

        // Procedure: procedure display(msg) { ... }
        if (tok.type === TokenType.KEYWORD && tok.value === 'procedure') {
            return this.parseProcedureDecl();
        }

        // Top level type declaration: int x = 5; or int calculate(a, b) { ... }
        if (tok.type === TokenType.TYPE) {
            const typeTok = this.advance();
            if (this.check(TokenType.KEYWORD, 'function')) {
                return this.parseFunctionDecl(typeTok.value);
            }
            if (this.check(TokenType.IDENTIFIER) && this.peek(1).value === '(') {
                return this.parseFunctionDecl(typeTok.value);
            }
            return this.parseVarDeclWithKnownType(typeTok.value);
        }

        // Global statement or top-level block
        if (tok.value === '{') {
            return this.parseBlock();
        }

        // Standalone statement at top-level
        return this.parseStatement();
    }

    parseGlobalVarDecl() {
        const globalTok = this.advance(); // 'global'
        let dataType = null;

        if (this.check(TokenType.TYPE)) {
            dataType = this.advance().value;
        }

        const nameTok = this.consume(TokenType.IDENTIFIER, null, "Expected variable name after 'global'");
        let initExpr = null;

        if (this.match(TokenType.OPERATOR, '=')) {
            initExpr = this.parseExpression();
        }

        this.consumeSemicolon();

        return new GlobalVarDeclNode(nameTok.value, dataType, initExpr, globalTok.line, globalTok.column);
    }

    parseFunctionDecl(explicitReturnType = null) {
        let funcTok;
        if (this.check(TokenType.KEYWORD, 'function')) {
            funcTok = this.advance();
        } else {
            funcTok = this.previous();
        }

        const nameTok = this.consume(TokenType.IDENTIFIER, null, "Expected function name");
        this.consume(TokenType.DELIMITER, '(', "Expected '(' after function name");

        const params = this.parseParameterList();
        this.consume(TokenType.DELIMITER, ')', "Expected ')' after parameter list");

        let returnType = explicitReturnType || 'int';
        if (this.match(TokenType.DELIMITER, ':')) {
            if (this.check(TokenType.TYPE)) {
                returnType = this.advance().value;
            }
        }

        const body = this.parseBlock();

        return new FunctionDeclNode(nameTok.value, params, returnType, body, funcTok.line, funcTok.column);
    }

    parseProcedureDecl() {
        const procTok = this.advance(); // 'procedure'
        const nameTok = this.consume(TokenType.IDENTIFIER, null, "Expected procedure name");

        this.consume(TokenType.DELIMITER, '(', "Expected '(' after procedure name");
        const params = this.parseParameterList();
        this.consume(TokenType.DELIMITER, ')', "Expected ')' after parameter list");

        const body = this.parseBlock();

        return new ProcedureDeclNode(nameTok.value, params, body, procTok.line, procTok.column);
    }

    parseParameterList() {
        const params = [];
        if (this.check(TokenType.DELIMITER, ')')) {
            return params;
        }

        do {
            let paramType = 'int'; // default if untyped (e.g. calculate(a, b))
            if (this.check(TokenType.TYPE)) {
                paramType = this.advance().value;
            }

            if (this.check(TokenType.IDENTIFIER)) {
                const idTok = this.advance();
                params.push(new ParameterNode(idTok.value, paramType, idTok.line, idTok.column));
            } else {
                this.syntaxErrors.push({
                    type: 'SYNTAX_ERROR',
                    message: `Expected parameter identifier at line ${this.peek().line}`,
                    line: this.peek().line,
                    column: this.peek().column
                });
                break;
            }
        } while (this.match(TokenType.DELIMITER, ','));

        return params;
    }

    parseBlock() {
        const startTok = this.consume(TokenType.DELIMITER, '{', "Expected '{' to start block");
        const statements = [];

        while (!this.isAtEnd() && !this.check(TokenType.DELIMITER, '}')) {
            try {
                const stmt = this.parseStatement();
                if (stmt) {
                    statements.push(stmt);
                }
            } catch (err) {
                this.synchronizePanicMode([';', '}', 'int', 'float', 'string', 'return', 'print', '{']);
            }
        }

        const endTok = this.consume(TokenType.DELIMITER, '}', "Expected '}' at end of block");
        return new BlockNode(statements, startTok.line, startTok.column, endTok ? endTok.line : startTok.line);
    }

    parseStatement() {
        const tok = this.peek();

        // Nested Block
        if (tok.value === '{') {
            return this.parseBlock();
        }

        // Variable declaration: int x = 5;
        if (tok.type === TokenType.TYPE) {
            const typeTok = this.advance();
            return this.parseVarDeclWithKnownType(typeTok.value);
        }

        // Return statement: return x + y;
        if (tok.type === TokenType.KEYWORD && tok.value === 'return') {
            return this.parseReturnStatement();
        }

        // Print statement: print x + msg;
        if (tok.type === TokenType.KEYWORD && tok.value === 'print') {
            return this.parsePrintStatement();
        }

        // Identifier assignment or expression: x = 10;
        if (tok.type === TokenType.IDENTIFIER) {
            if (this.peek(1).value === '=') {
                return this.parseAssignment();
            }
        }

        // Unrecognized or unknown token at statement boundary -> trigger panic mode
        if (tok.type === TokenType.UNKNOWN || (!['(', '{', ';'].includes(tok.value) && tok.type !== TokenType.IDENTIFIER && tok.type !== TokenType.INT_LITERAL && tok.type !== TokenType.FLOAT_LITERAL && tok.type !== TokenType.STRING_LITERAL)) {
            const badTok = this.advance();
            this.syntaxErrors.push({
                type: 'SYNTAX_ERROR',
                message: `Unexpected token '${badTok.value}' at statement start line ${badTok.line}`,
                line: badTok.line,
                column: badTok.column
            });
            this.synchronizePanicMode([';', '}', 'int', 'float', 'string', 'return', 'print', '{']);
            return null;
        }

        // Standalone expression statement
        const expr = this.parseExpression();
        this.consumeSemicolon();
        return expr;
    }

    parseVarDeclWithKnownType(dataType) {
        const idTok = this.consume(TokenType.IDENTIFIER, null, `Expected variable name after '${dataType}'`);
        let initExpr = null;

        if (this.match(TokenType.OPERATOR, '=')) {
            initExpr = this.parseExpression();
        }

        this.consumeSemicolon();

        return new VarDeclNode(idTok.value, dataType, initExpr, idTok.line, idTok.column);
    }

    parseAssignment() {
        const idTok = this.advance(); // identifier
        this.consume(TokenType.OPERATOR, '=', "Expected '=' in assignment");
        const expr = this.parseExpression();
        this.consumeSemicolon();

        return new AssignmentNode(idTok.value, expr, idTok.line, idTok.column);
    }

    parseReturnStatement() {
        const retTok = this.advance(); // 'return'
        let expr = null;

        if (!this.check(TokenType.DELIMITER, ';') && !this.check(TokenType.DELIMITER, '}')) {
            expr = this.parseExpression();
        }

        this.consumeSemicolon();
        return new ReturnNode(expr, retTok.line, retTok.column);
    }

    parsePrintStatement() {
        const printTok = this.advance(); // 'print'
        const expr = this.parseExpression();
        this.consumeSemicolon();
        return new PrintNode(expr, printTok.line, printTok.column);
    }

    consumeSemicolon() {
        if (this.check(TokenType.DELIMITER, ';')) {
            this.advance();
            return;
        }

        // Check if next token is on next line or closing brace -> trigger phrase-level recovery
        const prev = this.previous();
        const curr = this.peek();

        const isLineEndOrBrace = curr.line > prev.line || curr.value === '}' || this.isAtEnd();
        if (isLineEndOrBrace) {
            this.recoveryManager.recordPhraseLevel(
                'Missing Semicolon Recovery',
                `Missing ';' detected after statement at line ${prev.line}.`,
                prev.line,
                prev.column,
                "Virtual ';' inserted for continued analysis."
            );
            this.syntaxErrors.push({
                type: 'SYNTAX_WARNING',
                message: `Missing ';' after statement at line ${prev.line}`,
                line: prev.line,
                column: prev.column
            });
            return;
        }

        // Otherwise enforce consume
        this.consume(TokenType.DELIMITER, ';', "Expected ';' after statement");
    }

    // --- Expression Parsing (Precedence Climbing) ---

    parseExpression() {
        return this.parseAdditive();
    }

    parseAdditive() {
        let left = this.parseMultiplicative();

        while (this.match(TokenType.OPERATOR, '+') || this.match(TokenType.OPERATOR, '-')) {
            const opTok = this.previous();
            const right = this.parseMultiplicative();
            left = new BinaryExprNode(left, opTok.value, right, opTok.line, opTok.column);
        }

        return left;
    }

    parseMultiplicative() {
        let left = this.parsePrimary();

        while (this.match(TokenType.OPERATOR, '*') || this.match(TokenType.OPERATOR, '/') || this.match(TokenType.OPERATOR, '%')) {
            const opTok = this.previous();
            const right = this.parsePrimary();
            left = new BinaryExprNode(left, opTok.value, right, opTok.line, opTok.column);
        }

        return left;
    }

    parsePrimary() {
        const tok = this.peek();

        // Integer Literal
        if (tok.type === TokenType.INT_LITERAL) {
            this.advance();
            return new LiteralNode(parseInt(tok.value, 10), 'int', tok.value, tok.line, tok.column);
        }

        // Float Literal
        if (tok.type === TokenType.FLOAT_LITERAL) {
            this.advance();
            return new LiteralNode(parseFloat(tok.value), 'float', tok.value, tok.line, tok.column);
        }

        // String Literal
        if (tok.type === TokenType.STRING_LITERAL) {
            this.advance();
            return new LiteralNode(tok.value, 'string', `"${tok.value}"`, tok.line, tok.column);
        }

        // Identifier
        if (tok.type === TokenType.IDENTIFIER) {
            this.advance();
            return new IdentifierNode(tok.value, tok.line, tok.column);
        }

        // Grouped Expression '(' Expr ')'
        if (this.match(TokenType.DELIMITER, '(')) {
            const expr = this.parseExpression();
            this.consume(TokenType.DELIMITER, ')', "Expected ')' after expression");
            return expr;
        }

        // Error recovery in expression
        this.syntaxErrors.push({
            type: 'SYNTAX_ERROR',
            message: `Unexpected token '${tok.value}' in expression at line ${tok.line}`,
            line: tok.line,
            column: tok.column
        });
        this.advance(); // skip bad token
        return new LiteralNode(0, 'int', '0', tok.line, tok.column);
    }
}
