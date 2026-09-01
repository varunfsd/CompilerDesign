"""Tests for Optimization Passes."""

import unittest
from craftlang.lexer.lexer import Lexer
from craftlang.parser.parser import Parser
from craftlang.semantics.analyzer import SemanticAnalyzer
from craftlang.ir.tac_generator import TACGenerator
from craftlang.optimizer.pass_manager import PassManager
from craftlang.optimizer.constant_folding import ConstantFoldingPass
from craftlang.optimizer.algebraic_simplification import AlgebraicSimplificationPass


class TestOptimizer(unittest.TestCase):

    def get_tac(self, code: str):
        tokens = Lexer(code).tokenize()
        ast = Parser(tokens, source=code).parse()
        SemanticAnalyzer(source=code).analyze(ast)
        return TACGenerator().generate(ast)

    def test_constant_folding(self):
        code = "let x: int = 10 + 20 * 2;"
        tac = self.get_tac(code)
        opt_tac, changes = ConstantFoldingPass().run(tac)
        self.assertTrue(any(inst.arg1 == 50 or inst.arg1 == 40 for inst in opt_tac))

    def test_algebraic_simplification(self):
        code = """
        fn test(x: int) -> int {
            let y: int = x * 1 + 0;
            return y;
        }
        """
        tac = self.get_tac(code)
        opt_tac, changes = AlgebraicSimplificationPass().run(tac)
        self.assertTrue(len(changes) > 0)

    def test_full_pipeline_optimization(self):
        code = """
        let a: int = 5 + 5;
        let b: int = a * 1;
        let dead: int = 100;
        print(b);
        """
        tac = self.get_tac(code)
        opt_tac, steps = PassManager().optimize(tac)
        self.assertTrue(len(steps) > 0)
        opt_text = "\n".join(i.format() for i in opt_tac)
        self.assertNotIn("dead", opt_text)


if __name__ == "__main__":
    unittest.main()
