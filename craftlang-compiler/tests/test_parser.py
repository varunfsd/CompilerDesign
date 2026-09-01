"""Tests for CraftLang Parser."""

import unittest
from craftlang.lexer.lexer import Lexer
from craftlang.parser.parser import Parser
from craftlang.parser.ast_nodes import Program, VarDecl, FunctionDef, BinaryOp, IfStmt, WhileStmt
from craftlang.errors import ParserError


class TestParser(unittest.TestCase):

    def parse(self, code: str) -> Program:
        tokens = Lexer(code).tokenize()
        return Parser(tokens, source=code).parse()

    def test_var_decl(self):
        ast = self.parse("let count: int = 5 + 3 * 2;")
        self.assertEqual(len(ast.declarations), 1)
        decl = ast.declarations[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "count")
        self.assertEqual(decl.type_name, "int")
        # Precedence: 5 + (3 * 2)
        self.assertIsInstance(decl.initializer, BinaryOp)
        self.assertEqual(decl.initializer.op, "+")
        self.assertEqual(decl.initializer.right.op, "*")

    def test_function_definition(self):
        code = """
        fn add(a: int, b: int) -> int {
            return a + b;
        }
        """
        ast = self.parse(code)
        self.assertEqual(len(ast.declarations), 1)
        fn_decl = ast.declarations[0]
        self.assertIsInstance(fn_decl, FunctionDef)
        self.assertEqual(fn_decl.name, "add")
        self.assertEqual(len(fn_decl.params), 2)
        self.assertEqual(fn_decl.return_type, "int")

    def test_if_while(self):
        code = """
        if (x > 0) {
            print(x);
        } else {
            print(0);
        }

        while (x < 10) {
            x = x + 1;
        }
        """
        ast = self.parse(code)
        self.assertEqual(len(ast.declarations), 2)
        self.assertIsInstance(ast.declarations[0], IfStmt)
        self.assertIsInstance(ast.declarations[1], WhileStmt)

    def test_syntax_error(self):
        code = "let x int = 5;"  # Missing colon
        with self.assertRaises(ParserError):
            self.parse(code)


if __name__ == "__main__":
    unittest.main()
