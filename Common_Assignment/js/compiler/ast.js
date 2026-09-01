/**
 * ScopeLab - AST (Abstract Syntax Tree) Node Definitions
 */

export class ASTNode {
    constructor(type, line = 0, column = 0) {
        this.nodeType = type;
        this.line = line;
        this.column = column;
    }
}

export class ProgramNode extends ASTNode {
    constructor(declarations = [], line = 1, column = 1) {
        super('Program', line, column);
        this.declarations = declarations; // array of GlobalVarDecl, FunctionDecl, ProcedureDecl, etc.
    }
}

export class GlobalVarDeclNode extends ASTNode {
    constructor(name, dataType, initExpr, line, column) {
        super('GlobalVarDecl', line, column);
        this.name = name;
        this.dataType = dataType; // 'int', 'float', 'string', or null (inferred)
        this.initExpr = initExpr;
    }
}

export class ParameterNode extends ASTNode {
    constructor(name, dataType = 'int', line, column) {
        super('Parameter', line, column);
        this.name = name;
        this.dataType = dataType;
    }
}

export class FunctionDeclNode extends ASTNode {
    constructor(name, params = [], returnType = 'int', body = null, line, column) {
        super('FunctionDecl', line, column);
        this.name = name;
        this.params = params;
        this.returnType = returnType;
        this.body = body; // BlockNode
    }
}

export class ProcedureDeclNode extends ASTNode {
    constructor(name, params = [], body = null, line, column) {
        super('ProcedureDecl', line, column);
        this.name = name;
        this.params = params;
        this.returnType = 'void';
        this.body = body; // BlockNode
    }
}

export class BlockNode extends ASTNode {
    constructor(statements = [], line, column, endLine = 0) {
        super('Block', line, column);
        this.statements = statements;
        this.endLine = endLine;
    }
}

export class VarDeclNode extends ASTNode {
    constructor(name, dataType, initExpr = null, line, column) {
        super('VarDecl', line, column);
        this.name = name;
        this.dataType = dataType;
        this.initExpr = initExpr;
    }
}

export class AssignmentNode extends ASTNode {
    constructor(name, expr, line, column) {
        super('Assignment', line, column);
        this.name = name;
        this.expr = expr;
    }
}

export class ReturnNode extends ASTNode {
    constructor(expr = null, line, column) {
        super('Return', line, column);
        this.expr = expr;
    }
}

export class PrintNode extends ASTNode {
    constructor(expr, line, column) {
        super('Print', line, column);
        this.expr = expr;
    }
}

export class BinaryExprNode extends ASTNode {
    constructor(left, operator, right, line, column) {
        super('BinaryExpr', line, column);
        this.left = left;
        this.operator = operator;
        this.right = right;
    }
}

export class IdentifierNode extends ASTNode {
    constructor(name, line, column) {
        super('Identifier', line, column);
        this.name = name;
    }
}

export class LiteralNode extends ASTNode {
    constructor(value, valueType, raw, line, column) {
        super('Literal', line, column);
        this.value = value;
        this.valueType = valueType; // 'int', 'float', 'string'
        this.raw = raw;
    }
}
