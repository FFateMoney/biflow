from adapters.base_adapter import BaseAdapter
from core.node import WorkflowNode
from pathlib import Path


class PicardAdapter(BaseAdapter):
    def __init__(self, config, sample_data=None):
        super().__init__(config, sample_data)

    def adapt(self, node: WorkflowNode) -> WorkflowNode:
        operation = node.name.lower()

        # 1. 精确映射（兼容原 ReadMapping）
        operation_map = {
            "batch_mark_duplicates":   self._build_mark_duplicates,
            "batch_add_read_groups":   self._build_add_read_groups,
            "picard_create_sequence_dictionary": self._build_create_sequence_dictionary,
        }

        if operation in operation_map:
            return operation_map[operation](node)

        # 2. 关键字模糊匹配（向后兼容扩展）
        if "markdup" in operation:
            return self._build_mark_duplicates(node)
        if "add_read_group" in operation or "addrg" in operation:
            return self._build_add_read_groups(node)
        if "dict" in operation:
            return self._build_create_sequence_dictionary(node)

        raise ValueError(f"Unsupported Picard operation: {node.name}")

    # ------------------------------------------------------------------
    # 原 ReadMapping 批处理逻辑
    # ------------------------------------------------------------------
    def _build_mark_duplicates(self, node: WorkflowNode):
        java = node.params.get("java_path", "java")
        jar = node.params["picard_path"]
        mem = node.params.get("memory", 4)

        breeds = node.params.get("breeds") or []
        samples = node.params.get("samples") or []
        if not breeds or not samples:
            # 向下兼容：无批量信息时返回空命令
            return node

        in_dir = Path(node.input_dir["input_bam"])
        out_dir = Path(node.output_dir)
        log_dir = Path("/RUN_DOCKER/output/logs")
        for d in (out_dir, log_dir):
            d.mkdir(parents=True, exist_ok=True)

        cmds = []
        for b in breeds:
            for s in samples:
                sample = f"{b}{s}"
                in_bam = in_dir / f"{sample}.sort.bam"
                out_bam = out_dir / f"{sample}.marked.sort.bam"
                metrics = out_dir / f"{sample}.dup_metrics.txt"
                logfile = log_dir / f"02_markdup_{sample}.log"

                cmd = (
                    f"{java} -Xmx{mem}g -jar {jar} MarkDuplicates "
                    f"I={in_bam} O={out_bam} M={metrics} "
                    f"REMOVE_DUPLICATES=false VALIDATION_STRINGENCY=LENIENT "
                    f"> {logfile} 2>&1"
                )
                cmds.append(cmd)
        node.commands = cmds
        return node

    def _build_add_read_groups(self, node: WorkflowNode):
        java = node.params.get("java_path", "java")
        jar = node.params["picard_path"]
        mem = node.params.get("memory", 4)
        pl = node.params.get("platform", "ILLUMINA")
        pu = node.params.get("platform_unit", "UNIT1")

        breeds = node.params.get("breeds") or []
        samples = node.params.get("samples") or []
        if not breeds or not samples:
            return node  # 向下兼容

        in_dir = Path(node.input_dir["input_bam"])
        out_dir = Path(node.output_dir)
        log_dir = Path("/RUN_DOCKER/output/logs")
        for d in (out_dir, log_dir):
            d.mkdir(parents=True, exist_ok=True)

        cmds = []
        for b in breeds:
            for s in samples:
                sample = f"{b}{s}"
                in_bam = in_dir / f"{sample}.marked.sort.bam"
                out_bam = out_dir / f"{sample}.addRG.marked.sort.bam"
                logfile = log_dir / f"02_readgroup_{sample}.log"

                cmd = (
                    f"{java} -Xmx{mem}g -jar {jar} AddOrReplaceReadGroups "
                    f"I={in_bam} O={out_bam} "
                    f"RGID={sample} RGLB={sample} RGPL={pl} "
                    f"RGPU={pu} RGSM={sample} "
                    f"> {logfile} 2>&1"
                )
                cmds.append(cmd)
        node.commands = cmds
        return node

    # ------------------------------------------------------------------
    # 新增：创建序列字典
    # ------------------------------------------------------------------
    def _build_create_sequence_dictionary(self, node: WorkflowNode):
        reference = node.params.get("reference")
        java_path = node.params.get("java_path", "java")
        picard_path = node.params.get("picard_path")
        if not reference or not picard_path:
            raise ValueError("Missing 'reference' or 'picard_path' in params")

        ref_path = Path(node.input_dir["reference"]) / reference
        dict_path = Path(node.output_dir) / reference.replace(".fa", ".dict")

        cmd = (
            f"{java_path} -jar {picard_path} CreateSequenceDictionary "
            f"R={ref_path} O={dict_path}"
        )
        node.commands = [cmd]
        return node