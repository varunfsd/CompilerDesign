"""Tests for Code Generation (LLVM IR & x86-64 Assembly)."""

import unittest
from craftlang.compiler import CraftLangCompiler


class TestCodeGen(unittest.TestCase):

    def test_llvm_emitter(self):
        code = """
        fn add(a: int, b: int) -> int {
            return a + b;
        }

        fn main() -> void {
            let res: int = add(10, 20);
            print(res);
        }
        """
        compiler = CraftLangCompiler()
        res = compiler.compile(code, execute=False)
        self.assertTrue(res.success)
        self.assertIn("@main", res.llvm_ir)
        self.assertIn("@add", res.llvm_ir)
        self.assertIn("@printf", res.llvm_ir)
        self.assertIn("add nsw i32", res.llvm_ir)

    def test_asm_emitter(self):
        code = """
        fn multiply(a: int, b: int) -> int {
            return a * b;
        }

        fn main() -> void {
            let res: int = multiply(6, 7);
            print(res);
        }
        """
        compiler = CraftLangCompiler()
        res = compiler.compile(code, execute=False)
        self.assertTrue(res.success)
        self.assertIn(".globl main", res.assembly)
        self.assertIn("pushq   %rbp", res.assembly)
        self.assertIn("imulq", res.assembly)


if __name__ == "__main__":
    unittest.main()
