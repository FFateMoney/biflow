from adapters.base_adapter import BaseAdapter
from core.node import WorkflowNode
from pathlib import Path

class BwaAdapter(BaseAdapter):
    def __init__(self, config=None, sample_data=None):
        super().__init__(config or {}, sample_data)

    def adapt(self, node: WorkflowNode) -> WorkflowNode:
        operation = node.subcommand.lower()
        operation_map = {"index": self._index, "mem": self._mem}
        if operation not in operation_map:
            raise ValueError(f"Unsupported bwa operation: {operation}")
        return operation_map[operation](node)

    def _index(self, node: WorkflowNode):
        bwa_path = node.params["bwa_path"]
        ref_path = Path(node.params["reference"])
        output_prefix = Path(node.output_dir) / node.params["prefix"]
        output_prefix.parent.mkdir(parents=True, exist_ok=True)
        node.commands = [[bwa_path, "index", "-p", str(output_prefix), str(ref_path)]]
        return node

    def _mem(self, node: WorkflowNode):
        bwa_path     = node.params["bwa_path"]
        index_prefix = node.params["index_prefix"]
        platform     = node.params["platform"]
        breeds       = node.params.get("breeds") or []
        samples      = node.params.get("samples") or []
        if not breeds or not samples:
            raise ValueError("Missing breeds or samples in params")

        commands = []
        base_dir   = Path(node.input_dir["base"])
        output_dir = Path(node.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for breed in breeds:
            breed_dir = base_dir / breed
            if not breed_dir.exists():
                raise FileNotFoundError(f"目录不存在: {breed_dir}")
            for sample_id in samples:
                sample_prefix = f"{breed}{sample_id}"

                # 通配匹配 Trim Galore 实际输出
                read1_candidates = list(breed_dir.glob(f"{sample_prefix}*_val_1.fq.gz"))
                read2_candidates = list(breed_dir.glob(f"{sample_prefix}*_val_2.fq.gz"))
                if not (read1_candidates and read2_candidates):
                    print(f"Warning: 找不到配对文件 for {sample_prefix}")
                    continue

                read1 = read1_candidates[0]
                read2 = read2_candidates[0]
                output_sam = output_dir / f"{sample_prefix}.sam"

                # 关键修复：使用字面量 \\t  而非真实制表符
                rg = f"@RG\\tID:{sample_prefix}\\tSM:{sample_prefix}\\tPL:{platform}"

                commands.append([
                    bwa_path, "mem",
                    "-t", str(node.params.get("threads", 4)),
                    "-R", rg,
                    "-o", str(output_sam),
                    index_prefix,
                    str(read1), str(read2)
                ])

        node.commands = commands
        return node