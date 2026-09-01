"""End-to-End Compilation & Execution Pipeline Tests."""

import unittest
from craftlang.compiler import CraftLangCompiler


class TestEndToEnd(unittest.TestCase):

    def setUp(self):
        self.compiler = CraftLangCompiler()

    def test_arithmetic_execution(self):
        code = """
        let a: int = 15;
        let b: int = 4;
        let sum: int = a + b;
        let diff: int = a - b;
        let prod: int = a * b;
        let quot: int = a / b;
        let rem: int = a % b;
        print(sum);
        print(diff);
        print(prod);
        print(quot);
        print(rem);
        """
        res = self.compiler.compile(code, execute=True)
        self.assertTrue(res.success, f"Compilation failed: {res.diagnostics}")
        self.assertIsNotNone(res.execution_result)
        self.assertTrue(res.execution_result["success"])
        lines = res.execution_result["output"].strip().split("\n")
        self.assertEqual(lines, ["19", "11", "60", "3", "3"])

    def test_while_loop_execution(self):
        code = """
        let total: int = 0;
        let i: int = 1;
        while (i <= 5) {
            total = total + i;
            i = i + 1;
        }
        print(total);
        """
        res = self.compiler.compile(code, execute=True)
        self.assertTrue(res.success)
        self.assertEqual(res.execution_result["output"].strip(), "15")

    def test_factorial_recursion(self):
        code = """
        fn factorial(n: int) -> int {
            if (n <= 1) {
                return 1;
            }
            return n * factorial(n - 1);
        }

        fn main() -> void {
            let res: int = factorial(5);
            print(res);
        }
        """
        res = self.compiler.compile(code, execute=True)
        self.assertTrue(res.success)
        self.assertEqual(res.execution_result["output"].strip(), "120")

    def test_fibonacci_iterative(self):
        code = """
        fn fib(n: int) -> int {
            if (n <= 0) { return 0; }
            if (n == 1) { return 1; }
            let a: int = 0;
            let b: int = 1;
            let i: int = 2;
            while (i <= n) {
                let temp: int = a + b;
                a = b;
                b = temp;
                i = i + 1;
            }
            return b;
        }

        fn main() -> void {
            let f7: int = fib(7);
            print(f7);
        }
        """
        res = self.compiler.compile(code, execute=True)
        self.assertTrue(res.success)
        self.assertEqual(res.execution_result["output"].strip(), "13")


if __name__ == "__main__":
    unittest.main()
