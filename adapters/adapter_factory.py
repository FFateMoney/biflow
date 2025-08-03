# adapters/adapter_factory.py

from adapters.bwa_adapter import BwaAdapter
from adapters.bowtie2_adapter import Bowtie2Adapter
from adapters.samtools_adapter import SamtoolsAdapter
from adapters.picard_adapter import PicardAdapter
from adapters.test_adapter import TestAdapter  # 如需可添加

def get_adapter(tool_name: str, config=None, sample_data=None):
    """
    根据工具名获取对应适配器实例（大小写不敏感）
    """
    tool_name = tool_name.lower()

    adapter_map = {
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

    if tool_name not in adapter_map:
        raise ValueError(f"No adapter found for tool: '{tool_name}'")

    return adapter_map[tool_name](config, sample_data)