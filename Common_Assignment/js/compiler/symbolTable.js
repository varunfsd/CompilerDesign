/**
 * ScopeLab - Symbol & SymbolTable Data Structures
 */

export class Symbol {
    constructor({
        name,
        type = 'int',
        scopeName = 'Global',
        scopeLevel = 0,
        scopeId = 'scope_0',
        memoryLocation = 1000,
        isParameter = false,
        declarationLine = 1,
        declarationCol = 1
    }) {
        this.name = name;
        this.type = type;
        this.scopeName = scopeName;
        this.scopeLevel = scopeLevel;
        this.scopeId = scopeId;
        this.memoryLocation = memoryLocation;
        this.isParameter = isParameter;
        this.declarationLine = declarationLine;
        this.declarationCol = declarationCol;
        this.references = []; // [{ line, column, scopeName, context }]
    }

    addReference(line, column, scopeName, context = 'read') {
        this.references.push({ line, column, scopeName, context });
    }
}

export class SymbolTable {
    constructor() {
        this.symbols = [];
        this.nextMemoryAddress = 1000;
        this.addressIncrement = 4; // 4-byte standard word size
    }

    reset() {
        this.symbols = [];
        this.nextMemoryAddress = 1000;
    }

    allocateAddress() {
        const addr = this.nextMemoryAddress;
        this.nextMemoryAddress += this.addressIncrement;
        return addr;
    }

    addSymbol(symbolData) {
        if (!symbolData.memoryLocation) {
            symbolData.memoryLocation = this.allocateAddress();
        }
        const symbol = new Symbol(symbolData);
        this.symbols.push(symbol);
        return symbol;
    }

    getAllSymbols() {
        return this.symbols;
    }

    getSymbolsByScope(scopeId) {
        return this.symbols.filter(s => s.scopeId === scopeId);
    }
}
