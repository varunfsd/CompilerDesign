"""Type definitions and type system operations for CraftLang."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass(frozen=True)
class Type:
    """Base representation of a CraftLang type."""
    name: str

    def is_numeric(self) -> bool:
        return self.name in ("int", "float")

    def is_boolean(self) -> bool:
        return self.name == "bool"

    def is_string(self) -> bool:
        return self.name == "string"

    def is_void(self) -> bool:
        return self.name == "void"

    def __str__(self) -> str:
        return self.name

    def to_dict(self) -> Dict[str, Any]:
        return {"kind": "primitive", "name": self.name}


@dataclass(frozen=True)
class FunctionType(Type):
    """Function type with parameter types and return type."""
    param_types: List[Type]
    return_type: Type

    def __init__(self, param_types: List[Type], return_type: Type):
        object.__setattr__(self, "name", f"({', '.join(str(p) for p in param_types)}) -> {return_type}")
        object.__setattr__(self, "param_types", param_types)
        object.__setattr__(self, "return_type", return_type)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kind": "function",
            "name": self.name,
            "params": [str(p) for p in self.param_types],
            "return_type": str(self.return_type),
        }


# Standard Primitive Singletons
INT_TYPE = Type("int")
FLOAT_TYPE = Type("float")
BOOL_TYPE = Type("bool")
STRING_TYPE = Type("string")
VOID_TYPE = Type("void")
UNKNOWN_TYPE = Type("unknown")

PRIMITIVES: Dict[str, Type] = {
    "int": INT_TYPE,
    "float": FLOAT_TYPE,
    "bool": BOOL_TYPE,
    "string": STRING_TYPE,
    "void": VOID_TYPE,
}


def from_type_name(name: str) -> Type:
    """Resolves a type string to a Type instance."""
    return PRIMITIVES.get(name, UNKNOWN_TYPE)


def check_assignment_compatibility(target: Type, source: Type) -> bool:
    """Returns True if source type can be assigned to target type (allows int -> float promotion)."""
    if target == source:
        return True
    if target == FLOAT_TYPE and source == INT_TYPE:
        return True
    return False


def get_binary_result_type(left: Type, op: str, right: Type) -> Optional[Type]:
    """Computes the resulting type of a binary operation, or None if invalid."""
    # Arithmetic operators (+, -, *, /, %)
    if op in ("+", "-", "*", "/"):
        if left == INT_TYPE and right == INT_TYPE:
            return INT_TYPE
        if (left == INT_TYPE and right == FLOAT_TYPE) or (left == FLOAT_TYPE and right == INT_TYPE) or (left == FLOAT_TYPE and right == FLOAT_TYPE):
            return FLOAT_TYPE
        if op == "+" and (left == STRING_TYPE or right == STRING_TYPE):
            return STRING_TYPE  # String concatenation
        return None

    if op == "%":
        # Modulo is supported on integers
        if left == INT_TYPE and right == INT_TYPE:
            return INT_TYPE
        return None

    # Comparison / Relational operators (==, !=, <, <=, >, >=)
    if op in ("==", "!="):
        if left == right:
            return BOOL_TYPE
        if left.is_numeric() and right.is_numeric():
            return BOOL_TYPE
        return None

    if op in ("<", "<=", ">", ">="):
        if left.is_numeric() and right.is_numeric():
            return BOOL_TYPE
        return None

    # Logical operators (&&, ||)
    if op in ("&&", "||"):
        if left == BOOL_TYPE and right == BOOL_TYPE:
            return BOOL_TYPE
        return None

    return None
