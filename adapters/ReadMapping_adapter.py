from adapters.base_adapter import BaseAdapter
from core.node import WorkflowNode
from adapters.readmapping_indexing import ReadMappingIndexingAdapter
from adapters.readmapping_mapping import ReadMappingMappingAdapter
from adapters.readmapping_sortbam import ReadMappingSortBamAdapter
from adapters.readmapping_markdup import ReadMappingMarkDuplicatesAdapter
from adapters.readmapping_addrg import ReadMappingAddReadGroupAdapter

class ReadMappingAdapter(BaseAdapter):
    def adapt(self, node: WorkflowNode) -> WorkflowNode:
        operation = node.name.lower()
        operation_map = {
            "indexing": ReadMappingIndexingAdapter().adapt,
            "mapping": ReadMappingMappingAdapter().adapt,
            "sort_bam": ReadMappingSortBamAdapter().adapt,
            "mark_duplicates": ReadMappingMarkDuplicatesAdapter().adapt,
            "add_readgroup": ReadMappingAddReadGroupAdapter().adapt,
        }
        if operation not in operation_map:
            raise ValueError(f"Unsupported readmapping operation: {operation}")
        return operation_map[operation](node)