"""Tests for CraftLang Lexer."""

import unittest
from craftlang.lexer.lexer import Lexer
from craftlang.lexer.tokens import TokenType
from craftlang.errors import LexerError


class TestLexer(unittest.TestCase):

    def test_keywords_and_identifiers(self):
        code = "let x: int = 42; fn test() -> void {} if while return print true false"
        tokens = Lexer(code).tokenize()
        types = [t.type for t in tokens]
        self.assertEqual(types[0], TokenType.LET)
        self.assertEqual(types[1], TokenType.IDENTIFIER)
        self.assertEqual(types[2], TokenType.COLON)
        self.assertEqual(types[3], TokenType.TYPE_INT)
        self.assertEqual(types[4], TokenType.ASSIGN)
        self.assertEqual(types[5], TokenType.INT_LIT)
        self.assertEqual(tokens[5].value, 42)

    def test_numbers_and_strings(self):
        code = '100 3.1415 "Hello World\\n"'
        tokens = Lexer(code).tokenize()
        self.assertEqual(tokens[0].value, 100)
        self.assertEqual(tokens[1].value, 3.1415)
        self.assertEqual(tokens[2].value, "Hello World\n")

    def test_operators(self):
        code = "+ - * / % == != < <= > >= && || !"
        tokens = Lexer(code).tokenize()
        expected = [
            TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH, TokenType.PERCENT,
            TokenType.EQ_EQ, TokenType.BANG_EQ, TokenType.LT, TokenType.LTE, TokenType.GT, TokenType.GTE,
            TokenType.AND, TokenType.OR, TokenType.BANG, TokenType.EOF,
        ]
        self.assertEqual([t.type for t in tokens], expected)

    def test_comments(self):
        code = """
        // Single line comment
        let x: int = 10; /* Multi-line
        comment */
        let y: int = 20;
        """
        tokens = Lexer(code).tokenize()
        names = [t.value for t in tokens if t.type == TokenType.IDENTIFIER]
        self.assertEqual(names, ["x", "y"])

    def test_invalid_character(self):
        code = "let x = @123;"
        with self.assertRaises(LexerError):
            Lexer(code).tokenize()


if __name__ == "__main__":
    unittest.main()
