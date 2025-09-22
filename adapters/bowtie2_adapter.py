from adapters.base_adapter import BaseAdapter
from core.node import WorkflowNode
from pathlib import Path

class Bowtie2Adapter(BaseAdapter):
    def __init__(self, config=None, sample_data=None):
        super().__init__(config, sample_data)

    def adapt(self, node: WorkflowNode) -> WorkflowNode:
        operation = node.name.lower()

        if operation == "indexing":
            ref_key = "reference"
            if isinstance(node.input_dir, dict):
                ref_path = Path(node.input_dir[ref_key])
            else:
                ref_path = Path(node.input_dir)

            index_dir = Path(node.output_dir)
            index_dir.mkdir(parents=True, exist_ok=True)

            node.commands = [
                [
                    "bowtie2-build",
                    "--threads",
                    str(node.params.get("threads", 4)),
                    str(ref_path),
                    str(index_dir / "ref")
                ]
            ]
            return node

        elif operation == "mapping":
            raise NotImplementedError("Bowtie2 mapping not implemented yet")

        else:
            raise ValueError(f"Unsupported Bowtie2 operation: {operation}")