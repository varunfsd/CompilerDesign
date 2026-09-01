"""Compiler diagnostic and error reporting module."""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Diagnostic:
    """Represents a compiler diagnostic with precise location info."""
    stage: str
    message: str
    line: int
    column: int
    length: int = 1
    source_line: Optional[str] = None
    severity: str = "ERROR"  # "ERROR", "WARNING", "NOTE"

    def format_cli(self) -> str:
        """Formats the diagnostic with caret indicators for terminal output."""
        output = [f"[{self.severity}] ({self.stage}) Line {self.line}, Column {self.column}: {self.message}"]
        if self.source_line:
            output.append(f"  {self.line} | {self.source_line}")
            padding = " " * (len(str(self.line)) + 3 + max(0, self.column - 1))
            caret = "^" * max(1, self.length)
            output.append(f"{padding}{caret}")
        return "\n".join(output)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes diagnostic to JSON-compatible dictionary."""
        return {
            "stage": self.stage,
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "length": self.length,
            "source_line": self.source_line,
            "severity": self.severity,
            "formatted": self.format_cli(),
        }


class CompilerError(Exception):
    """Base exception for all compiler pipeline errors."""
    def __init__(self, diagnostic: Diagnostic):
        super().__init__(diagnostic.format_cli())
        self.diagnostic = diagnostic


class LexerError(CompilerError):
    """Raised during lexical scanning."""
    def __init__(self, message: str, line: int, column: int, length: int = 1, source_line: Optional[str] = None):
        super().__init__(Diagnostic("Lexer", message, line, column, length, source_line))


class ParserError(CompilerError):
    """Raised during syntactic parsing."""
    def __init__(self, message: str, line: int, column: int, length: int = 1, source_line: Optional[str] = None):
        super().__init__(Diagnostic("Parser", message, line, column, length, source_line))


class SemanticError(CompilerError):
    """Raised during semantic analysis and type checking."""
    def __init__(self, message: str, line: int, column: int, length: int = 1, source_line: Optional[str] = None):
        super().__init__(Diagnostic("Semantic Analyzer", message, line, column, length, source_line))


class TACError(CompilerError):
    """Raised during intermediate representation lowering."""
    def __init__(self, message: str, line: int = 1, column: int = 1):
        super().__init__(Diagnostic("TAC Generator", message, line, column))


class RuntimeError(CompilerError):
    """Raised during virtual machine execution."""
    def __init__(self, message: str, line: int = 1, column: int = 1):
        super().__init__(Diagnostic("VM Runtime", message, line, column))
