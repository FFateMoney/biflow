from adapters.base_adapter import BaseAdapter
from core.node import WorkflowNode
from pathlib import Path

#把adapt改成map形式 01完成

class BwaAdapter(BaseAdapter):
    def __init__(self, config=None, sample_data=None):
        super().__init__(config or {}, sample_data)

    def adapt(self, node: WorkflowNode) -> WorkflowNode:
        operation = node.name.lower()

        if operation in ("indexing", "bwa_index"):
            return self._build_index(node)
        if operation in ("batch_mapping", "bwa_mem"):
            return self._build_mem(node)
        raise ValueError(f"Unsupported BWA operation: {operation}")

    def _build_index(self, node: WorkflowNode):
        bwa_path = node.params["bwa_path"]
        ref_path = Path(node.params["reference"])
        output_prefix = Path(node.output_dir) / node.params["prefix"]
        output_prefix.parent.mkdir(parents=True, exist_ok=True)

        node.commands = [
            [
                bwa_path,
                "index",
                "-p",
                str(output_prefix),
                str(ref_path),
            ]
        ]
        return node

    def _build_mem(self, node: WorkflowNode):
        bwa_path = node.params["bwa_path"]
        index_prefix = node.params["index_prefix"]
        platform = node.params["platform"]
        breeds = node.params.get("breeds") or []
        samples = node.params.get("samples") or []
        if not breeds or not samples:
            raise ValueError("Missing breeds or samples in params")

        commands = []
        base_dir = Path(node.input_dir["base"])
        output_dir = Path(node.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for breed in breeds:
            breed_dir = base_dir / breed
            if not breed_dir.exists():
                raise FileNotFoundError(f"目录不存在: {breed_dir}")
            for sample_id in samples:
                read1 = breed_dir / f"{breed}{sample_id}_1_trimmed.fq.gz"
                read2 = breed_dir / f"{breed}{sample_id}_2_trimmed.fq.gz"
                output_sam = output_dir / f"{breed}{sample_id}.sam"
                rg = f"@RG\\tID:{breed}{sample_id}\\tSM:{breed}{sample_id}\\tPL:{platform}"

                commands.append(
                    [
                        bwa_path,
                        "mem",
                        "-t",
                        str(node.params.get("threads", 4)),
                        "-R",
                        rg,
                        "-o",
                        str(output_sam),
                        index_prefix,
                        str(read1),
                        str(read2),
                    ]
                )
        node.commands = commands
        return node