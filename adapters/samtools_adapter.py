from adapters.base_adapter import BaseAdapter
from core.node import WorkflowNode
from pathlib import Path

class SamtoolsAdapter(BaseAdapter):
    def __init__(self, config=None, sample_data=None):
        super().__init__(config or {}, sample_data)

    def adapt(self, node: WorkflowNode) -> WorkflowNode:
        operation = node.name.lower()
        if operation in ("batch_sorting", "samtools_sort"):
            return self._build_sort(node)
        raise ValueError(f"Unsupported samtools operation: {operation}")

    def _build_sort(self, node: WorkflowNode):
        samtools_path = node.params["samtools_path"]
        breeds = node.params.get("breeds") or []
        samples = node.params.get("samples") or []

        commands = []
        input_dir = Path(node.input_dir["input_sam"])
        output_dir = Path(node.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for breed in breeds:
            for sample_id in samples:
                input_sam = input_dir / f"{breed}{sample_id}.sam"
                output_bam = output_dir / f"{breed}{sample_id}.sort.bam"

                commands.append(
                    [
                        samtools_path,
                        "sort",
                        "-@",
                        str(node.params.get("threads", 4)),
                        "-o",
                        str(output_bam),
                        str(input_sam),
                    ]
                )
        node.commands = commands
        return node