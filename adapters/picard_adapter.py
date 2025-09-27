from adapters.base_adapter import BaseAdapter
from core.node import WorkflowNode
from pathlib import Path

#adapt修改为map形式，01结束 02结束

class PicardAdapter(BaseAdapter):
    def __init__(self, config=None, sample_data=None):
        super().__init__(config or {}, sample_data)

    def adapt(self, node: WorkflowNode) -> WorkflowNode:
        operation = node.subcommand.lower()  # node的name即是操作

        # 映射操作名到函数
        operation_map = {
            "mark_duplicates": self._mark_duplicates,
            "add_read_groups": self._add_read_groups,
            "create_sequence_dictionary": self._create_sequence_dictionary
        }

        if operation not in operation_map:
            raise ValueError(f"Unsupported picard operation: {operation}")

        return operation_map[operation](node)

    def _mark_duplicates(self, node: WorkflowNode):
        java = node.params.get("java_path", "java")
        jar = node.params["picard_path"]
        mem = node.params.get("memory", 4)
        breeds = node.params.get("breeds") or []
        samples = node.params.get("samples") or []

        commands = []
        in_dir = Path(node.input_dir["input_bam"])
        out_dir = Path(node.output_dir)
        log_dir = Path("/RUN_DOCKER/output/logs")
        for d in (out_dir, log_dir):
            d.mkdir(parents=True, exist_ok=True)

        for b in breeds:
            for s in samples:
                sample = f"{b}{s}"
                in_bam = in_dir / f"{sample}.sort.bam"
                out_bam = out_dir / f"{sample}.marked.sort.bam"
                metrics = out_dir / f"{sample}.dup_metrics.txt"
                logfile = log_dir / f"02_markdup_{sample}.log"

                commands.append(
                    [
                        java,
                        f"-Xmx{mem}g",
                        "-jar",
                        jar,
                        "MarkDuplicates",
                        "I=" + str(in_bam),
                        "O=" + str(out_bam),
                        "M=" + str(metrics),
                        "REMOVE_DUPLICATES=false",
                        "VALIDATION_STRINGENCY=LENIENT",
                    ]
                )
        node.commands = commands
        return node

    def _add_read_groups(self, node: WorkflowNode):
        java = node.params.get("java_path", "java")
        jar = node.params["picard_path"]
        mem = node.params.get("memory", 4)
        pl = node.params.get("platform", "ILLUMINA")
        pu = node.params.get("platform_unit", "UNIT1")
        breeds = node.params.get("breeds") or []
        samples = node.params.get("samples") or []

        commands = []
        in_dir = Path(node.input_dir["input_bam"])
        out_dir = Path(node.output_dir)
        log_dir = Path("/RUN_DOCKER/output/logs")  #不能写死
        for d in (out_dir, log_dir):
            d.mkdir(parents=True, exist_ok=True)

        for b in breeds:
            for s in samples:
                sample = f"{b}{s}"
                in_bam = in_dir / f"{sample}.marked.sort.bam"
                out_bam = out_dir / f"{sample}.addRG.marked.sort.bam"
                logfile = log_dir / f"02_readgroup_{sample}.log"   #未使用的变量

                commands.append(
                    [
                        java,
                        f"-Xmx{mem}g",
                        "-jar",
                        jar,
                        "AddOrReplaceReadGroups",
                        "I=" + str(in_bam),
                        "O=" + str(out_bam),
                        f"RGID={sample}",
                        f"RGLB={sample}",
                        f"RGPL={pl}",
                        f"RGPU={pu}",
                        f"RGSM={sample}",
                    ]
                )
        node.commands = commands
        return node

    def _create_sequence_dictionary(self, node: WorkflowNode):
        java = node.params.get("java_path", "java")
        jar = node.params["picard_path"]
        ref_name = node.params["reference"]
        ref_path = Path(node.input_dir["reference"]) / ref_name
        dict_path = Path(node.output_dir) / ref_name.replace(".fa", ".dict")

        node.commands = [
            [
                java,
                "-jar",
                jar,
                "CreateSequenceDictionary",
                "R=" + str(ref_path),
                "O=" + str(dict_path),
            ]
        ]
        return node