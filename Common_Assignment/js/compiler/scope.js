/**
 * ScopeLab - Scope and Scope Hierarchy Management
 */

export const ScopeType = {
    GLOBAL: 'GLOBAL',
    FUNCTION: 'FUNCTION',
    PROCEDURE: 'PROCEDURE',
    BLOCK: 'BLOCK'
};

export class Scope {
    constructor({
        id,
        name,
        type = ScopeType.BLOCK,
        level = 0,
        parent = null,
        startLine = 1,
        endLine = 1
    }) {
        this.id = id;
        this.name = name;
        this.type = type;
        this.level = level;
        this.parent = parent;
        this.children = [];
        this.symbols = new Map(); // name -> Symbol
        this.startLine = startLine;
        this.endLine = endLine;
    }

    define(symbol) {
        this.symbols.set(symbol.name, symbol);
    }

    lookupLocal(name) {
        return this.symbols.get(name) || null;
    }

    /**
     * Lexical scope resolution climbing up the parent scope chain.
     * Records the exact resolution step-by-step path for educational display.
     */
    resolveWithTrace(name) {
        let current = this;
        const steps = [];
        let resolvedSymbol = null;

        while (current) {
            const found = current.lookupLocal(name);
            if (found) {
                steps.push({
                    scopeId: current.id,
                    scopeName: current.name,
                    scopeLevel: current.level,
                    found: true,
                    symbol: found
                });
                resolvedSymbol = found;
                break;
            } else {
                steps.push({
                    scopeId: current.id,
                    scopeName: current.name,
                    scopeLevel: current.level,
                    found: false,
                    symbol: null
                });
                current = current.parent;
            }
        }

        return {
            symbol: resolvedSymbol,
            found: resolvedSymbol !== null,
            steps: steps
        };
    }

    /**
     * Retrieves all accessible symbols from this scope (including enclosing scopes).
     * Preserves lexical shadowing (the innermost definition shadows outer definitions).
     */
    getAccessibleSymbols() {
        const accessible = new Map(); // name -> { symbol, scopeName, scopeLevel, isShadowed }
        let current = this;

        while (current) {
            for (const [name, sym] of current.symbols.entries()) {
                if (!accessible.has(name)) {
                    accessible.set(name, {
                        symbol: sym,
                        declaredInScope: current.name,
                        declaredAtLevel: current.level,
                        isShadowed: false
                    });
                }
            }
            current = current.parent;
        }

        return Array.from(accessible.values());
    }

    getLocalSymbols() {
        return Array.from(this.symbols.values());
    }

    isDescendantOf(potentialAncestor) {
        let curr = this.parent;
        while (curr) {
            if (curr.id === potentialAncestor.id) return true;
            curr = curr.parent;
        }
        return false;
    }
}

export class ScopeManager {
    constructor() {
        this.scopes = [];
        this.globalScope = null;
        this.currentScope = null;
        this.scopeCounter = 0;
    }

    reset() {
        this.scopes = [];
        this.scopeCounter = 0;
        this.globalScope = new Scope({
            id: 'scope_0',
            name: 'Global Scope',
            type: ScopeType.GLOBAL,
            level: 0,
            parent: null,
            startLine: 1,
            endLine: 9999
        });
        this.scopes.push(this.globalScope);
        this.currentScope = this.globalScope;
        return this.globalScope;
    }

    enterScope(name, type, startLine = 1) {
        this.scopeCounter++;
        const newScope = new Scope({
            id: `scope_${this.scopeCounter}`,
            name: name,
            type: type,
            level: this.currentScope.level + 1,
            parent: this.currentScope,
            startLine: startLine,
            endLine: startLine
        });

        this.currentScope.children.push(newScope);
        this.scopes.push(newScope);
        this.currentScope = newScope;
        return newScope;
    }

    exitScope(endLine = 1) {
        if (this.currentScope) {
            this.currentScope.endLine = endLine;
            this.currentScope = this.currentScope.parent || this.globalScope;
        }
        return this.currentScope;
    }

    getAllScopes() {
        return this.scopes;
    }

    getScopeById(id) {
        return this.scopes.find(s => s.id === id) || null;
    }

    getScopeForLine(line) {
        // Find the deepest scope containing this line
        let deepest = this.globalScope;
        for (const sc of this.scopes) {
            if (line >= sc.startLine && line <= sc.endLine) {
                if (sc.level >= deepest.level) {
                    deepest = sc;
                }
            }
        }
        return deepest;
    }
}
