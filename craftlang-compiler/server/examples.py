"""Curated educational CraftLang code examples."""

from typing import List, Dict, Any

EXAMPLES: List[Dict[str, Any]] = [
    {
        "id": "intro_arithmetic",
        "title": "1. Variables & Arithmetic",
        "category": "Basics",
        "description": "Demonstrates variables, type definitions, arithmetic operations (+, -, *, /, %), and print output.",
        "code": """// 1. Variables and Arithmetic in CraftLang
let a: int = 25;
let b: int = 10;

let sum: int = a + b;
let diff: int = a - b;
let prod: int = a * b;
let quot: int = a / b;
let rem: int = a % b;

print("Sum:", sum);
print("Difference:", diff);
print("Product:", prod);
print("Quotient:", quot);
print("Remainder:", rem);
""",
    },
    {
        "id": "optimization_showcase",
        "title": "2. Multi-Pass Optimization Showcase",
        "category": "Optimization",
        "description": "Shows constant folding (2+3*4), constant propagation, algebraic simplification (x*1, y+0), and dead code elimination in action.",
        "code": """// 2. Multi-Pass Compiler Optimizations
// Notice how the compiler folds arithmetic, propagates constants,
// simplifies algebraic identities, and eliminates dead code!

let a: int = 10 + 20 * 2;   // Constant Folding: 10 + 40 = 50
let b: int = a + 5;         // Constant Propagation: 50 + 5 = 55
let c: int = b * 1;         // Algebraic Simplification: b * 1 = b
let d: int = c + 0;         // Algebraic Simplification: c + 0 = c
let dead_var: int = 999;    // Dead Code: never used downstream

print("Optimized Value:", d);
""",
    },
    {
        "id": "conditionals",
        "title": "3. Conditionals (if / else)",
        "category": "Control Flow",
        "description": "Tests boolean conditions, relational comparisons, and branching in TAC and LLVM IR.",
        "code": """// 3. Conditionals & Branching in CraftLang
let score: int = 88;

if (score >= 90) {
    print("Grade: A - Outstanding!");
} else if (score >= 80) {
    print("Grade: B - Great work!");
} else if (score >= 70) {
    print("Grade: C - Satisfactory.");
} else {
    print("Grade: F - Needs improvement.");
}
""",
    },
    {
        "id": "while_loop",
        "title": "4. While Loop & Summation",
        "category": "Control Flow",
        "description": "Computes the triangular number (sum of 1 to N) using a while loop and accumulator.",
        "code": """// 4. While Loop: Sum of Numbers from 1 to 10
let n: int = 10;
let total: int = 0;
let i: int = 1;

while (i <= n) {
    total = total + i;
    i = i + 1;
}

print("Sum of 1 to 10 is:", total);
""",
    },
    {
        "id": "factorial_recursion",
        "title": "5. Factorial (Functions & Recursion)",
        "category": "Functions",
        "description": "Demonstrates function declaration, parameter passing, return statements, and recursive evaluation.",
        "code": """// 5. Recursive Factorial in CraftLang
fn factorial(n: int) -> int {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

fn main() -> void {
    let num: int = 6;
    let result: int = factorial(num);
    print("Factorial of 6 is:", result);
}
""",
    },
    {
        "id": "fibonacci_iterative",
        "title": "6. Fibonacci Sequence",
        "category": "Algorithms",
        "description": "Computes the N-th Fibonacci number iteratively using two sliding variables.",
        "code": """// 6. Fibonacci Sequence Calculation
fn fibonacci(n: int) -> int {
    if (n <= 0) {
        return 0;
    }
    if (n == 1) {
        return 1;
    }

    let a: int = 0;
    let b: int = 1;
    let count: int = 2;

    while (count <= n) {
        let temp: int = a + b;
        a = b;
        b = temp;
        count = count + 1;
    }
    return b;
}

fn main() -> void {
    let n: int = 9;
    let fib_n: int = fibonacci(n);
    print("Fibonacci(9) is:", fib_n);
}
""",
    },
    {
        "id": "prime_checker",
        "title": "7. Prime Number Checker",
        "category": "Algorithms",
        "description": "Determines if a number is prime by checking divisibility up to its square root limit.",
        "code": """// 7. Prime Number Checker
fn is_prime(n: int) -> bool {
    if (n <= 1) {
        return false;
    }
    let d: int = 2;
    while (d * d <= n) {
        if (n % d == 0) {
            return false;
        }
        d = d + 1;
    }
    return true;
}

fn main() -> void {
    let target: int = 29;
    let prime: bool = is_prime(target);
    if (prime) {
        print("29 is a prime number!");
    } else {
        print("29 is NOT a prime number.");
    }
}
""",
    },
]
