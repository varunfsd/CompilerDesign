"""Token definitions and TokenType enumeration for CraftLang."""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Dict


class TokenType(Enum):
    # Literals
    INT_LIT = auto()
    FLOAT_LIT = auto()
    STRING_LIT = auto()
    BOOL_LIT = auto()

    # Identifiers
    IDENTIFIER = auto()

    # Keywords
    LET = auto()
    FN = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    RETURN = auto()
    PRINT = auto()
    
    # Types
    TYPE_INT = auto()
    TYPE_FLOAT = auto()
    TYPE_BOOL = auto()
    TYPE_STRING = auto()
    TYPE_VOID = auto()

    # Boolean literals
    TRUE = auto()
    FALSE = auto()

    # Arithmetic Operators
    PLUS = auto()           # +
    MINUS = auto()          # -
    STAR = auto()           # *
    SLASH = auto()          # /
    PERCENT = auto()        # %

    # Comparison Operators
    EQ_EQ = auto()          # ==
    BANG_EQ = auto()        # !=
    LT = auto()             # <
    LTE = auto()            # <=
    GT = auto()             # >
    GTE = auto()            # >=

    # Logical Operators
    AND = auto()            # &&
    OR = auto()             # ||
    BANG = auto()           # !

    # Assignment
    ASSIGN = auto()         # =

    # Punctuation & Delimiters
    LPAREN = auto()         # (
    RPAREN = auto()         # )
    LBRACE = auto()         # {
    RBRACE = auto()         # }
    COMMA = auto()          # ,
    SEMICOLON = auto()      # ;
    COLON = auto()          # :
    ARROW = auto()          # ->

    # Special
    EOF = auto()


KEYWORDS: Dict[str, TokenType] = {
    "let": TokenType.LET,
    "fn": TokenType.FN,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "return": TokenType.RETURN,
    "print": TokenType.PRINT,
    "int": TokenType.TYPE_INT,
    "float": TokenType.TYPE_FLOAT,
    "bool": TokenType.TYPE_BOOL,
    "string": TokenType.TYPE_STRING,
    "void": TokenType.TYPE_VOID,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
}


@dataclass
class Token:
    """Represents a lexical token with exact source coordinates."""
    type: TokenType
    value: Any
    raw: str
    line: int
    column: int
    length: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, val={self.value!r}, line={self.line}, col={self.column})"

    def to_dict(self) -> Dict[str, Any]:
        """Serializes token for UI table representation."""
        return {
            "type": self.type.name,
            "value": str(self.value) if self.value is not None else "",
            "raw": self.raw,
            "line": self.line,
            "column": self.column,
            "length": self.length,
        }
