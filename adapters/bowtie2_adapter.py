from adapters.base_adapter import BaseAdapter
from pathlib import Path

from core.node import WorkflowNode

#缺少adapt 01完成

class Bowtie2Adapter(BaseAdapter):
    def adapt(self, node: WorkflowNode) -> WorkflowNode:
        operation = node.subcommand.lower()  # node的name即是操作

        # 映射操作名到函数
        operation_map = {
            "indexing": self.indexing,
            "mapping" : self.mapping,
        }

        if operation not in operation_map:
            raise ValueError(f"Unsupported bowtie2 operation: {operation}")

        return operation_map[operation](node)

    def __init__(self, config=None, sample_data=None):
        super().__init__(config or {}, sample_data)


    def indexing(self, node: WorkflowNode):
        """构建Bowtie2索引"""
        bowtie2_path = node.params["bowtie2_path"]
        threads = node.params.get("threads", 4)
        ref_path = Path(node.params["reference"])
        index_dir = Path(node.output_dir) / "ref"
        index_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            bowtie2_path,
            "-build",
            str(ref_path),
            str(index_dir / "ref"),
            f"--threads {threads}",
        ]
        node.commands = [cmd]
        return node

    def mapping(self, node: WorkflowNode):
        """执行Bowtie2比对"""
        bowtie2_path = node.params["bowtie2_path"]
        threads = node.params.get("threads", 4)
        index_dir = Path(node.input_dir["index"])
        read1 = Path(node.input_dir["read1"])
        read2 = Path(node.input_dir["read2"])
        output_dir = Path(node.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            bowtie2_path,
            "-p",
            str(threads),
            "-x",
            str(index_dir / "ref"),
            "-1",
            str(read1),
            "-2",
            str(read2),
            "-S",
            str(output_dir / f"{node.params['sample']}.sam"),
        ]
        node.commands = [cmd]
        return node