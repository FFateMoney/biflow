# adapters/adapter_factory.py

from adapters.samtools_adapter import SamtoolsAdapter
from adapters.test_adapter import TestAdapter
from adapters.fastqc_adapter import FastQCAdapter
from adapters.multiqc_adapter import MultiQCAdapter
from adapters.trimgalore_adapter import TrimGaloreAdapter
from adapters.bwa_adapter import BwaAdapter
from adapters.bowtie2_adapter import Bowtie2Adapter
from adapters.picard_adapter import PicardAdapter
from core.node import WorkflowNode

def get_adapter(node: WorkflowNode):
    tool = node.tool.lower()  # 小写防止大小写问题

    adapter_map = {
        "samtools": SamtoolsAdapter,
        "test": TestAdapter,
        "fastqc": FastQCAdapter,
        "multiqc": MultiQCAdapter,
        "trim_galore": TrimGaloreAdapter,
        "bowtie2": Bowtie2Adapter,
        "bwa": BwaAdapter,
        "samtools_sort": SamtoolsAdapter,
        "picard": PicardAdapter,
        # "bwa": BwaAdapter,
        # "bcftools": BcftoolsAdapter,
    }

    if tool not in adapter_map:
        raise ValueError(f"No adapter found for tool: '{tool}'")

    return adapter_map[tool]()