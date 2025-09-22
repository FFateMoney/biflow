from adapters.base_adapter import BaseAdapter
from core.node import WorkflowNode
from pathlib import Path

class SamtoolsAdapter(BaseAdapter):
    def __init__(self, config=None, sample_data=None):
        super().__init__(config or {}, sample_data)

    def adapt(self, node: WorkflowNode) -> WorkflowNode:
        operation = node.name.lower()
        operation_map = {
            "batch_sorting" : self._build_sort,
            "samtools_sort" : self._build_sort,
            "samtools_fadix": self._samtools_faidx
        }
        if operation not in operation_map:
            raise ValueError(f"Unsupported samtools operation: {operation}")
        return operation_map[operation](node)

    def _build_sort(self, node: WorkflowNode):
        samtools_path = node.params["samtools_path"]
        breeds = node.params.get("breeds") or []
        samples = node.params.get("samples") or []

        commands = []
        input_dir = Path(node.input_dir["input_sam"])
        output_dir = Path(node.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for breed in breeds:
            for sample_id in samples:
                input_sam = input_dir / f"{breed}{sample_id}.sam"
                output_bam = output_dir / f"{breed}{sample_id}.sort.bam"

                commands.append(
                    [
                        samtools_path,
                        "sort",
                        "-@",
                        str(node.params.get("threads", 4)),
                        "-o",
                        str(output_bam),
                        str(input_sam),
                    ]
                )
        node.commands = commands
        return node


    def _samtools_faidx(self,node: WorkflowNode):
        samtools_path: Path = node.params.get("tool_path")
        intput_path: Path = (node.input_dir.get("reference") / node.params.get("reference")).as_posix()
        command = [
            samtools_path,"faidx",intput_path
        ]
        node.commands.append(command)
        return node

    def _samtools_local_realignment(self,node: WorkflowNode):
        samtools_path: Path = node.params.get("tool_path")
        input_path: Path = node.input_dir.get("bam")
        output_path = node.output_dir
        bam_files = list(Path(input_path).glob("*.bam"))
        th = node.params.get("th")
        commands = []
        for bam in bam_files:
            bam = input_path/bam
            bam_str = bam.as_posix()
            output = output_path/bam_str.replace("bam","bai")
            command = [samtools_path,"index","-@",th,bam,output]
            commands.append(command)
        node.commands = commands
        return node



