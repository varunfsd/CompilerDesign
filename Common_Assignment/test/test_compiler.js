/**
 * ScopeLab - Automated Node.js Compiler Engine Test
 */

import { Lexer } from '../js/compiler/lexer.js';
import { Parser } from '../js/compiler/parser.js';
import { RecoveryManager } from '../js/compiler/errorRecovery.js';
import { ScopeManager } from '../js/compiler/scope.js';
import { SymbolTable } from '../js/compiler/symbolTable.js';
import { SemanticAnalyzer } from '../js/compiler/semanticAnalyzer.js';

const defaultProgram = `
global x = 10;

function calculate(a, b) {
    int x = 5;

    {
        int y = x + a;
        float z = y * b;
    }

    return x + y;
}

procedure display(msg) {
    string x = "Result:";
    print x + msg;
}
`;

console.log("=== RUNNING COMPILER TEST ===");

const lexer = new Lexer(defaultProgram);
const lexResult = lexer.tokenize();
console.log(`Tokens extracted: ${lexResult.tokens.length}`);

const recoveryManager = new RecoveryManager();
const parser = new Parser(lexResult.tokens, recoveryManager);
const parseResult = parser.parse();
console.log(`AST Declarations: ${parseResult.ast.declarations.length}`);
console.log(`Syntax Errors: ${parseResult.syntaxErrors.length}`);

const scopeManager = new ScopeManager();
const symbolTable = new SymbolTable();
const analyzer = new SemanticAnalyzer(scopeManager, symbolTable, recoveryManager);
const result = analyzer.analyze(parseResult.ast);

console.log("\n--- SYMBOL TABLE ---");
console.table(result.symbolTable.map(s => ({
    Name: s.name,
    Type: s.type,
    Scope: s.scopeName,
    Level: s.scopeLevel,
    Memory: s.memoryLocation,
    Param: s.isParameter ? 'Yes' : 'No'
})));

console.log("\n--- DIAGNOSTICS ---");
result.diagnostics.forEach(d => {
    console.log(`[${d.severity}] Line ${d.line}: ${d.title} - ${d.message}`);
    if (d.declaredInScope) console.log(`  Declared in: ${d.declaredInScope}`);
    if (d.usedInScope) console.log(`  Used in: ${d.usedInScope}`);
});

console.log("\n--- SCOPES ---");
result.scopes.forEach(s => {
    console.log(`- Scope '${s.name}' (Level ${s.level}), Parent: ${s.parent ? s.parent.name : 'null'}, Symbols: ${Array.from(s.symbols.keys()).join(', ')}`);
});

console.log("\n--- RESOLUTIONS ---");
result.resolutions.forEach(r => {
    console.log(`Identifier '${r.identifier}' at line ${r.usageLine} in ${r.usageScope} -> Status: ${r.status}`);
});

// Assertions
const scopeErrors = result.diagnostics.filter(d => d.category === 'Scope Error' && d.symbolName === 'y');
if (scopeErrors.length > 0) {
    console.log("\n[PASS] Correctly detected scope violation for 'y' at return x + y!");
} else {
    console.error("\n[FAIL] Failed to detect scope violation for 'y'!");
    process.exit(1);
}
