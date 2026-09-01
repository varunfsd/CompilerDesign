# The Craft of Compilers: Transforming Source Code into Machine Action

An educational compiler and interactive web workbench for **CraftLang**, demonstrating every phase of modern compiler construction from lexical scanning to multi-pass optimization and target code generation.

---

## 🌟 Compiler Architecture Pipeline

```
Source Code
    │
    ▼ [Stage 1]
Lexical Analysis (Scanner / Tokens with Line & Column Tracking)
    │
    ▼ [Stage 2]
Syntax Analysis & AST (Recursive-Descent Parser & Precedence Climbing)
    │
    ▼ [Stage 3]
Semantic Analysis (Scoped Symbol Table & Type Checking)
    │
    ▼ [Stage 4]
Intermediate Representation (Three-Address Code Quadruples & Basic Blocks / CFG)
    │
    ▼ [Stage 5]
Multi-Pass Optimizer:
    ├─ Constant Propagation
    ├─ Constant Folding
    ├─ Algebraic Simplification
    └─ Dead Code Elimination
    │
    ▼ [Stage 6]
Target Code Generation:
    ├─ LLVM IR (Textual LLVM IR Module)
    └─ x86-64 Assembly (AT&T syntax with register allocation & stack layout)
    │
    ▼ [Stage 7]
Virtual Machine Execution (In-Memory TAC Interpreter with stdout & memory tracking)
```

---

## 🚀 Key Features

1. **CraftLang Language Features:**
   - Static primitive types: `int`, `float`, `bool`, `string`, `void`.
   - Variables and mutable bindings: `let x: int = 10;`, `x = x + 5;`.
   - Arithmetic operators: `+`, `-`, `*`, `/`, `%`.
   - Relational & comparison operators: `==`, `!=`, `<`, `<=`, `>`, `>=`.
   - Logical operators: `&&`, `||`, `!`.
   - Control flow: `if (cond) { ... } else { ... }`, `while (cond) { ... }`.
   - Functions & recursion: `fn name(param: type) -> type { return val; }`.
   - I/O: `print(arg1, arg2, ...)`.
   - Single-line (`//`) and multi-line (`/* ... */`) comments.

2. **Educational Compiler Diagnostics:**
   - Precise 1-indexed line and column tracking.
   - Beautiful terminal and web UI error markers with source code context and carets (`^`).

3. **Optimization Passes:**
   - **Constant Propagation:** Propagates known constants through straight-line blocks.
   - **Constant Folding:** Evaluates constant arithmetic, boolean, and comparison operations at compile time.
   - **Algebraic Simplification:** Simplifies identity operations ($x + 0 \rightarrow x$, $x \times 1 \rightarrow x$, $x \times 0 \rightarrow 0$, $x \text{ \&\& } \text{true} \rightarrow x$, etc.).
   - **Dead Code Elimination:** Eliminates unreachable instructions after unconditional jumps/returns, unreferenced labels, and dead variables.

4. **Interactive Web Workbench:**
   - Single-page IDE layout with line numbers and editor controls.
   - **Tokens Inspector:** Filterable table of token types, values, lines, and columns.
   - **AST Visualizer:** Mermaid.js flowchart and raw JSON tree views.
   - **Symbol Table:** Scoped symbols view displaying variable categories, resolved types, and scope depths.
   - **Three-Address Code (TAC):** Side-by-side comparison of unoptimized vs. optimized TAC with Control Flow Graph (CFG) diagram.
   - **Optimization Timeline:** Step-by-step pass breakdown explaining exactly what was transformed.
   - **LLVM IR / Assembly:** Syntax-highlighted target code with 1-click clipboard copy.
   - **Virtual Machine Console:** Live program execution output (stdout), execution step metrics, and memory state inspection.

---

## 📁 Project Structure

```
craftlang-compiler/
├── craftlang/                          # Core Compiler Library
│   ├── errors.py                       # Diagnostics & error formatting
│   ├── compiler.py                     # Pipeline orchestrator
│   ├── lexer/                          # Stage 1: Lexical Analysis
│   │   ├── tokens.py                   # Token definitions & TokenType enum
│   │   └── lexer.py                    # Scanner implementation
│   ├── parser/                         # Stage 2: Syntax Analysis & AST
│   │   ├── ast_nodes.py                # Abstract Syntax Tree definitions
│   │   ├── parser.py                   # Recursive descent & precedence parser
│   │   └── visualizer.py               # AST to Mermaid & JSON serializers
│   ├── semantics/                      # Stage 3: Semantic Analysis
│   │   ├── types.py                    # CraftLang type system
│   │   ├── symbol_table.py             # Scoped symbol tables
│   │   └── analyzer.py                 # Semantic visitor & type checker
│   ├── ir/                             # Stage 4: Intermediate Representation
│   │   ├── instructions.py             # Quadruples/TAC instructions
│   │   ├── basic_block.py              # Basic blocks partitioner
│   │   ├── cfg.py                      # Control Flow Graph builder & visualizer
│   │   └── tac_generator.py            # AST -> TAC Lowering
│   ├── optimizer/                      # Stage 5: Multi-Pass Optimizer
│   │   ├── pass_manager.py             # Optimization runner & step diffs
│   │   ├── constant_folding.py         # Compile-time arithmetic evaluation
│   │   ├── constant_propagation.py     # Propagates constants through variables
│   │   ├── algebraic_simplification.py # Simplifies identity operations
│   │   └── dead_code_elimination.py    # Unreachable code & dead var pruning
│   ├── codegen/                        # Stage 6: Target Code Generation
│   │   ├── llvm_emitter.py             # Standard LLVM IR emitter
│   │   └── asm_emitter.py              # Educational x86-64 assembly emitter
│   └── vm/                             # Stage 7: Virtual Machine
│       └── tac_interpreter.py          # Executes TAC with stdout & memory trace
├── server/                             # FastAPI Backend Service
│   ├── main.py                         # App server & static file hosting
│   ├── routes.py                       # REST API endpoints (/compile, /examples)
│   └── examples.py                     # Preset educational programs
├── web/                                # Frontend Single Page Application
│   ├── index.html                      # Interactive compiler dashboard
│   ├── css/style.css                   # Modern dark-mode styling
│   └── js/
│       ├── app.js                      # UI logic & API coordinator
│       ├── editor.js                   # Code editor with line numbers
│       └── visualizer.js               # Visual AST & diff renderer
├── tests/                              # Comprehensive Test Suite
│   ├── test_lexer.py
│   ├── test_parser.py
│   ├── test_semantic.py
│   ├── test_tac.py
│   ├── test_optimizer.py
│   ├── test_codegen.py
│   └── test_end_to_end.py
└── requirements.txt
```

---

## 💻 Installation & Quickstart

### 1. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 2. Run the Test Suite
```bash
python -m unittest discover -s tests
```

### 3. Launch the Interactive Web Workbench
```bash
python -m uvicorn server.main:app --reload --port 8000
```
Open your browser at `http://localhost:8000`.

---

## 📚 Example CraftLang Program

```rust
// Recursive Factorial in CraftLang
fn factorial(n: int) -> int {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

fn main() -> void {
    let num: int = 5;
    let result: int = factorial(num);
    print("Factorial of 5 is: ", result);
}
```
