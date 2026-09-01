"""Virtual Machine and Interpreter for Three-Address Code."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from ..ir.instructions import TACInstruction, OpCode
from ..errors import RuntimeError


@dataclass
class ExecutionResult:
    """Encapsulates the runtime results and diagnostics of executing TAC."""
    output: str
    steps_executed: int
    final_variables: Dict[str, Any]
    return_code: int = 0
    success: bool = True
    error_message: Optional[str] = None
    execution_trace: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "output": self.output,
            "steps_executed": self.steps_executed,
            "final_variables": self.final_variables,
            "return_code": self.return_code,
            "success": self.success,
            "error_message": self.error_message,
            "execution_trace": self.execution_trace[:100],
        }


@dataclass
class StackFrame:
    """Call stack frame for function invocation."""
    fn_name: str
    return_pc: int
    return_dest: Optional[str]
    locals: Dict[str, Any] = field(default_factory=dict)


class TACInterpreter:
    """Executes Three-Address Code instructions with memory and I/O tracking."""

    def __init__(self, max_steps: int = 100_000):
        self.max_steps = max_steps

    def execute(self, instructions: List[TACInstruction]) -> ExecutionResult:
        if not instructions:
            return ExecutionResult(output="", steps_executed=0, final_variables={})

        label_map: Dict[str, int] = {}
        func_map: Dict[str, int] = {}

        for idx, inst in enumerate(instructions):
            if inst.op == OpCode.LABEL:
                label_map[str(inst.arg1)] = idx
            elif inst.op == OpCode.FUNC_START:
                func_map[str(inst.arg1)] = idx

        # Determine starting point: main function if present, otherwise 0
        pc = 0
        if "main" in func_map:
            pc = func_map["main"] + 1

        stdout_lines: List[str] = []
        globals_env: Dict[str, Any] = {}
        param_queue: List[Any] = []
        call_stack: List[StackFrame] = []
        current_frame = StackFrame(fn_name="main" if "main" in func_map else "global", return_pc=-1, return_dest=None)
        steps = 0
        trace: List[Dict[str, Any]] = []

        def get_val(arg: Any) -> Any:
            if isinstance(arg, bool):
                return arg
            if isinstance(arg, (int, float)):
                return arg
            if isinstance(arg, str):
                if len(arg) >= 2 and arg.startswith('"') and arg.endswith('"'):
                    return arg[1:-1]
                if arg in current_frame.locals:
                    return current_frame.locals[arg]
                if arg in globals_env:
                    return globals_env[arg]
                # Default numeric/boolean string if any
                if arg == "true":
                    return True
                if arg == "false":
                    return False
                return arg
            return arg

        def set_val(dest: str, val: Any) -> None:
            if call_stack or current_frame.fn_name != "global":
                current_frame.locals[dest] = val
            else:
                globals_env[dest] = val

        try:
            while 0 <= pc < len(instructions):
                steps += 1
                if steps > self.max_steps:
                    raise RuntimeError(f"Execution step limit exceeded ({self.max_steps} steps). Potential infinite loop.")

                inst = instructions[pc]

                if steps <= 50:
                    trace.append({
                        "step": steps,
                        "pc": pc,
                        "instruction": inst.format().strip(),
                        "fn": current_frame.fn_name,
                    })

                op = inst.op

                if op == OpCode.FUNC_START:
                    fn_name = str(inst.arg1)
                    if current_frame.fn_name != fn_name:
                        # Skip past function definition
                        scan_pc = pc + 1
                        while scan_pc < len(instructions) and not (
                            instructions[scan_pc].op == OpCode.FUNC_END and instructions[scan_pc].arg1 == fn_name
                        ):
                            scan_pc += 1
                        pc = scan_pc + 1
                        continue
                    else:
                        pc += 1
                        continue

                elif op == OpCode.FUNC_END:
                    if call_stack:
                        ret_frame = call_stack.pop()
                        return_dest = current_frame.return_dest
                        return_pc = current_frame.return_pc
                        current_frame = ret_frame
                        if return_dest:
                            set_val(return_dest, None)
                        pc = return_pc
                        continue
                    else:
                        break

                elif op == OpCode.ASSIGN:
                    v = get_val(inst.arg1)
                    set_val(inst.result, v)
                    pc += 1

                elif op == OpCode.ADD:
                    v1 = get_val(inst.arg1)
                    v2 = get_val(inst.arg2)
                    if isinstance(v1, str) or isinstance(v2, str):
                        set_val(inst.result, f"{v1}{v2}")
                    else:
                        set_val(inst.result, v1 + v2)
                    pc += 1

                elif op == OpCode.SUB:
                    v1 = get_val(inst.arg1)
                    v2 = get_val(inst.arg2)
                    set_val(inst.result, v1 - v2)
                    pc += 1

                elif op == OpCode.MUL:
                    v1 = get_val(inst.arg1)
                    v2 = get_val(inst.arg2)
                    set_val(inst.result, v1 * v2)
                    pc += 1

                elif op == OpCode.DIV:
                    v1 = get_val(inst.arg1)
                    v2 = get_val(inst.arg2)
                    if v2 == 0:
                        raise RuntimeError("Division by zero error at runtime.")
                    if isinstance(v1, int) and isinstance(v2, int):
                        set_val(inst.result, v1 // v2)
                    else:
                        set_val(inst.result, v1 / v2)
                    pc += 1

                elif op == OpCode.MOD:
                    v1 = get_val(inst.arg1)
                    v2 = get_val(inst.arg2)
                    if v2 == 0:
                        raise RuntimeError("Modulo by zero error at runtime.")
                    set_val(inst.result, v1 % v2)
                    pc += 1

                elif op == OpCode.NEG:
                    v1 = get_val(inst.arg1)
                    set_val(inst.result, -v1)
                    pc += 1

                elif op == OpCode.NOT:
                    v1 = get_val(inst.arg1)
                    set_val(inst.result, not bool(v1))
                    pc += 1

                elif op == OpCode.EQ:
                    v1 = get_val(inst.arg1)
                    v2 = get_val(inst.arg2)
                    set_val(inst.result, v1 == v2)
                    pc += 1

                elif op == OpCode.NE:
                    v1 = get_val(inst.arg1)
                    v2 = get_val(inst.arg2)
                    set_val(inst.result, v1 != v2)
                    pc += 1

                elif op == OpCode.LT:
                    v1 = get_val(inst.arg1)
                    v2 = get_val(inst.arg2)
                    set_val(inst.result, v1 < v2)
                    pc += 1

                elif op == OpCode.LE:
                    v1 = get_val(inst.arg1)
                    v2 = get_val(inst.arg2)
                    set_val(inst.result, v1 <= v2)
                    pc += 1

                elif op == OpCode.GT:
                    v1 = get_val(inst.arg1)
                    v2 = get_val(inst.arg2)
                    set_val(inst.result, v1 > v2)
                    pc += 1

                elif op == OpCode.GE:
                    v1 = get_val(inst.arg1)
                    v2 = get_val(inst.arg2)
                    set_val(inst.result, v1 >= v2)
                    pc += 1

                elif op == OpCode.AND:
                    v1 = get_val(inst.arg1)
                    v2 = get_val(inst.arg2)
                    set_val(inst.result, bool(v1) and bool(v2))
                    pc += 1

                elif op == OpCode.OR:
                    v1 = get_val(inst.arg1)
                    v2 = get_val(inst.arg2)
                    set_val(inst.result, bool(v1) or bool(v2))
                    pc += 1

                elif op == OpCode.LABEL:
                    pc += 1

                elif op == OpCode.JUMP:
                    target = str(inst.arg1)
                    if target in label_map:
                        pc = label_map[target]
                    else:
                        raise RuntimeError(f"Jump to unknown label '{target}'")

                elif op == OpCode.JUMP_IF_TRUE:
                    cond = get_val(inst.arg1)
                    if bool(cond):
                        target = str(inst.arg2)
                        pc = label_map[target]
                    else:
                        pc += 1

                elif op == OpCode.JUMP_IF_FALSE:
                    cond = get_val(inst.arg1)
                    if not bool(cond):
                        target = str(inst.arg2)
                        pc = label_map[target]
                    else:
                        pc += 1

                elif op == OpCode.PARAM:
                    param_queue.append(get_val(inst.arg1))
                    pc += 1

                elif op == OpCode.CALL:
                    callee = str(inst.arg1)
                    num_args = int(inst.arg2) if inst.arg2 is not None else len(param_queue)

                    if callee not in func_map:
                        raise RuntimeError(f"Call to undefined function '{callee}'")

                    args_passed = param_queue[-num_args:] if num_args > 0 else []
                    param_queue = param_queue[:-num_args] if num_args > 0 else []

                    call_stack.append(current_frame)
                    new_frame = StackFrame(
                        fn_name=callee,
                        return_pc=pc + 1,
                        return_dest=inst.result,
                        locals={},
                    )

                    for i, arg_val in enumerate(args_passed):
                        new_frame.locals[f"param_{i}"] = arg_val

                    current_frame = new_frame
                    pc = func_map[callee] + 1

                elif op == OpCode.RETURN:
                    ret_val = get_val(inst.arg1) if inst.arg1 is not None else None
                    if call_stack:
                        return_dest = current_frame.return_dest
                        return_pc = current_frame.return_pc
                        current_frame = call_stack.pop()
                        if return_dest:
                            set_val(return_dest, ret_val)
                        pc = return_pc
                    else:
                        break

                elif op == OpCode.PRINT:
                    val = get_val(inst.arg1)
                    if isinstance(val, bool):
                        out_str = "true" if val else "false"
                    else:
                        out_str = str(val)
                    stdout_lines.append(out_str)
                    pc += 1

                else:
                    pc += 1

        except Exception as e:
            return ExecutionResult(
                output="\n".join(stdout_lines),
                steps_executed=steps,
                final_variables={**globals_env, **current_frame.locals},
                return_code=1,
                success=False,
                error_message=str(e),
                execution_trace=trace,
            )

        merged_vars = {**globals_env, **current_frame.locals}
        clean_vars = {k: v for k, v in merged_vars.items() if not k.startswith("param_")}

        return ExecutionResult(
            output="\n".join(stdout_lines),
            steps_executed=steps,
            final_variables=clean_vars,
            return_code=0,
            success=True,
            execution_trace=trace,
        )
