# adapters/vcftools_adapter.py
from adapters.base_adapter import BaseAdapter
from core.node import WorkflowNode
from pathlib import Path

#把目前的adapt拆分，用其它函数写具体的任务
#03结束

class VcftoolsAdapter(BaseAdapter):
    def __init__(self, config=None, sample_data=None):
        super().__init__(config or {}, sample_data)

    def adapt(self, node: WorkflowNode) -> WorkflowNode:
        vcftools_path = node.params["vcftools_path"]
        vcf_in = Path(node.input_dir["vcf"])
        out_dir = Path(node.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        
        base_name = vcf_in.stem
        if base_name.endswith('.vcf'):
            base_name = base_name[:-4]
        
        # 根据参数决定过滤方式
        if "allow_chr" in node.params:
            new_vcf = f"{base_name}.allow_chr.vcf"
            cmd = [
                vcftools_path,
                "--gzvcf", str(vcf_in),
                "--chr", node.params["allow_chr"],
                "--out", str(out_dir / new_vcf),
                "--recode"
            ]
        elif "not_allow_chr" in node.params:
            new_vcf = f"{base_name}.not_allow_chr.vcf"
            cmd = [
                vcftools_path,
                "--gzvcf", str(vcf_in),
                "--not-chr", node.params["not_allow_chr"],
                "--out", str(out_dir / new_vcf),
                "--recode"
            ]
        else:
            new_vcf = f"{base_name}.original.vcf"
            cmd = [
                vcftools_path,
                "--gzvcf", str(vcf_in),
                "--out", str(out_dir / new_vcf),
                "--recode"
            ]
        
        # 添加压缩和索引命令
        output_vcf = out_dir / f"{new_vcf}.recode.vcf"
        compress_cmd = f"bgzip -f {output_vcf}"
        index_cmd = f"tabix -p vcf {output_vcf}.gz"
        
        node.commands = [cmd, compress_cmd, index_cmd]
        return node