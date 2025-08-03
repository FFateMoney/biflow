# adapters/adapter_factory.py

from typing import Union
from adapters.bwa_adapter import BwaAdapter
from adapters.bowtie2_adapter import Bowtie2Adapter
from adapters.samtools_adapter import SamtoolsAdapter
from adapters.picard_adapter import PicardAdapter
from adapters.test_adapter import TestAdapter  

from core.node import WorkflowNode


# 统一小写映射
ADAPTER_MAP = {
    "bwa_index": BwaAdapter,
    "bwa_mem": BwaAdapter,
    "samtools_sort": SamtoolsAdapter,
    "picard_markduplicates": PicardAdapter,
    "picard_addrg": PicardAdapter,
    "bwa": BwaAdapter,
    "bowtie2": Bowtie2Adapter,
    "samtools": SamtoolsAdapter,
    "picard": PicardAdapter,
    "test": TestAdapter,
}


def get_adapter(
    tool_or_node: Union[str, WorkflowNode],
    config=None,
    sample_data=None,
):
    """
    支持两种调用方式：
    1. get_adapter("bwa", config, sample_data)
    2. get_adapter(node_obj)   # 自动提取 node.tool
    """
    if isinstance(tool_or_node, WorkflowNode):
        tool = tool_or_node.tool
        # 如果适配器需要从 node.params 取配置，可在此扩展
        config = config or {}  # 外部未传则给空
        sample_data = None     # 可按需扩展
    else:
        tool = tool_or_node

    tool = tool.lower()
    if tool not in ADAPTER_MAP:
        raise ValueError(f"No adapter found for tool: '{tool}'")

    return ADAPTER_MAP[tool](config, sample_data)