from adapters.base_adapter import BaseAdapter
from core.node import WorkflowNode
from pathlib import Path

class ReadMappingMappingAdapter(BaseAdapter):
    def adapt(self, node: WorkflowNode) -> WorkflowNode:
        ref_index = (node.input_dir.get("reference") / "ref").as_posix()
        fastq1 = node.input_dir.get("fastq1").as_posix()
        fastq2 = node.input_dir.get("fastq2").as_posix()
        tool = node.params.get("tool")
        threads = node.params.get("threads")
        sample = node.params.get("sample")
        out_sam = (node.output_dir / f"{sample}.sam").as_posix()
        log_file = (node.output_dir / f"01_mapping_{sample}.log").as_posix()

        if tool == "bwa":
            command = [
                tool, "mem", "-t", str(threads),
                "-R", f"@RG\\tID:{sample}\\tSM:{sample}\\tPL:ILLUMINA",
                ref_index, fastq1, fastq2,
                ">", out_sam
            ]
        elif tool == "bowtie2":
            command = [
                tool, "-p", str(threads),
                "-x", ref_index, "-1", fastq1, "-2", fastq2,
                "-S", out_sam
            ]
        else:
            raise ValueError(f"Unsupported tool: {tool}")

        node.commands.append((command, log_file))
        return node