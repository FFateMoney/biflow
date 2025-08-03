import os
from pathlib import Path

from adapters.base_adapter import BaseAdapter
from core.node import WorkflowNode


class MultiQCAdapter(BaseAdapter):
    """MultiQC报告生成适配器 - 基于Stat_calculator.pl的multiqc函数"""

    def adapt(self, node: WorkflowNode) -> WorkflowNode:
        operation = node.name.lower()

        operation_map = {
            "multiqc": self._multiqc
        }

        if operation not in operation_map:
            raise ValueError(f"Unsupported MultiQC operation: {operation}")

        return operation_map[operation](node)

    def _multiqc(self, node: WorkflowNode) -> WorkflowNode:
        """
        生成MultiQC汇总报告 - 对应Perl脚本中的multiqc函数
        参数：params:multiqc_path
        """
        multiqc_path = node.params.get("multiqc_path")
        input_dir = node.input_dir
        output_dir = node.output_dir
        for item in os.listdir(input_dir):
            item_inpath = os.path.join(input_dir, item)
            item_inpath = Path(item_inpath)
            item_outpath = os.path.join(output_dir, item)
            item_outpath = Path(item_outpath)
            # 简单的multiqc命令，在当前目录执行
            command = [multiqc_path, item_inpath.as_posix(), '-o', item_outpath.as_posix()]
            node.commands.append(command)

        return node