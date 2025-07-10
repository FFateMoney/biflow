from typing import List, Dict
from adapters.adapter_factory import get_adapter
class WorkflowNode:
    def __init__(self, name: str, commands: List[str],input_dir:str,output_dir:str,log_dir: str,pararm: dict,tool:str,parallelizable: bool = False):
        self.name = name
        self.commands = commands
        self.pararm = pararm
        self.tool = tool
        self.parallelizable = parallelizable
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.log_dir = log_dir

    def __repr__(self):
        return (
            f"WorkflowNode(name='{self.name}', "
            f"tool='{self.tool}', "
            f"commands={self.commands}, "
            f"parallelizable={self.parallelizable}, "
            f"log_dir='{self.log_dir}', "
             f"input_dir={self.input_dir},"
            f"pararm={self.pararm})"

        )

    @classmethod
    def built_nodes(cls, config_dict: Dict) -> Dict[str, "WorkflowNode"]:
        """从配置字典构建所有节点，返回 {节点名: WorkflowNode} 映射"""
        node_defs = config_dict.get("nodes", [])
        name_to_node = {}

        for node_cfg in node_defs:
            name = node_cfg.get("name")
            if not name:
                raise ValueError("Node missing 'name' field")

            tool = node_cfg.get("tool")
            if not tool:
                raise ValueError(f"Node '{name}' missing 'tool' field")

            parallelizable = node_cfg.get("parallel", False)

            # 合并 param 列表为字典
            params_list = node_cfg.get("params", [])
            pararm = {}
            for item in params_list:
                if isinstance(item, dict):
                    pararm.update(item)
                else:
                    raise TypeError(f"Invalid param item in node '{name}': {item}")

            node = cls(  # 使用 cls 构造当前类
                name=name,
                tool=tool,
                commands=[],
                input_dir=node_cfg.get("input_dir"),
                output_dir=node_cfg.get("output_dir"),
                log_dir="",
                pararm=pararm,
                parallelizable=parallelizable
            )
            adapter = get_adapter(node)
            node = adapter.adapt(node)
            name_to_node[name] = node

        return name_to_node
