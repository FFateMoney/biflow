import os
from pathlib import Path

from adapters.base_adapter import BaseAdapter
from core.node import WorkflowNode


class FastQCAdapter(BaseAdapter):
    """FastQC质量控制适配器 - 基于Stat_calculator.pl的fastqc函数"""

    def adapt(self, node: WorkflowNode) -> WorkflowNode:
        operation = node.name.lower()

        operation_map = {
            "fastqc": self._fastqc
        }

        if operation not in operation_map:
            raise ValueError(f"Unsupported FastQC operation: {operation}")

        return operation_map[operation](node)

    def _fastqc(self, node: WorkflowNode) -> WorkflowNode:
        """
        FastQC分析 - 对应Perl脚本中的fastqc函数
        参数：input_dir:fastq; params:fastqc_path,threads,file_pattern,flag
        flag=0: 原始数据分析, flag=1: 修剪后数据分析
        """
        fastqc_path = node.params.get("fastqc_path")
        input_dir = node.input_dir.get("fastq")
        output_dir = node.output_dir
        threads = node.params.get("threads", 1)
        flag = node.params.get("flag", 0)

        # 根据flag设置不同的文件匹配模式
        if flag == 0:
            # 原始数据分析
            file_pattern = node.params.get("file_pattern", "*.fastq*")
        else:
            # 修剪后数据分析
            file_pattern = node.params.get("file_pattern", "*_val_*.fq.gz")
            input_dir = node.input_dir.get("trimmed_data", input_dir)

        # 确保输出目录存在
        output_dir.mkdir(parents=True, exist_ok=True)

        # 批量处理所有匹配的FASTQ文件
        for fastq_file in input_dir.glob(file_pattern):
            command = [
                fastqc_path,
                "-f", "fastq",
                "-o", output_dir.as_posix(),
                "-t", str(threads),
                fastq_file.as_posix()
            ]

            # 添加日志重定向
            log_file = output_dir / f"{fastq_file.stem}.fastqc.log"
            command.extend(["2>", log_file.as_posix()])

            node.commands.append(command)

        return node