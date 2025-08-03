# adapters/adapter_factory.py

from adapters import samtools_adapter
# 根据需要继续添加其它工具
from adapters.samtools_adapter import SamtoolsAdapter
from adapters.test_adapter import TestAdapter
from adapters.fastqc_adapter import FastQCAdapter
from adapters.multiqc_adapter import MultiQCAdapter
from adapters.trimgalore_adapter import TrimGaloreAdapter
from core.node import WorkflowNode

def get_adapter(node: WorkflowNode):
    tool = node.tool.lower()  # 小写防止大小写问题

    adapter_map = {
        "samtools": SamtoolsAdapter,
        "test": TestAdapter,
        "fastqc": FastQCAdapter,
        "multiqc": MultiQCAdapter,
        "trim_galore": TrimGaloreAdapter
        # "bwa": BwaAdapter,
        # "bcftools": BcftoolsAdapter,
    }

    if tool not in adapter_map:
        raise ValueError(f"No adapter found for tool: '{tool}'")

    return adapter_map[tool]()
