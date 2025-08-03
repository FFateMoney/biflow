from adapters.base_adapter import BaseAdapter
from core.node import WorkflowNode
from pathlib import Path

class BwaAdapter(BaseAdapter):
    def __init__(self, config, sample_data=None):
        self.config = config
        self.sample_data = sample_data

    def adapt(self, node: WorkflowNode) -> WorkflowNode:
        operation = node.name.lower()

        operation_map = {
            "indexing": self._build_index,
            "batch_mapping": self._build_mem,
            "mapping": self._build_mem
        }

        if operation in operation_map:
            return operation_map[operation](node)

        if "index" in operation:
            return self._build_index(node)
        if "map" in operation or "mem" in operation:
            return self._build_mem(node)

        raise ValueError(f"Unsupported BWA operation: {operation}")

    def _build_index(self, node: WorkflowNode):
        required_params = ["bwa_path", "reference", "prefix"]
        for param in required_params:
            if param not in node.params:
                raise ValueError(f"Missing required parameter: '{param}'")

        ref_path = Path(node.params["reference"])
        output_prefix = Path(node.output_dir) / node.params["prefix"]
        output_prefix.parent.mkdir(parents=True, exist_ok=True)

        command = (
            f"{node.params['bwa_path']} index "
            f"-p {output_prefix} "
            f"{ref_path}"
        )
        node.commands = [command]
        return node

    def _build_mem(self, node: WorkflowNode):
        required_params = ["bwa_path", "index_prefix", "platform"]
        for param in required_params:
            if param not in node.params:
                raise ValueError(f"Missing required parameter: '{param}'")

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
                raise FileNotFoundError(f"品种目录不存在: {breed_dir}")

            for sample_id in samples:
                read1 = breed_dir / f"{breed}{sample_id}_1_trimmed.fq.gz"
                read2 = breed_dir / f"{breed}{sample_id}_2_trimmed.fq.gz"
                output_sam = output_dir / f"{breed}{sample_id}.sam"
                read_group = f"@RG\\tID:{breed}{sample_id}\\tSM:{breed}{sample_id}\\tPL:{node.params['platform']}"

                command = (
                    f"{node.params['bwa_path']} mem "
                    f"-t {node.params.get('threads', 4)} "
                    f"-R '{read_group}' "
                    f"-o {output_sam} "
                    f"{node.params['index_prefix']} "
                    f"{read1} {read2}"
                )
                commands.append(command)

        node.commands = commands
        return node