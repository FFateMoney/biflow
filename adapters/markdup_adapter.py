from adapters.base_adapter import BaseAdapter
from core.node import WorkflowNode

class ReadMappingMarkDuplicatesAdapter(BaseAdapter):
    def adapt(self, node: WorkflowNode) -> WorkflowNode:
        java = node.params.get("java")
        picard = node.params.get("picard")
        memory = node.params.get("memory")
        sample = node.params.get("sample")
        sorted_bam = node.input_dir.get("bam").as_posix()
        marked_bam = (node.output_dir / f"{sample}.marked.sort.bam").as_posix()
        metrics = (node.output_dir / f"{sample}.dup_metrics.txt").as_posix()
        log_file = (node.output_dir / f"02_markdup_{sample}.log").as_posix()

        command = [
            java, "-Xmx", f"{memory}g", "-jar", picard,
            "MarkDuplicates",
            "I=" + sorted_bam, "O=" + marked_bam, "M=" + metrics
        ]
        node.commands.append((command, log_file))
        return node