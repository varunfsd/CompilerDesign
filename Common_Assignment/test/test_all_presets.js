/**
 * ScopeLab - Automated Comprehensive Test Suite
 * Tests all presets, error cases, recovery cases, and resolution tracing
 */

import { Lexer } from '../js/compiler/lexer.js';
import { Parser } from '../js/compiler/parser.js';
import { RecoveryManager } from '../js/compiler/errorRecovery.js';
import { ScopeManager } from '../js/compiler/scope.js';
import { SymbolTable } from '../js/compiler/symbolTable.js';
import { SemanticAnalyzer } from '../js/compiler/semanticAnalyzer.js';
import { PRESETS } from '../js/presets.js';

console.log("=== COMPREHENSIVE COMPILER TEST SUITE ===");

let totalTests = 0;
let passedTests = 0;

function assert(condition, testName, details = '') {
    totalTests++;
    if (condition) {
        passedTests++;
        console.log(`  [PASS] ${testName}`);
    } else {
        console.error(`  [FAIL] ${testName}: ${details}`);
    }
}

function runAnalysis(sourceCode) {
    const lexer = new Lexer(sourceCode);
    const lexResult = lexer.tokenize();

    const recoveryManager = new RecoveryManager();
    const parser = new Parser(lexResult.tokens, recoveryManager);
    const parseResult = parser.parse();

    const scopeManager = new ScopeManager();
    const symbolTable = new SymbolTable();
    const analyzer = new SemanticAnalyzer(scopeManager, symbolTable, recoveryManager);
    const semanticResult = analyzer.analyze(parseResult.ast);

    return {
        tokens: lexResult.tokens,
        ast: parseResult.ast,
        syntaxErrors: parseResult.syntaxErrors,
        diagnostics: semanticResult.diagnostics,
        resolutions: semanticResult.resolutions,
        symbolTable: semanticResult.symbolTable,
        scopes: semanticResult.scopes,
        recoveryEvents: semanticResult.recoveryEvents
    };
}

// --- Test 1: Default Preset (Scope Violation) ---
console.log("\n--- Testing Preset 1: Default Scope Violation ---");
const p1 = PRESETS.find(p => p.id === 'default_scope_violation');
const r1 = runAnalysis(p1.code);

assert(r1.scopes.length === 4, "Creates 4 scopes (Global, calculate, Block, display)");
assert(r1.symbolTable.length === 10, "Extracts 10 symbols across all scopes");
assert(r1.diagnostics.some(d => d.category === 'Scope Error' && d.symbolName === 'y'), "Identifies 'y' scope violation at return x + y");
assert(r1.symbolTable.some(s => s.name === 'x' && s.memoryLocation === 1000), "Allocates global x at address 1000");
assert(r1.symbolTable.some(s => s.name === 'a' && s.isParameter === true), "Marks param 'a' as parameter");
assert(r1.symbolTable.some(s => s.name === 'y' && s.scopeName === 'Block Scope' && s.scopeLevel === 2), "Records 'y' in Block Scope at level 2");

// Test resolution steps for 'y'
const yRes = r1.resolutions.find(r => r.identifier === 'y' && r.status === 'SCOPE_VIOLATION');
assert(yRes && yRes.status === 'SCOPE_VIOLATION', "Resolution record for 'y' at return statement has SCOPE_VIOLATION status");
assert(yRes && yRes.lookupPath.length >= 2, "Resolution lookup path traced calculate() and Global scopes");

// --- Test 2: Redeclaration Error Preset ---
console.log("\n--- Testing Preset 2: Redeclaration in Same Scope ---");
const p2 = PRESETS.find(p => p.id === 'redeclaration_error');
const r2 = runAnalysis(p2.code);
assert(r2.diagnostics.some(d => d.category === 'Redeclaration Error' && d.symbolName === 'count'), "Detects redeclaration of 'count'");
assert(r2.diagnostics.some(d => d.category === 'Redeclaration Error' && d.symbolName === 'temp'), "Detects redeclaration of 'temp' in nested block");

// --- Test 3: Undeclared Variable Preset ---
console.log("\n--- Testing Preset 3: Undeclared Identifier ---");
const p3 = PRESETS.find(p => p.id === 'undeclared_identifier');
const r3 = runAnalysis(p3.code);
assert(r3.diagnostics.some(d => d.category === 'Undeclared Identifier' && d.symbolName === 'factor'), "Detects undeclared 'factor'");
assert(r3.diagnostics.some(d => d.category === 'Undeclared Identifier' && d.symbolName === 'missingVar'), "Detects undeclared 'missingVar'");

// --- Test 4: Type Mismatch Preset ---
console.log("\n--- Testing Preset 4: Type Mismatch & Incompatible Return ---");
const p4 = PRESETS.find(p => p.id === 'type_mismatch');
const r4 = runAnalysis(p4.code);
assert(r4.diagnostics.some(d => d.category === 'Type Mismatch' && d.symbolName === 'score'), "Detects int score = string mismatch");
assert(r4.diagnostics.some(d => d.category === 'Return Type Error'), "Detects return value inside procedure (void)");

// --- Test 5: Error Recovery Preset ---
console.log("\n--- Testing Preset 5: Phrase-Level & Panic Mode Recovery ---");
const p5 = PRESETS.find(p => p.id === 'error_recovery_demo');
const r5 = runAnalysis(p5.code);
assert(r5.recoveryEvents.some(e => e.technique === 'Phrase-Level Recovery'), "Applies phrase-level semicolon insertion recovery");
assert(r5.recoveryEvents.some(e => e.technique === 'Panic Mode Recovery'), "Applies panic mode synchronization recovery");
assert(r5.symbolTable.some(s => s.name === 'validVar'), "Recovers parsing and successfully analyzes subsequent statements");

// --- Test 6: Clean Nested Scopes Preset ---
console.log("\n--- Testing Preset 6: Clean Multi-Level Scopes ---");
const p6 = PRESETS.find(p => p.id === 'clean_nested_scopes');
const r6 = runAnalysis(p6.code);
const errors = r6.diagnostics.filter(d => d.severity === 'ERROR');
assert(errors.length === 0, "Zero errors on valid 3-level nested scope program");
assert(r6.scopes.some(s => s.level === 3), "Properly handles level 3 nested blocks");

console.log(`\n========================================`);
console.log(`TEST SUMMARY: ${passedTests}/${totalTests} tests passed.`);
console.log(`========================================\n`);

if (passedTests === totalTests) {
    console.log("ALL TESTS COMPLETED SUCCESSFULLY!");
    process.exit(0);
} else {
    process.exit(1);
}
