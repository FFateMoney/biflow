from adapters import bowtie2_adapter, bwa_adapter, fastqc_adapter, gatk_adapter, hapmap_adapter, multiqc_adapter, \
    picard_adapter, plink_adapter, samtools_adapter, trimgalore_adapter, vcftoolsadapter
from core.node import WorkflowNode


ADAPTER_MAP = {
    "bowtie2" : bowtie2_adapter.Bowtie2Adapter,
    "bwa" : bwa_adapter.BwaAdapter,
    "fastqc" : fastqc_adapter.FastQCAdapter,
    "gatk" : gatk_adapter.GatkAdapter,
    "hapmap": hapmap_adapter.HapmapAdapter,
    "multiqc": multiqc_adapter.MultiQCAdapter,
    "picard" : picard_adapter.PicardAdapter,
    "plink": plink_adapter.PlinkAdapter,
    "samtools": samtools_adapter.SamtoolsAdapter,
    "trim_galore" : trimgalore_adapter.TrimGaloreAdapter,
    "vcftools": vcftools_adapter.VcftoolsAdapter
}

def get_adapter(node: WorkflowNode):
    tool = node.tool.lower()
    if tool not in ADAPTER_MAP:
        raise ValueError(f"No adapter found for tool: '{tool}'")
    return ADAPTER_MAP[tool]()