# adapters/plink_adapter.py
from adapters.base_adapter import BaseAdapter
from core.node import WorkflowNode
from pathlib import Path

class PlinkAdapter(BaseAdapter):
    def __init__(self, config=None, sample_data=None):
        super().__init__(config or {}, sample_data)

    def adapt(self, node: WorkflowNode) -> WorkflowNode:
        plink_path = node.params["plink_path"]
        vcf_in = Path(node.input_dir["vcf"])
        out_dir = Path(node.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        
        base_name = vcf_in.stem
        if base_name.endswith('.vcf.gz'):
            base_name = base_name[:-7]
        
        # 构建PLINK命令
        cmd = [
            plink_path,
            "--vcf", str(vcf_in),
            "--make-bed",
            "--geno", str(node.params.get("geno", 0.01)),
            "--maf", str(node.params.get("maf", 0.05)),
            "--hwe", str(node.params.get("hwe", 1e-6)),
            "--chr-set", str(node.params.get("chr-set", 1)),
            "--out", str(out_dir / base_name)
        ]
        
        # 添加染色体过滤参数
        if "allow_chr" in node.params:
            cmd.extend(["--chr", node.params["allow_chr"]])
        elif "not_allow_chr" in node.params:
            cmd.extend(["--not-chr", node.params["not_allow_chr"]])
        
        node.commands = [cmd]
        return node