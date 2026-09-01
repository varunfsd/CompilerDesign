"""Basic Block partitioner for Three-Address Code."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .instructions import TACInstruction, OpCode


@dataclass
class BasicBlock:
    """A straight-line sequence of TAC instructions with single entry and single exit."""
    id: int
    name: str
    instructions: List[TACInstruction] = field(default_factory=list)
    predecessors: List["BasicBlock"] = field(default_factory=list)
    successors: List["BasicBlock"] = field(default_factory=list)

    def is_empty(self) -> bool:
        return len(self.instructions) == 0

    def get_leader_label(self) -> Optional[str]:
        if self.instructions and self.instructions[0].op == OpCode.LABEL:
            return str(self.instructions[0].arg1)
        return None

    def get_terminator(self) -> Optional[TACInstruction]:
        if self.instructions:
            return self.instructions[-1]
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "instructions": [inst.to_dict() for inst in self.instructions],
            "predecessors": [p.name for p in self.predecessors],
            "successors": [s.name for s in self.successors],
        }


class BasicBlockBuilder:
    """Partitions a flat list of TAC instructions into Basic Blocks."""

    @classmethod
    def build(cls, instructions: List[TACInstruction]) -> List[BasicBlock]:
        if not instructions:
            return []

        # 1. Identify leaders
        leaders = set()
        leaders.add(0)  # First instruction is always a leader

        jump_ops = (OpCode.JUMP, OpCode.JUMP_IF_TRUE, OpCode.JUMP_IF_FALSE, OpCode.RETURN)

        # Map label names to instruction indices
        label_map: Dict[str, int] = {}
        for idx, inst in enumerate(instructions):
            if inst.op == OpCode.LABEL:
                label_map[str(inst.arg1)] = idx

        for idx, inst in enumerate(instructions):
            if inst.op == OpCode.LABEL:
                leaders.add(idx)
            elif inst.op in jump_ops:
                # Instruction immediately following a jump is a leader
                if idx + 1 < len(instructions):
                    leaders.add(idx + 1)
                # Target of jump is a leader
                target_label = str(inst.arg1 if inst.op == OpCode.JUMP else inst.arg2)
                if target_label in label_map:
                    leaders.add(label_map[target_label])
            elif inst.op == OpCode.FUNC_START:
                leaders.add(idx)

        # 2. Partition into contiguous blocks
        sorted_leaders = sorted(leaders)
        blocks: List[BasicBlock] = []

        for i, start_idx in enumerate(sorted_leaders):
            end_idx = sorted_leaders[i + 1] if i + 1 < len(sorted_leaders) else len(instructions)
            block_insts = instructions[start_idx:end_idx]
            block_name = f"B{i}"
            if block_insts and block_insts[0].op == OpCode.LABEL:
                block_name = f"{block_insts[0].arg1}"
            elif block_insts and block_insts[0].op == OpCode.FUNC_START:
                block_name = f"fn_{block_insts[0].arg1}"

            blocks.append(BasicBlock(id=i, name=block_name, instructions=block_insts))

        return blocks
