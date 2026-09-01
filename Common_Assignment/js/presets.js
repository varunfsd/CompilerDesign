/**
 * ScopeLab - Educational Program Presets for Testing & Viva Demo
 */

export const PRESETS = [
    {
        id: 'default_scope_violation',
        name: 'Default: Scope Violation (y in inner block)',
        description: 'Demonstrates that variable y declared in the inner block scope cannot be accessed in the outer function scope return statement.',
        code: `global x = 10;

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
}`
    },
    {
        id: 'redeclaration_error',
        name: 'Semantic Error: Redeclaration in Same Scope',
        description: 'Demonstrates detection of duplicate variable and parameter definitions in the exact same scope.',
        code: `global x = 10;

function testRedeclare(a) {
    int count = 5;
    int count = 10; // Error: count redeclared in testRedeclare()

    {
        int temp = 20;
        int temp = 30; // Error: temp redeclared in Block
    }

    return count;
}`
    },
    {
        id: 'undeclared_identifier',
        name: 'Semantic Error: Undeclared Variable',
        description: 'Demonstrates symbol lookup failure when an identifier was never declared in any enclosing or global scope.',
        code: `global total = 100;

function compute(val) {
    int result = val * factor; // Error: factor is undeclared

    return result + missingVar; // Error: missingVar is undeclared
}`
    },
    {
        id: 'type_mismatch',
        name: 'Semantic Error: Type Mismatch & Incompatible Return',
        description: 'Demonstrates static type checking on variable initializers, operations, and function/procedure returns.',
        code: `function calculateScore(bonus) {
    int score = "InvalidString"; // Error: type mismatch
    float multiplier = 1.5;

    return score;
}

procedure printStatus(msg) {
    print msg;
    return 100; // Error: procedure has void return type
}`
    },
    {
        id: 'error_recovery_demo',
        name: 'Error Recovery: Phrase-Level & Panic Mode',
        description: 'Demonstrates virtual semicolon insertion and panic mode token skipping to synchronize parser.',
        code: `global x = 10 // Missing semicolon (Phrase-Level Recovery)

function process(a, b) {
    int num = 42
    
    // Malformed statement triggers panic mode synchronization
    @#$ invalid_token_sequence ;

    int validVar = num + a;
    return validVar;
}`
    },
    {
        id: 'clean_nested_scopes',
        name: 'Clean Program: Deep 3-Level Nested Scopes',
        description: 'Valid program showing lexical variable shadowing, global variable access, and correct scope inheritance.',
        code: `global systemBase = 1000;

function processTransaction(userId, amount) {
    int fee = 15;
    int balance = systemBase;

    {
        int localMultiplier = 2;
        int discount = 5;

        {
            int finalCalculation = (amount * localMultiplier) - discount + fee;
            balance = balance + finalCalculation;
        }
    }

    return balance;
}

procedure logTransaction(status) {
    string prefix = "System Log: ";
    print prefix + status;
}`
    }
];
