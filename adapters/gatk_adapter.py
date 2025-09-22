import os
from pathlib import Path

from adapters.base_adapter import BaseAdapter
from core.node import WorkflowNode

#完成

class GatkAdapter(BaseAdapter):
    def adapt(self, node: WorkflowNode) -> WorkflowNode:
        operation = node.name.lower()  # node的name即是操作

        # 映射操作名到函数
        operation_map = {
            "haplotype_caller": self._haplotypecaller,
            "combine_gvcf": self._combine_gvcf,
            "genotyping": self._genotyping,
            "variant_filtering": self._variant_filtering,
            "select_variants": self._select_variants,
            "varint_selection": self._varint_selection
        }

        if operation not in operation_map:
            raise ValueError(f"Unsupported gatk operation: {operation}")

        return operation_map[operation](node)

    '''
    参数：input_dir:reference,gvcf params:reference,java_path,memory,vcf_prefix,tool_path
    '''

    def _combine_gvcf(self, node: WorkflowNode):
        reference_path = (node.input_dir.get("reference") / node.params.get("reference")).as_posix()
        gvcf_dir: Path = node.input_dir.get("gvcf")
        command = [
            node.params.get("java_path"), "-Xmx", f"{node.params.get('memory')}g", "-jar", node.params.get("tool_path"),
            "-T", "CombineGVCFs", "--disable_auto_index_creation_and_locking_when_reading_rods",
            "-R", reference_path

        ]
        for f in os.listdir(gvcf_dir):
            if f.endswith(".g.vcf"):
                gvcf_path = gvcf_dir / f
                command += ["--variant", gvcf_path.as_posix()]
        command += [
            "-O", (node.output_dir / f"{node.params.get('vcf_prefix')}.variant.combined.g.vcf.gz").as_posix()
        ]
        node.commands.append(command)
        return node

    '''
    参数：input_dir.reference input_dir.bam java_path memory tool_path option_line th
    '''

    def _haplotypecaller(self, node: WorkflowNode):
        reference_path = (node.input_dir.get("reference") / node.params.get("reference")).as_posix()
        input_dir = node.input_dir.get("bam")
        output_dir = node.output_dir

        # 确保输出目录存在
        output_dir.mkdir(parents=True, exist_ok=True)

        # 遍历所有 .bam 文件
        for bam_file in input_dir.glob("*.bam"):
            bam_path = bam_file.as_posix()
            out_file = output_dir / f"{bam_file.stem}.variant.g.vcf"

            command = [
                node.params.get("java_path"), "-Xmx", f"{node.params.get('memory')}g",
                "-jar", node.params.get("tool_path"), "-T", "HaplotypeCaller",
                node.params.get("option_line"), "-nct", node.params.get("th"),
                "-R", reference_path, "-I", bam_path, "-O", out_file.as_posix(),
                "-ERC", "GVCF"
            ]

            node.commands.append(command)

        return node

    '''
    参数：input_dir:reference,vcf;params:java_path,memory,tool_path,vcf_prefix
    '''

    def _genotyping(self, node: WorkflowNode):
        reference_path = (node.input_dir.get("reference") / node.params.get("reference")).as_posix()
        input_path: Path = node.input_dir.get("vcf") / f"{node.params.get('vcf_prefix')}.variant.combined.gvcf"
        out_path: Path = node.output_dir / f"{node.params.get('vcf_prefix')}.variant.combined.GT.vcf"
        command = [
            node.params.get("java_path"), "-Xmx", f"{node.params.get('memory')}g", "-jar", node.params.get("tool_path"),
            "-T", "GenotypeGVCFs",
            "--disable_auto_index_creation_and_locking_when_reading_rods", "-R",
            reference_path, "--variant", input_path.as_posix(), "--out",
            out_path.as_posix()
        ]
        node.commands.append(command)
        return node

    '''
     参数：input_dir:reference,vcf;;params:java_path,memory,tool_path,vcf_prefix,filterExpression,option_line,reference
    '''

    def _variant_filtering(self, node: WorkflowNode):
        reference_path = (node.input_dir.get("reference") / node.params.get("reference")).as_posix()
        input_path: Path = node.input_dir.get("vcf") / f"{node.params.get('vcf_prefix')}.variant.combined.GT.SNP.vcf"
        out_path: Path = node.output_dir / f"{node.params.get('vcf_prefix')}.variant.combined.GT.SNP.tag.vcf"
        command = [
            node.params.get("java_path"), "-Xmx", f"{node.params.get('memory')}g", "-jar",
            node.params.get("tool_path"), "-T", "VariantFiltration",
            "--disable_auto_index_creation_and_locking_when_reading_rods",
            node.params.get("option_line"), "-R", reference_path, "--variant",
            input_path.as_posix(), "--filterName",
            "SNPFILTER", "--filterExpression", node.params.get("filter_expression"), "--out",
            out_path.as_posix()
        ]
        node.commands.append(command)
        return node

    '''
    参数：input_dir:reference,vcf;;params:java_path,memory,tool_path,vcf_prefix
    '''

    def _select_variants(self, node: WorkflowNode):
        reference_path = (node.input_dir.get("reference") / node.params.get("reference")).as_posix()
        input_path: Path = node.input_dir.get(
            "vcf") / f"{node.params.get('vcf_prefix')}.variant.combined.GT.SNP.tag.vcf"
        out_path: Path = node.output_dir / f"{node.params.get('vcf_prefix')}.variant.combined.GT.SNP.flt.vcf"
        command = [
            node.params.get("java_path"), "-Xmx", f"{node.params.get('memory')}g", "-jar",
            node.params.get("tool_path"), "-T", "SelectVariants",
            "--disable_auto_index_creation_and_locking_when_reading_rods",
            "-R", reference_path, "--variant", input_path.as_posix(), "-select", 'FILTER == "SNPFILTER"',
            "--invertSelect", "-o", out_path.as_posix()
        ]
        node.commands.append(command)
        return node

    '''
    参数： input: reference,vcf;;params: reference vcf_prefix java_path tool_path memory
    '''
    def _varint_selection(self, node: WorkflowNode):
        reference_path = (node.input_dir.get("reference") / node.params.get("reference")).as_posix()
        input_path: Path = node.input_dir.get("vcf") / f"{node.params.get('vcf_prefix')}.variant.combined.GT.vcf"
        output_path: Path = node.output_dir / f"{node.params.get('vcf_prefix')}.variant.combined.GT.SNP.vcf"
        command = [
            node.params.get("java_path"), "-Xmx", f"{node.params.get('memory')}g", "-jar",
            node.params.get("tool_path"), "-T", "SelectVariants",
            "--disable_auto_index_creation_and_locking_when_reading_rods", "-R",
            reference_path, "-variant", input_path,
            "selectType", "SNP", "-o", output_path
        ]
        node.commands.append(command)
        return node
