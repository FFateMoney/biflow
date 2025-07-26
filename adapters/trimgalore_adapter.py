from adapters.base_adapter import BaseAdapter
from core.node import WorkflowNode


class TrimGaloreAdapter(BaseAdapter):
    """Trim Galore序列修剪适配器 - 基于Read_trimmer.pl的TrimGalore函数"""

    def adapt(self, node: WorkflowNode) -> WorkflowNode:
        operation = node.name.lower()

        operation_map = {
            "trim_galore": self._trim_galore
        }

        if operation not in operation_map:
            raise ValueError(f"Unsupported Trim Galore operation: {operation}")

        return operation_map[operation](node)

    def _trim_galore(self, node: WorkflowNode) -> WorkflowNode:
        """
        Trim Galore序列修剪 - 对应Perl脚本中的TrimGalore函数
        参数：params:trim_galore_path,cores,input_files,sample_name,additional_params
        """
        trim_galore_path = node.params.get("trim_galore_path")
        cores = node.params.get("cores", 8)
        input_files = node.params.get("input_files", "")  # 对应$input参数
        sample_name = node.params.get("sample_name", "")  # 对应$indiv参数
        additional_params = node.params.get("additional_params", "")  # 附加参数

        # 构建命令 - 完全按照Perl脚本的格式
        command = [
            trim_galore_path,
            additional_params,
            "--gzip",
            "--paired",
            "--cores", str(cores),
            input_files,
            "2>", f"{sample_name}.log"
        ]

        # 清理空字符串参数
        command = [arg for arg in command if arg.strip()]

        node.commands.append(command)
        return node