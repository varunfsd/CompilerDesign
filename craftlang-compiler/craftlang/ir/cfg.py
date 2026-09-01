"""Control Flow Graph (CFG) construction and visualization."""

from typing import List, Dict, Any, Optional
from .instructions import TACInstruction, OpCode
from .basic_block import BasicBlock, BasicBlockBuilder


class ControlFlowGraph:
    """Represents a Control Flow Graph of interconnected Basic Blocks."""

    def __init__(self, blocks: List[BasicBlock]):
        self.blocks: List[BasicBlock] = blocks
        self._build_edges()

    def _build_edges(self) -> None:
        if not self.blocks:
            return

        # Map labels and block names to blocks
        label_to_block: Dict[str, BasicBlock] = {}
        for block in self.blocks:
            label_to_block[block.name] = block
            leader = block.get_leader_label()
            if leader:
                label_to_block[leader] = block

        for i, block in enumerate(self.blocks):
            if not block.instructions:
                continue

            last = block.instructions[-1]

            if last.op == OpCode.JUMP:
                target_label = str(last.arg1)
                if target_label in label_to_block:
                    target_block = label_to_block[target_label]
                    self._add_edge(block, target_block)

            elif last.op in (OpCode.JUMP_IF_TRUE, OpCode.JUMP_IF_FALSE):
                target_label = str(last.arg2)
                if target_label in label_to_block:
                    target_block = label_to_block[target_label]
                    self._add_edge(block, target_block)
                # Fallthrough to next sequential block
                if i + 1 < len(self.blocks):
                    self._add_edge(block, self.blocks[i + 1])

            elif last.op == OpCode.RETURN:
                # Terminal block - no outgoing edges
                pass

            else:
                # Sequential fallthrough
                if i + 1 < len(self.blocks):
                    self._add_edge(block, self.blocks[i + 1])

    def _add_edge(self, src: BasicBlock, dst: BasicBlock) -> None:
        if dst not in src.successors:
            src.successors.append(dst)
        if src not in dst.predecessors:
            dst.predecessors.append(src)

    def to_mermaid(self) -> str:
        """Converts the CFG into a clean Mermaid flowchart."""
        lines = ["graph TD"]
        for block in self.blocks:
            # Build node label with instructions
            inst_lines = []
            for inst in block.instructions:
                clean_str = inst.format().strip().replace('"', "'").replace('<', '&lt;').replace('>', '&gt;')
                inst_lines.append(clean_str)
            content = "<br/>".join(inst_lines) if inst_lines else "(empty)"
            lines.append(f'    {block.name}["<b>{block.name}</b><br/>{content}"]')

        for block in self.blocks:
            for succ in block.successors:
                lines.append(f"    {block.name} --> {succ.name}")

        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "blocks": [b.to_dict() for b in self.blocks],
            "mermaid": self.to_mermaid(),
        }


class CFGBuilder:
    """Helper to build a Control Flow Graph from TAC instructions."""

    @classmethod
    def build_from_instructions(cls, instructions: List[TACInstruction]) -> ControlFlowGraph:
        blocks = BasicBlockBuilder.build(instructions)
        return ControlFlowGraph(blocks)
