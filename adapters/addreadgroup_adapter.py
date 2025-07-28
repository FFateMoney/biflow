from adapters.base_adapter import BaseAdapter
from core.node import WorkflowNode

class ReadMappingAddReadGroupAdapter(BaseAdapter):
    def adapt(self, node: WorkflowNode) -> WorkflowNode:
        java = node.params.get("java")
        picard = node.params.get("picard")
        memory = node.params.get("memory")
        sample = node.params.get("sample")
        platform = node.params.get("platform")
        platform_unit = node.params.get("platform_unit")
        marked_bam = node.input_dir.get("bam").as_posix()
        out_bam = (node.output_dir / f"{sample}.addRG.marked.sort.bam").as_posix()
        log_file = (node.output_dir / f"02_readgroup_{sample}.log").as_posix()

        command = [
            java, "-Xmx", f"{memory}g", "-jar", picard,
            "AddOrReplaceReadGroups",
            "I=" + marked_bam, "O=" + out_bam,
            f"RGID={sample}", f"RGSM={sample}", f"PL={platform}", f"PU={platform_unit}"
        ]
        node.commands.append((command, log_file))
        return node