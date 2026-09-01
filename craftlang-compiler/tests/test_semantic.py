"""Tests for CraftLang Semantic Analyzer."""

import unittest
from craftlang.lexer.lexer import Lexer
from craftlang.parser.parser import Parser
from craftlang.semantics.analyzer import SemanticAnalyzer
from craftlang.errors import SemanticError


class TestSemantic(unittest.TestCase):

    def analyze(self, code: str):
        tokens = Lexer(code).tokenize()
        ast = Parser(tokens, source=code).parse()
        analyzer = SemanticAnalyzer(source=code)
        return analyzer.analyze(ast)

    def test_valid_program(self):
        code = """
        let x: int = 10;
        let y: float = 3.5;
        let is_ok: bool = true;

        fn double_it(n: int) -> int {
            return n * 2;
        }

        let z: int = double_it(x);
        """
        table = self.analyze(code)
        self.assertIsNotNone(table.lookup("x"))
        self.assertIsNotNone(table.lookup("double_it"))

    def test_undeclared_variable(self):
        code = "let x: int = y + 1;"
        with self.assertRaises(SemanticError):
            self.analyze(code)

    def test_type_mismatch_assignment(self):
        code = 'let x: int = "hello";'
        with self.assertRaises(SemanticError):
            self.analyze(code)

    def test_duplicate_declaration(self):
        code = """
        let a: int = 1;
        let a: int = 2;
        """
        with self.assertRaises(SemanticError):
            self.analyze(code)

    def test_invalid_condition_type(self):
        code = """
        if (42) {
            print(1);
        }
        """
        with self.assertRaises(SemanticError):
            self.analyze(code)


if __name__ == "__main__":
    unittest.main()
