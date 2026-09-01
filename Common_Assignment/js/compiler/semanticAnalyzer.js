/**
 * ScopeLab - Semantic Analyzer and Type Checker
 */

import { ScopeType } from './scope.js';

export class SemanticDiagnostic {
    constructor({
        severity = 'ERROR', // 'ERROR' | 'WARNING' | 'INFO'
        category = 'Scope Error',
        title,
        message,
        line = 1,
        column = 1,
        symbolName = null,
        declaredInScope = null,
        declaredAtLevel = null,
        usedInScope = null,
        usedAtLevel = null,
        recoveryTechnique = null,
        suggestedFix = null
    }) {
        this.id = 'diag_' + Math.random().toString(36).substr(2, 9);
        this.severity = severity;
        this.category = category;
        this.title = title;
        this.message = message;
        this.line = line;
        this.column = column;
        this.symbolName = symbolName;
        this.declaredInScope = declaredInScope;
        this.declaredAtLevel = declaredAtLevel;
        this.usedInScope = usedInScope;
        this.usedAtLevel = usedAtLevel;
        this.recoveryTechnique = recoveryTechnique;
        this.suggestedFix = suggestedFix;
    }
}

export class ResolutionRecord {
    constructor({
        identifier,
        usageLine,
        usageColumn,
        usageScope,
        resolved,
        resolvedSymbol = null,
        lookupPath = [],
        status = 'SUCCESS', // 'SUCCESS' | 'SCOPE_VIOLATION' | 'UNDECLARED'
        declaredScope = null,
        note = ''
    }) {
        this.id = 'res_' + Math.random().toString(36).substr(2, 9);
        this.identifier = identifier;
        this.usageLine = usageLine;
        this.usageColumn = usageColumn;
        this.usageScope = usageScope;
        this.resolved = resolved;
        this.resolvedSymbol = resolvedSymbol;
        this.lookupPath = lookupPath;
        this.status = status;
        this.declaredScope = declaredScope;
        this.note = note;
    }
}

export class SemanticAnalyzer {
    constructor(scopeManager, symbolTable, recoveryManager) {
        this.scopeManager = scopeManager;
        this.symbolTable = symbolTable;
        this.recoveryManager = recoveryManager;
        this.diagnostics = [];
        this.resolutions = [];
        this.currentFunction = null;
    }

    analyze(ast) {
        this.diagnostics = [];
        this.resolutions = [];
        this.scopeManager.reset();
        this.symbolTable.reset();

        if (!ast) return this.getResult();

        // Pass 1: Semantic Analysis and Symbol Table Construction
        this.visitProgram(ast);

        // Pass 2: Unused Variable Warnings
        this.checkUnusedVariables();

        return this.getResult();
    }

    getResult() {
        return {
            diagnostics: this.diagnostics,
            resolutions: this.resolutions,
            symbolTable: this.symbolTable.getAllSymbols(),
            scopes: this.scopeManager.getAllScopes(),
            recoveryEvents: this.recoveryManager.getEvents()
        };
    }

    // --- AST Visitors ---

    visitProgram(node) {
        for (const decl of node.declarations) {
            this.visitDeclaration(decl);
        }
    }

    visitDeclaration(decl) {
        if (!decl) return;

        switch (decl.nodeType) {
            case 'GlobalVarDecl':
                this.visitGlobalVarDecl(decl);
                break;
            case 'FunctionDecl':
                this.visitFunctionDecl(decl);
                break;
            case 'ProcedureDecl':
                this.visitProcedureDecl(decl);
                break;
            case 'VarDecl':
                this.visitVarDecl(decl);
                break;
            case 'Block':
                this.visitBlock(decl, 'Block Scope');
                break;
            case 'Assignment':
                this.visitAssignment(decl);
                break;
            case 'Return':
                this.visitReturn(decl);
                break;
            case 'Print':
                this.visitPrint(decl);
                break;
            default:
                if (decl.nodeType === 'BinaryExpr' || decl.nodeType === 'Identifier' || decl.nodeType === 'Literal') {
                    this.inferExpressionType(decl);
                }
                break;
        }
    }

    visitGlobalVarDecl(node) {
        const currentScope = this.scopeManager.currentScope;
        let inferredType = node.dataType;

        if (node.initExpr) {
            const exprType = this.inferExpressionType(node.initExpr);
            if (!inferredType) {
                inferredType = exprType;
            } else if (inferredType !== exprType && !this.areTypesCompatible(inferredType, exprType)) {
                this.addDiagnostic({
                    severity: 'ERROR',
                    category: 'Type Mismatch',
                    title: 'Type Mismatch',
                    message: `Variable '${node.name}' expects type ${inferredType} but the expression has type ${exprType}.`,
                    line: node.line,
                    column: node.column,
                    symbolName: node.name,
                    recoveryTechnique: 'Phrase-Level Recovery: Coerced expression type for semantic analysis.',
                    suggestedFix: `Ensure value assigned matches the declared type '${inferredType}'.`
                });
            }
        }

        if (!inferredType) inferredType = 'int'; // default

        // Check redeclaration in current scope
        if (currentScope.lookupLocal(node.name)) {
            this.addDiagnostic({
                severity: 'ERROR',
                category: 'Redeclaration Error',
                title: 'Redeclaration Error',
                message: `'${node.name}' has already been declared in this scope.`,
                line: node.line,
                column: node.column,
                symbolName: node.name,
                recoveryTechnique: 'Phrase-Level Recovery: Retained previous definition in symbol table.',
                suggestedFix: `Rename variable '${node.name}' or remove duplicate declaration.`
            });
            return;
        }

        const symbol = this.symbolTable.addSymbol({
            name: node.name,
            type: inferredType,
            scopeName: currentScope.name,
            scopeLevel: currentScope.level,
            scopeId: currentScope.id,
            isParameter: false,
            declarationLine: node.line,
            declarationCol: node.column
        });

        currentScope.define(symbol);
    }

    visitFunctionDecl(node) {
        const currentScope = this.scopeManager.currentScope;

        // Check redeclaration of function name in global scope
        if (currentScope.lookupLocal(node.name)) {
            this.addDiagnostic({
                severity: 'ERROR',
                category: 'Redeclaration Error',
                title: 'Redeclaration Error',
                message: `Function '${node.name}' has already been declared in this scope.`,
                line: node.line,
                column: node.column,
                symbolName: node.name,
                suggestedFix: `Use a unique name for function '${node.name}'.`
            });
        } else {
            // Function symbol in enclosing scope
            const funcSymbol = this.symbolTable.addSymbol({
                name: node.name,
                type: `function(${node.params.map(p => p.dataType).join(', ')}): ${node.returnType}`,
                scopeName: currentScope.name,
                scopeLevel: currentScope.level,
                scopeId: currentScope.id,
                isParameter: false,
                declarationLine: node.line,
                declarationCol: node.column
            });
            currentScope.define(funcSymbol);
        }

        // Enter function scope
        const funcScope = this.scopeManager.enterScope(`${node.name}()`, ScopeType.FUNCTION, node.line);
        const prevFunc = this.currentFunction;
        this.currentFunction = { name: node.name, returnType: node.returnType, isProcedure: false, line: node.line };

        // Register parameters
        for (const param of node.params) {
            if (funcScope.lookupLocal(param.name)) {
                this.addDiagnostic({
                    severity: 'ERROR',
                    category: 'Redeclaration Error',
                    title: 'Duplicate Parameter',
                    message: `Parameter '${param.name}' is declared multiple times in function '${node.name}'.`,
                    line: param.line,
                    column: param.column,
                    symbolName: param.name
                });
            } else {
                const paramSymbol = this.symbolTable.addSymbol({
                    name: param.name,
                    type: param.dataType || 'int',
                    scopeName: funcScope.name,
                    scopeLevel: funcScope.level,
                    scopeId: funcScope.id,
                    isParameter: true,
                    declarationLine: param.line,
                    declarationCol: param.column
                });
                funcScope.define(paramSymbol);
            }
        }

        // Visit function body statements
        if (node.body && node.body.statements) {
            for (const stmt of node.body.statements) {
                this.visitDeclaration(stmt);
            }
            funcScope.endLine = node.body.endLine || node.line;
        }

        this.scopeManager.exitScope(funcScope.endLine);
        this.currentFunction = prevFunc;
    }

    visitProcedureDecl(node) {
        const currentScope = this.scopeManager.currentScope;

        if (currentScope.lookupLocal(node.name)) {
            this.addDiagnostic({
                severity: 'ERROR',
                category: 'Redeclaration Error',
                title: 'Redeclaration Error',
                message: `Procedure '${node.name}' has already been declared in this scope.`,
                line: node.line,
                column: node.column,
                symbolName: node.name
            });
        } else {
            const procSymbol = this.symbolTable.addSymbol({
                name: node.name,
                type: `procedure(${node.params.map(p => p.dataType).join(', ')})`,
                scopeName: currentScope.name,
                scopeLevel: currentScope.level,
                scopeId: currentScope.id,
                isParameter: false,
                declarationLine: node.line,
                declarationCol: node.column
            });
            currentScope.define(procSymbol);
        }

        const procScope = this.scopeManager.enterScope(`${node.name}()`, ScopeType.PROCEDURE, node.line);
        const prevFunc = this.currentFunction;
        this.currentFunction = { name: node.name, returnType: 'void', isProcedure: true, line: node.line };

        for (const param of node.params) {
            if (procScope.lookupLocal(param.name)) {
                this.addDiagnostic({
                    severity: 'ERROR',
                    category: 'Redeclaration Error',
                    title: 'Duplicate Parameter',
                    message: `Parameter '${param.name}' is declared multiple times in procedure '${node.name}'.`,
                    line: param.line,
                    column: param.column,
                    symbolName: param.name
                });
            } else {
                const paramSymbol = this.symbolTable.addSymbol({
                    name: param.name,
                    type: param.dataType || 'string',
                    scopeName: procScope.name,
                    scopeLevel: procScope.level,
                    scopeId: procScope.id,
                    isParameter: true,
                    declarationLine: param.line,
                    declarationCol: param.column
                });
                procScope.define(paramSymbol);
            }
        }

        if (node.body && node.body.statements) {
            for (const stmt of node.body.statements) {
                this.visitDeclaration(stmt);
            }
            procScope.endLine = node.body.endLine || node.line;
        }

        this.scopeManager.exitScope(procScope.endLine);
        this.currentFunction = prevFunc;
    }

    visitBlock(node, blockName = 'Block Scope') {
        const blockScope = this.scopeManager.enterScope(blockName, ScopeType.BLOCK, node.line);

        for (const stmt of node.statements) {
            this.visitDeclaration(stmt);
        }

        blockScope.endLine = node.endLine || node.line;
        this.scopeManager.exitScope(blockScope.endLine);
    }

    visitVarDecl(node) {
        const currentScope = this.scopeManager.currentScope;
        const expectedType = node.dataType;

        if (node.initExpr) {
            const actualType = this.inferExpressionType(node.initExpr);
            if (actualType && !this.areTypesCompatible(expectedType, actualType)) {
                this.addDiagnostic({
                    severity: 'ERROR',
                    category: 'Type Mismatch',
                    title: 'Type Mismatch',
                    message: `Variable '${node.name}' expects type ${expectedType} but the expression has type ${actualType}.`,
                    line: node.line,
                    column: node.column,
                    symbolName: node.name,
                    recoveryTechnique: 'Phrase-Level Recovery: Variable declared with requested type despite initializer mismatch.',
                    suggestedFix: `Change expression to evaluate to type '${expectedType}' or change declaration type.`
                });
            }
        }

        // Check redeclaration in current scope
        if (currentScope.lookupLocal(node.name)) {
            this.addDiagnostic({
                severity: 'ERROR',
                category: 'Redeclaration Error',
                title: 'Redeclaration Error',
                message: `'${node.name}' has already been declared in this scope.`,
                line: node.line,
                column: node.column,
                symbolName: node.name,
                declaredInScope: currentScope.name,
                declaredAtLevel: currentScope.level,
                recoveryTechnique: 'Phrase-Level Recovery: Retained previous definition in symbol table.',
                suggestedFix: `Remove redundant declaration or use a different variable name.`
            });
            return;
        }

        const symbol = this.symbolTable.addSymbol({
            name: node.name,
            type: expectedType,
            scopeName: currentScope.name,
            scopeLevel: currentScope.level,
            scopeId: currentScope.id,
            isParameter: false,
            declarationLine: node.line,
            declarationCol: node.column
        });

        currentScope.define(symbol);
    }

    visitAssignment(node) {
        const resolved = this.resolveIdentifier(node.name, node.line, node.column, 'write');
        const exprType = this.inferExpressionType(node.expr);

        if (resolved && exprType) {
            if (!this.areTypesCompatible(resolved.type, exprType)) {
                this.addDiagnostic({
                    severity: 'ERROR',
                    category: 'Type Mismatch',
                    title: 'Assignment Type Mismatch',
                    message: `Cannot assign expression of type '${exprType}' to variable '${node.name}' of type '${resolved.type}'.`,
                    line: node.line,
                    column: node.column,
                    symbolName: node.name,
                    recoveryTechnique: 'Phrase-Level Recovery: Analysis resumed assuming assignment type coercion.',
                    suggestedFix: `Convert expression value to '${resolved.type}'.`
                });
            }
        }
    }

    visitReturn(node) {
        if (!this.currentFunction) {
            this.addDiagnostic({
                severity: 'ERROR',
                category: 'Semantic Error',
                title: 'Return Outside Function',
                message: `'return' statement cannot appear outside a function or procedure.`,
                line: node.line,
                column: node.column,
                suggestedFix: `Wrap the return statement inside a function definition.`
            });
            return;
        }

        if (this.currentFunction.isProcedure) {
            if (node.expr) {
                this.addDiagnostic({
                    severity: 'ERROR',
                    category: 'Return Type Error',
                    title: 'Return Value in Procedure',
                    message: `Procedure '${this.currentFunction.name}' has void return type and cannot return a value.`,
                    line: node.line,
                    column: node.column,
                    recoveryTechnique: 'Phrase-Level Recovery: Treated as empty return statement.',
                    suggestedFix: `Change procedure '${this.currentFunction.name}' to a function or remove the return expression.`
                });
            }
            return;
        }

        // Function return type checking
        if (node.expr) {
            const retExprType = this.inferExpressionType(node.expr);
            const expectedType = this.currentFunction.returnType;

            if (retExprType && !this.areTypesCompatible(expectedType, retExprType)) {
                this.addDiagnostic({
                    severity: 'ERROR',
                    category: 'Return Type Error',
                    title: 'Return Type Mismatch',
                    message: `Function '${this.currentFunction.name}' expects return type '${expectedType}', but returned expression has type '${retExprType}'.`,
                    line: node.line,
                    column: node.column,
                    recoveryTechnique: 'Phrase-Level Recovery: Inferred function return value type for analysis.',
                    suggestedFix: `Ensure returned expression matches expected type '${expectedType}'.`
                });
            }
        }
    }

    visitPrint(node) {
        if (node.expr) {
            this.inferExpressionType(node.expr);
        }
    }

    // --- Type Inference & Scope Resolution ---

    inferExpressionType(expr) {
        if (!expr) return 'void';

        if (expr.nodeType === 'Literal') {
            return expr.valueType;
        }

        if (expr.nodeType === 'Identifier') {
            const resolved = this.resolveIdentifier(expr.name, expr.line, expr.column, 'read');
            return resolved ? resolved.type : 'any';
        }

        if (expr.nodeType === 'BinaryExpr') {
            const leftType = this.inferExpressionType(expr.left);
            const rightType = this.inferExpressionType(expr.right);

            // String concatenation (+)
            if (expr.operator === '+') {
                if (leftType === 'string' || rightType === 'string') {
                    return 'string';
                }
            }

            // Arithmetic operations
            if (['+', '-', '*', '/', '%'].includes(expr.operator)) {
                if (leftType === 'string' || rightType === 'string') {
                    this.addDiagnostic({
                        severity: 'ERROR',
                        category: 'Type Mismatch',
                        title: 'Invalid Arithmetic Operation',
                        message: `Operator '${expr.operator}' is not supported between types '${leftType}' and '${rightType}'.`,
                        line: expr.line,
                        column: expr.column,
                        suggestedFix: `Use compatible numeric types (int, float) for arithmetic operations.`
                    });
                    return 'int';
                }

                if (leftType === 'float' || rightType === 'float') {
                    return 'float';
                }

                return 'int';
            }

            // Relational & Equality operations
            if (['==', '!=', '<', '<=', '>', '>='].includes(expr.operator)) {
                return 'int'; // Boolean represented as int
            }

            return leftType || 'int';
        }

        return 'int';
    }

    resolveIdentifier(name, line, column, context = 'read') {
        const currentScope = this.scopeManager.currentScope;
        const trace = currentScope.resolveWithTrace(name);

        if (trace.found && trace.symbol) {
            trace.symbol.addReference(line, column, currentScope.name, context);

            this.resolutions.push(new ResolutionRecord({
                identifier: name,
                usageLine: line,
                usageColumn: column,
                usageScope: `${currentScope.name} (Level ${currentScope.level})`,
                resolved: true,
                resolvedSymbol: trace.symbol,
                lookupPath: trace.steps,
                status: 'SUCCESS',
                declaredScope: `${trace.symbol.scopeName} (Level ${trace.symbol.scopeLevel})`,
                note: `Successfully resolved in ${trace.symbol.scopeName}`
            }));

            return trace.symbol;
        }

        // Identifier not found in lexical chain: Check if it was declared in an inner block or sibling scope!
        const allSymbols = this.symbolTable.getAllSymbols().filter(s => s.name === name);
        let isScopeViolation = false;
        let declaringSymbol = null;

        if (allSymbols.length > 0) {
            // Check if symbol exists in a scope that is a closed block or child/sibling scope
            declaringSymbol = allSymbols[0];
            isScopeViolation = true;
        }

        if (isScopeViolation && declaringSymbol) {
            const diag = new SemanticDiagnostic({
                severity: 'ERROR',
                category: 'Scope Error',
                title: 'Scope Violation',
                message: `'${name}' was declared inside an inner block and cannot be accessed here.`,
                line: line,
                column: column,
                symbolName: name,
                declaredInScope: `${declaringSymbol.scopeName} (Level ${declaringSymbol.scopeLevel})`,
                declaredAtLevel: declaringSymbol.scopeLevel,
                usedInScope: `${currentScope.name} (Level ${currentScope.level})`,
                usedAtLevel: currentScope.level,
                recoveryTechnique: 'Phrase-Level Recovery: Created virtual placeholder in symbol resolution to continue type checking.',
                suggestedFix: `Move the declaration of '${name}' to '${currentScope.name}' scope if it is needed by subsequent statements.`
            });
            this.addDiagnostic(diag);

            this.resolutions.push(new ResolutionRecord({
                identifier: name,
                usageLine: line,
                usageColumn: column,
                usageScope: `${currentScope.name} (Level ${currentScope.level})`,
                resolved: false,
                resolvedSymbol: null,
                lookupPath: trace.steps,
                status: 'SCOPE_VIOLATION',
                declaredScope: `${declaringSymbol.scopeName} (Level ${declaringSymbol.scopeLevel})`,
                note: `Scope Violation: '${name}' was declared in closed '${declaringSymbol.scopeName}' (Level ${declaringSymbol.scopeLevel}) and is inaccessible in '${currentScope.name}' (Level ${currentScope.level}).`
            }));
        } else {
            const diag = new SemanticDiagnostic({
                severity: 'ERROR',
                category: 'Undeclared Identifier',
                title: 'Undeclared Identifier',
                message: `'${name}' has not been declared in any accessible scope.`,
                line: line,
                column: column,
                symbolName: name,
                declaredInScope: 'None',
                declaredAtLevel: null,
                usedInScope: `${currentScope.name} (Level ${currentScope.level})`,
                usedAtLevel: currentScope.level,
                recoveryTechnique: 'Phrase-Level Recovery: Inferred temporary symbol of type int to permit continuing analysis.',
                suggestedFix: `Declare variable '${name}' with a data type before using it.`
            });
            this.addDiagnostic(diag);

            this.resolutions.push(new ResolutionRecord({
                identifier: name,
                usageLine: line,
                usageColumn: column,
                usageScope: `${currentScope.name} (Level ${currentScope.level})`,
                resolved: false,
                resolvedSymbol: null,
                lookupPath: trace.steps,
                status: 'UNDECLARED',
                declaredScope: 'Undeclared',
                note: `Undeclared Identifier: '${name}' was searched through all enclosing scopes up to Global Scope without match.`
            }));
        }

        return null;
    }

    checkUnusedVariables() {
        const allSymbols = this.symbolTable.getAllSymbols();
        for (const sym of allSymbols) {
            if (!sym.isParameter && !sym.type.startsWith('function') && !sym.type.startsWith('procedure')) {
                if (sym.references.length === 0) {
                    this.addDiagnostic({
                        severity: 'WARNING',
                        category: 'Optimization Warning',
                        title: 'Unused Variable',
                        message: `Variable '${sym.name}' is declared in '${sym.scopeName}' but never referenced.`,
                        line: sym.declarationLine,
                        column: sym.declarationCol,
                        symbolName: sym.name,
                        suggestedFix: `Consider removing '${sym.name}' if it is unneeded.`
                    });
                }
            }
        }
    }

    areTypesCompatible(targetType, actualType) {
        if (!targetType || !actualType) return true;
        if (targetType === actualType) return true;
        if (targetType === 'any' || actualType === 'any') return true;

        // Numeric promotion: int can be assigned to float
        if (targetType === 'float' && actualType === 'int') return true;

        return false;
    }

    addDiagnostic(diag) {
        this.diagnostics.push(diag);
    }
}
