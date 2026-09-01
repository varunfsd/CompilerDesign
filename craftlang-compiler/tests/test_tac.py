"""Tests for Three-Address Code (TAC) Generation."""

import unittest
from craftlang.lexer.lexer import Lexer
from craftlang.parser.parser import Parser
from craftlang.semantics.analyzer import SemanticAnalyzer
from craftlang.ir.tac_generator import TACGenerator
from craftlang.ir.instructions import OpCode


class TestTAC(unittest.TestCase):

    def generate_tac(self, code: str):
        tokens = Lexer(code).tokenize()
        ast = Parser(tokens, source=code).parse()
        SemanticAnalyzer(source=code).analyze(ast)
        return TACGenerator().generate(ast)

    def test_arithmetic_tac(self):
        code = "let x: int = (2 + 3) * 4;"
        tac = self.generate_tac(code)
        ops = [i.op for i in tac]
        self.assertIn(OpCode.ADD, ops)
        self.assertIn(OpCode.MUL, ops)
        self.assertIn(OpCode.ASSIGN, ops)

    def test_while_tac_labels(self):
        code = """
        let i: int = 0;
        while (i < 5) {
            i = i + 1;
        }
        """
        tac = self.generate_tac(code)
        ops = [i.op for i in tac]
        self.assertIn(OpCode.LABEL, ops)
        self.assertIn(OpCode.JUMP_IF_FALSE, ops)
        self.assertIn(OpCode.JUMP, ops)


if __name__ == "__main__":
    unittest.main()
