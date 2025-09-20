import os
from collections import defaultdict
from pathlib import Path

from core.node import WorkflowNode


class LDdecay_adapter:
    def adapt(self, node: WorkflowNode) -> WorkflowNode:
        operation = node.name.lower()  # node的name即是操作

        # 映射操作名到函数
        operation_map = {

        }

        if operation not in operation_map:
            raise ValueError(f"Unsupported LDdecay operation: {operation}")

        return operation_map[operation](node)

    def _make_samplelist(sample_file, out_dir):
        """按群体生成样本列表文件 (.list)，并返回群体名列表"""
        os.makedirs(out_dir, exist_ok=True)
        breeds = defaultdict(list)

        # 读取样本文件并按 breed 分组
        with open(sample_file, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                sample, sex, breed = line.strip().split()
                breeds[breed].append(f"{breed}_{sample}")

        # 输出每个群体的 .list 文件
        for breed, samples in breeds.items():
            with open(os.path.join(out_dir, f"{breed}.list"), 'w') as out_f:
                out_f.write("\n".join(samples) + "\n")

        print(f"生成了 {len(breeds)} 个群体样本列表: {', '.join(breeds.keys())}")
        return list(breeds.keys())
    '''
    参数：params: tool_path MaxDist sample_path vcf_path;; output_path
    '''
    def _run_LD(self,node: WorkflowNode):
        sample_path: Path = node.params.get("sample_path")
        output_path: Path = node.output_dir
        breed_list = self._make_samplelist

