from core.node import WorkflowNode
#from adapters.samtools_adapter import SamtoolsAdapter
from adapters.test_adapter import TestAdapter
#from adapters.fastqc_adapter import FastQCAdapter
#from adapters.multiqc_adapter import MultiQCAdapter
#from adapters.trimgalore_adapter import TrimGaloreAdapter
#from adapters.bwa_adapter import BwaAdapter
#from adapters.bowtie2_adapter import Bowtie2Adapter
#from adapters.picard_adapter import PicardAdapter
from adapters.vcftools_adapter import VcftoolsAdapter
from adapters.plink_adapter import PlinkAdapter
from adapters.hapmap_adapter import HapmapAdapter

ADAPTER_MAP = {
    #"samtools": SamtoolsAdapter,
   # "samtools_sort": SamtoolsAdapter,
    "test": TestAdapter,
   # "fastqc": FastQCAdapter,
   #"multiqc": MultiQCAdapter,
   # "trim_galore": TrimGaloreAdapter,
    #"bwa_index": BwaAdapter,
    #"bwa_mem": BwaAdapter,
    #"bwa": BwaAdapter,
    #"bowtie2": Bowtie2Adapter,
    #"picard_markduplicates": PicardAdapter,
    #"picard_addrg": PicardAdapter,
    #"picard": PicardAdapter,
    "vcftools": VcftoolsAdapter,
    "plink": PlinkAdapter,
    "hapmap": HapmapAdapter,
}

def get_adapter(node: WorkflowNode):
    tool = node.tool.lower()
    if tool not in ADAPTER_MAP:
        raise ValueError(f"No adapter found for tool: '{tool}'")
    return ADAPTER_MAP[tool]()