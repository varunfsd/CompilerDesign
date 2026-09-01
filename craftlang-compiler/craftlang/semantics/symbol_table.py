"""Scoped Symbol Table for CraftLang semantic analysis."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from .types import Type


@dataclass
class Symbol:
    """Represents an entry in the symbol table."""
    name: str
    type: Type
    category: str       # "variable", "parameter", "function", "builtin"
    line: int
    column: int
    scope_level: int
    scope_name: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": str(self.type),
            "category": self.category,
            "line": self.line,
            "column": self.column,
            "scope_level": self.scope_level,
            "scope_name": self.scope_name,
        }


class SymbolTable:
    """Hierarchical scoped symbol table."""

    def __init__(self, name: str = "global", parent: Optional["SymbolTable"] = None, level: int = 0):
        self.name: str = name
        self.parent: Optional["SymbolTable"] = parent
        self.level: int = level
        self.symbols: Dict[str, Symbol] = {}
        self.children: List["SymbolTable"] = []

        if parent is not None:
            parent.children.append(self)

    def define(self, symbol: Symbol) -> bool:
        """Inserts a symbol in the current scope. Returns False if already defined in THIS scope."""
        if symbol.name in self.symbols:
            return False
        self.symbols[symbol.name] = symbol
        return True

    def lookup(self, name: str, current_scope_only: bool = False) -> Optional[Symbol]:
        """Look up symbol by name, walking up the parent scope chain if current_scope_only is False."""
        if name in self.symbols:
            return self.symbols[name]
        if not current_scope_only and self.parent is not None:
            return self.parent.lookup(name, current_scope_only=False)
        return None

    def lookup_function(self, name: str) -> Optional[Symbol]:
        """Look up a function symbol starting from global scope."""
        root = self
        while root.parent is not None:
            root = root.parent
        sym = root.lookup(name, current_scope_only=True)
        if sym and sym.category in ("function", "builtin"):
            return sym
        return None

    def get_all_symbols_flat(self) -> List[Dict[str, Any]]:
        """Collects all symbols across this table and all its subscopes as a flat list for UI inspection."""
        results = [sym.to_dict() for sym in self.symbols.values()]
        for child in self.children:
            results.extend(child.get_all_symbols_flat())
        return results

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the entire scope tree."""
        return {
            "name": self.name,
            "level": self.level,
            "symbols": [s.to_dict() for s in self.symbols.values()],
            "children": [c.to_dict() for c in self.children],
        }
