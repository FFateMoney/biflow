from adapters.base_adapter import BaseAdapter
from core.node import WorkflowNode
from pathlib import Path

class ReadMappingIndexingAdapter(BaseAdapter):
    def adapt(self, node: WorkflowNode) -> WorkflowNode:
        ref_fasta = (node.input_dir.get("reference") / node.params.get("reference")).as_posix()
        tool = node.params.get("tool")
        threads = node.params.get("threads")
        out_prefix = (node.output_dir / "ref").as_posix()
        log_file = (node.output_dir / "01_indexing.log").as_posix()

        if tool == "bwa":
            command = [tool, "index", "-p", out_prefix, ref_fasta]
        elif tool == "bowtie2":
            command = [tool + "-build", "--threads", str(threads), ref_fasta, out_prefix]
        else:
            raise ValueError(f"Unsupported tool: {tool}")

        node.commands.append((command, log_file))
        return node