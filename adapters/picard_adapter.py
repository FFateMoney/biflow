from adapters.base_adapter import BaseAdapter
from core.node import WorkflowNode


class PicardAdapter(BaseAdapter):
    def adapt(self, node: WorkflowNode) -> WorkflowNode:
        operation = node.name.lower()  # node的name即是操作

        # 映射操作名到函数
        operation_map = {
            "picard_create_sequence_dictionary": self._build_create_sequence_dictionary,

        }

        if operation not in operation_map:
            raise ValueError(f"Unsupported picard operation: {operation}")

        return operation_map[operation](node)

    def _build_create_sequence_dictionary(self, node: WorkflowNode):
        reference_path = (node.input_dir / node.params.get("reference")).as_posix()
        output_dir = (node.output_dir / node.params.get('reference').replace('.fa', '.dict')).as_posix()
        command = [
            node.params.get("java_path"), "-jar", f"R={reference_path}",
            f"O={output_dir}"
        ]
        node.commands.append(command)
        return node
