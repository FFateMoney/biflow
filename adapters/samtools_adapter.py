from base_adapter import BaseAdapter
from core.node import WorkflowNode


class SamtoolsAdapter(BaseAdapter):
    def adapt(self, node: WorkflowNode) -> WorkflowNode:
        operation = node.name.lower()  # node的name即是操作

        # 映射操作名到函数
        operation_map = {
            "samtools_sort": self._build_sort,
            "samtools_faidx": self._build_faidx
        }

        if operation not in operation_map:
            raise ValueError(f"Unsupported samtools operation: {operation}")

        return operation_map[operation](node)

    def _build_sort(self, node: WorkflowNode) -> WorkflowNode:

        return node

    def _build_faidx(self, node: WorkflowNode) -> WorkflowNode:
        reference = node.pararm.get("reference")
        samtools_path = node.pararm.get("samtools_path")
        node.commands = [samtools_path, "faidx", reference]
        return node
