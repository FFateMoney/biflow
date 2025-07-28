from adapters.base_adapter import BaseAdapter
from core.node import WorkflowNode


class ReadMappingSortBamAdapter(BaseAdapter):
    def adapt(self, node: WorkflowNode) -> WorkflowNode:
        samtools = node.params.get("samtools")
        threads = node.params.get("threads")
        sample = node.params.get("sample")
        in_sam = node.input_dir.get("sam").as_posix()
        out_bam = (node.output_dir / f"{sample}.sort.bam").as_posix()
        log_file = (node.output_dir / f"02_sam2bam_{sample}.log").as_posix()

        command = [samtools, "sort", "-@", str(threads), "-o", out_bam, in_sam]
        node.commands.append((command, log_file))
        return node