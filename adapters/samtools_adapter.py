from adapters.base_adapter import BaseAdapter
from core.node import WorkflowNode
from pathlib import Path


class SamtoolsAdapter(BaseAdapter):
    def __init__(self, config, sample_data=None):
        super().__init__(config, sample_data)

    def adapt(self, node: WorkflowNode) -> WorkflowNode:
        operation = node.name.lower()

        # 1. 优先精确映射
        operation_map = {
            "samtools_sort": self._build_sort,
            "samtools_faidx": self._build_faidx,
            "batch_sorting": self._build_sort,  # 新增兼容
            "sorting": self._build_sort,        # 新增兼容
        }

        if operation in operation_map:
            return operation_map[operation](node)

        # 2. 精确匹配失败后，按关键字模糊匹配（向后兼容）
        if "sort" in operation:
            return self._build_sort(node)
        if "faidx" in operation:
            return self._build_faidx(node)

        raise ValueError(f"Unsupported samtools operation: {operation}")

    def _build_sort(self, node: WorkflowNode) -> WorkflowNode:
        if "samtools_path" not in node.params:
            raise ValueError("Missing 'samtools_path' in params")

        breeds = node.params.get("breeds") or []
        samples = node.params.get("samples") or []

        # 如果参数中没有 breeds/samples，直接返回 node
        if not breeds or not samples:
            return node

        # 批量构造 sort 命令
        commands = []
        input_dir = Path(node.input_dir["input_sam"])
        output_dir = Path(node.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for breed in breeds:
            for sample_id in samples:
                input_sam = input_dir / f"{breed}{sample_id}.sam"
                output_bam = output_dir / f"{breed}{sample_id}.sort.bam"

                command = [
                    node.params["samtools_path"],
                    "sort",
                    "-@", str(node.params.get("threads", 4)),
                    "-o", str(output_bam),
                    str(input_sam)
                ]
                commands.append(" ".join(command))

        node.commands = commands
        return node

    def _build_faidx(self, node: WorkflowNode) -> WorkflowNode:
        reference = node.params.get("reference")
        samtools_path = node.params.get("samtools_path")
        if not reference or not samtools_path:
            raise ValueError("Missing 'reference' or 'samtools_path' in params")
        if not node.commands:
            node.commands = []
        node.commands.append(" ".join([samtools_path, "faidx", str(reference)]))
        return node