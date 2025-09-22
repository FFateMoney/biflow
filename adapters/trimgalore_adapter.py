import os
from pathlib import Path
from adapters.base_adapter import BaseAdapter
from core.node import WorkflowNode

#compelete

class TrimGaloreAdapter(BaseAdapter):
    """Trim Galore序列修剪适配器 - 基于Read_trimmer.pl的TrimGalore函数"""

    def adapt(self, node: WorkflowNode) -> WorkflowNode:
        operation = node.name.lower()

        operation_map = {
            "trim_galore": self._trim_galore
        }

        if operation not in operation_map:
            raise ValueError(f"Unsupported Trim Galore operation: {operation}")

        return operation_map[operation](node)

    def _trim_galore(self, node: WorkflowNode) -> WorkflowNode:
        """
        Trim Galore序列修剪 - 对应Perl脚本中的TrimGalore函数
        参数：input_dir:fastq; params:trim_galore_path,cores,additional_params,paired_pattern
        """
        trim_galore_path = node.params.get("trim_galore_path")
        input_dir = node.input_dir.get("fastq")
        output_dir = node.output_dir
        cores = node.params.get("cores", 8)
        additional_params = node.params.get("additional_params", "")
        paired_pattern = node.params.get("paired_pattern", "*_R1_*")  # 用于匹配R1文件的模式
        
        # 确保输出目录存在
        output_dir.mkdir(parents=True, exist_ok=True)
        for item in os.listdir(input_dir):
            item_inpath = os.path.join(input_dir, item)
            item_inpath = Path(item_inpath)
            item_outpath = os.path.join(output_dir, item)
            item_outpath = Path(item_outpath)
            # 确保输出目录存在
            item_outpath.mkdir(parents=True, exist_ok=True)
            # 批量处理所有匹配的配对端FASTQ文件
            for r1_file in item_inpath.glob(paired_pattern):
                # 根据R1文件推断R2文件
                r2_file = None
                r1_name = r1_file.name
                
                # 尝试多种配对模式
                for pattern_pair in [("_1.", "_2."), ("_R1.", "_R2."), ("_1_", "_2_")]:
                    r1_pattern, r2_pattern = pattern_pair
                    if r1_pattern in r1_name:
                        r2_name = r1_name.replace(r1_pattern, r2_pattern)
                        r2_candidates = list(item_inpath.glob(r2_name))
                        if r2_candidates:
                            r2_file = r2_candidates[0]
                            break
                
                if not r2_file:
                    print(f"Warning: No paired file found for {r1_file.name}")
                    continue  # 跳过没有配对文件的样本
                
                # 获取样本名称
                sample_name = r1_file.stem.split('_')[0]  # 简单提取样本名
                
                # 构建命令
                command = [
                    trim_galore_path,
                    "--gzip",
                    "--paired",
                    "--cores", str(cores),
                    "-o", item_outpath.as_posix(),
                    r1_file.as_posix(),
                    r2_file.as_posix()
                ]
                
                # 添加附加参数
                if additional_params and additional_params.strip():
                    # 将字符串参数分割并插入到固定参数之后
                    additional_args = additional_params.strip().split()
                    command = command[:1] + additional_args + command[1:]
                
                # # 添加日志重定向
                # log_file = output_dir / f"{sample_name}.trim.log"
                # command.extend(["2>&1", ">", log_file.as_posix()])
                
                node.commands.append(command)
        
        return node