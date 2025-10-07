from adapters.base_adapter import BaseAdapter
from core.node import WorkflowNode
from pathlib import Path

# 01完成 02完成

class SamtoolsAdapter(BaseAdapter):
    def __init__(self, config=None, sample_data=None):
        super().__init__(config or {}, sample_data)

    def adapt(self, node: WorkflowNode) -> WorkflowNode:
        operation = node.subcommand.lower()
        operation_map = {
            "sort" : self._sort,
            "faidx": self._samtools_faidx,
            "local_realignment" : self._samtools_local_realignment
        }
        if operation not in operation_map:
            raise ValueError(f"Unsupported samtools operation: {operation}")
        return operation_map[operation](node)

    def _sort(self, node: WorkflowNode):
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

    def _samtools_local_realignment(self, node: WorkflowNode):
        samtools_path: Path = Path(node.params.get("tool_path"))
        input_path: Path =  Path(node.input_dir.get("bam"))
        output_path = node.output_dir
        bam_files = list(Path(input_path).glob("*.bam"))
        th= node.params.get("th")

        commands = []
        for bam in bam_files:
            bam_str = bam.as_posix()
            output = output_path/bam_str.replace("bam","bai")
            command = [samtools_path.as_posix(),"index","-@",th,bam.as_posix(),output.as_posix()]
            print(command)
            commands.append(command)
        node.commands = commands
        return node