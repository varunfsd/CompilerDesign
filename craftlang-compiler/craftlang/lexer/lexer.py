"""Lexer implementation for CraftLang."""

from typing import List, Optional, Any
from .tokens import TokenType, Token, KEYWORDS
from ..errors import LexerError


class Lexer:
    """Scans CraftLang source text into a sequential stream of Tokens."""

    def __init__(self, source: str):
        self.source: str = source
        self.length: int = len(source)
        self.lines: List[str] = source.splitlines()
        self.pos: int = 0
        self.line: int = 1
        self.col: int = 1
        self.tokens: List[Token] = []

    def _get_current_line(self, line_num: int) -> Optional[str]:
        idx = line_num - 1
        if 0 <= idx < len(self.lines):
            return self.lines[idx]
        return None

    def _peek(self, offset: int = 0) -> str:
        idx = self.pos + offset
        if idx < self.length:
            return self.source[idx]
        return '\0'

    def _advance(self) -> str:
        ch = self._peek()
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def tokenize(self) -> List[Token]:
        """Tokenizes the entire source string and returns a list of Tokens."""
        self.tokens = []
        while self.pos < self.length:
            ch = self._peek()

            # Skip whitespace
            if ch in (' ', '\t', '\r', '\n'):
                self._advance()
                continue

            # Comments
            if ch == '/' and self._peek(1) == '/':
                # Single-line comment
                while self._peek() != '\0' and self._peek() != '\n':
                    self._advance()
                continue

            if ch == '/' and self._peek(1) == '*':
                # Multi-line comment
                start_line, start_col = self.line, self.col
                self._advance()  # '/'
                self._advance()  # '*'
                closed = False
                while self._peek() != '\0':
                    if self._peek() == '*' and self._peek(1) == '/':
                        self._advance()
                        self._advance()
                        closed = True
                        break
                    self._advance()
                if not closed:
                    raise LexerError(
                        "Unterminated multi-line comment",
                        line=start_line,
                        column=start_col,
                        length=2,
                        source_line=self._get_current_line(start_line),
                    )
                continue

            start_line = self.line
            start_col = self.col

            # Numbers (Integer & Float)
            if ch.isdigit():
                self._lex_number(start_line, start_col)
                continue

            # Strings
            if ch == '"':
                self._lex_string(start_line, start_col)
                continue

            # Identifiers and Keywords
            if ch.isalpha() or ch == '_':
                self._lex_identifier(start_line, start_col)
                continue

            # Two-character and Single-character Operators / Punctuation
            self._lex_symbol(start_line, start_col)

        # Append EOF token
        self.tokens.append(Token(
            type=TokenType.EOF,
            value=None,
            raw="",
            line=self.line,
            column=self.col,
            length=0,
        ))
        return self.tokens

    def _lex_number(self, start_line: int, start_col: int) -> None:
        start_pos = self.pos
        is_float = False

        while self._peek().isdigit():
            self._advance()

        # Check for fractional point
        if self._peek() == '.' and self._peek(1).isdigit():
            is_float = True
            self._advance()  # consume '.'
            while self._peek().isdigit():
                self._advance()

        raw = self.source[start_pos:self.pos]
        val = float(raw) if is_float else int(raw)
        tok_type = TokenType.FLOAT_LIT if is_float else TokenType.INT_LIT

        self.tokens.append(Token(
            type=tok_type,
            value=val,
            raw=raw,
            line=start_line,
            column=start_col,
            length=len(raw),
        ))

    def _lex_string(self, start_line: int, start_col: int) -> None:
        start_pos = self.pos
        self._advance()  # Skip opening quote
        chars = []

        while True:
            ch = self._peek()
            if ch == '\0' or ch == '\n':
                raise LexerError(
                    "Unterminated string literal",
                    line=start_line,
                    column=start_col,
                    length=self.pos - start_pos,
                    source_line=self._get_current_line(start_line),
                )
            if ch == '"':
                self._advance()  # Skip closing quote
                break

            if ch == '\\':
                self._advance()
                esc = self._advance()
                if esc == 'n':
                    chars.append('\n')
                elif esc == 't':
                    chars.append('\t')
                elif esc == 'r':
                    chars.append('\r')
                elif esc == '"':
                    chars.append('"')
                elif esc == '\\':
                    chars.append('\\')
                else:
                    chars.append(esc)
            else:
                chars.append(self._advance())

        raw = self.source[start_pos:self.pos]
        val = "".join(chars)
        self.tokens.append(Token(
            type=TokenType.STRING_LIT,
            value=val,
            raw=raw,
            line=start_line,
            column=start_col,
            length=len(raw),
        ))

    def _lex_identifier(self, start_line: int, start_col: int) -> None:
        start_pos = self.pos
        while self._peek().isalnum() or self._peek() == '_':
            self._advance()

        raw = self.source[start_pos:self.pos]
        tok_type = KEYWORDS.get(raw, TokenType.IDENTIFIER)

        val: Any = raw
        if tok_type == TokenType.TRUE:
            tok_type = TokenType.BOOL_LIT
            val = True
        elif tok_type == TokenType.FALSE:
            tok_type = TokenType.BOOL_LIT
            val = False

        self.tokens.append(Token(
            type=tok_type,
            value=val,
            raw=raw,
            line=start_line,
            column=start_col,
            length=len(raw),
        ))

    def _lex_symbol(self, start_line: int, start_col: int) -> None:
        ch = self._advance()

        # Two-char checks
        if ch == '=':
            if self._peek() == '=':
                self._advance()
                self.tokens.append(Token(TokenType.EQ_EQ, "==", "==", start_line, start_col, 2))
                return
            self.tokens.append(Token(TokenType.ASSIGN, "=", "=", start_line, start_col, 1))
            return

        if ch == '!':
            if self._peek() == '=':
                self._advance()
                self.tokens.append(Token(TokenType.BANG_EQ, "!=", "!=", start_line, start_col, 2))
                return
            self.tokens.append(Token(TokenType.BANG, "!", "!", start_line, start_col, 1))
            return

        if ch == '<':
            if self._peek() == '=':
                self._advance()
                self.tokens.append(Token(TokenType.LTE, "<=", "<=", start_line, start_col, 2))
                return
            self.tokens.append(Token(TokenType.LT, "<", "<", start_line, start_col, 1))
            return

        if ch == '>':
            if self._peek() == '=':
                self._advance()
                self.tokens.append(Token(TokenType.GTE, ">=", ">=", start_line, start_col, 2))
                return
            self.tokens.append(Token(TokenType.GT, ">", ">", start_line, start_col, 1))
            return

        if ch == '&' and self._peek() == '&':
            self._advance()
            self.tokens.append(Token(TokenType.AND, "&&", "&&", start_line, start_col, 2))
            return

        if ch == '|' and self._peek() == '|':
            self._advance()
            self.tokens.append(Token(TokenType.OR, "||", "||", start_line, start_col, 2))
            return

        if ch == '-' and self._peek() == '>':
            self._advance()
            self.tokens.append(Token(TokenType.ARROW, "->", "->", start_line, start_col, 2))
            return

        # Single-char symbols
        single_map = {
            '+': (TokenType.PLUS, "+"),
            '-': (TokenType.MINUS, "-"),
            '*': (TokenType.STAR, "*"),
            '/': (TokenType.SLASH, "/"),
            '%': (TokenType.PERCENT, "%"),
            '(': (TokenType.LPAREN, "("),
            ')': (TokenType.RPAREN, ")"),
            '{': (TokenType.LBRACE, "{"),
            '}': (TokenType.RBRACE, "}"),
            ',': (TokenType.COMMA, ","),
            ';': (TokenType.SEMICOLON, ";"),
            ':': (TokenType.COLON, ":"),
        }

        if ch in single_map:
            tok_type, raw = single_map[ch]
            self.tokens.append(Token(tok_type, raw, raw, start_line, start_col, 1))
            return

        raise LexerError(
            f"Unexpected character: {ch!r}",
            line=start_line,
            column=start_col,
            length=1,
            source_line=self._get_current_line(start_line),
        )
