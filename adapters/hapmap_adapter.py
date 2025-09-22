# adapters/hapmap_adapter.py
from adapters.base_adapter import BaseAdapter
from core.node import WorkflowNode
from pathlib import Path

#把目前的adapt拆分，用其它函数写具体的任务

class HapmapAdapter(BaseAdapter):
    def __init__(self, config=None, sample_data=None):
        super().__init__(config or {}, sample_data)

    def adapt(self, node: WorkflowNode) -> WorkflowNode:
        perl_path = node.params["perl_path"]
        script_path = node.params["script_path"]
        vcf_in = Path(node.input_dir["vcf"])
        out_dir = Path(node.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            perl_path,
            script_path,
            str(vcf_in),
            str(out_dir)
        ]
        node.commands = [cmd]
        return node