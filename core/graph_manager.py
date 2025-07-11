from pathlib import Path
from typing import Dict, Tuple, List

import networkx as nx

from adapters.adapter_factory import get_adapter
from core.node import WorkflowNode  # 确保 import 位置正确


def build_graph(config_dict: Dict) -> nx.DiGraph:
    """根据配置字典创建完整图结构（节点id为唯一标识，依赖也是id）"""
    G = nx.DiGraph()
    G.graph.update(config_dict.get("global", {}))


    id_to_node = built_nodes(config_dict)

    # 添加节点
    for node_id, node in id_to_node.items():
        G.add_node(node_id, node=node)

    # 添加依赖边
    for node_cfg in config_dict.get("nodes", []):
        current_id = str(node_cfg["id"])
        deps = node_cfg.get("dependencies")
        if not deps:
            continue
        if isinstance(deps, (int, str)):
            deps = [str(deps)]
        else:
            deps = [str(d) for d in deps]

        for dep_id in deps:
            if dep_id not in id_to_node:
                raise ValueError(f"Dependency id '{dep_id}' not found")
            G.add_edge(dep_id, current_id)

    return G


def built_nodes(config_dict: Dict) -> Dict[str, WorkflowNode]:
    """构建所有节点，返回 {节点id: WorkflowNode}"""
    node_defs = config_dict.get("nodes", [])
    id_to_node = {}

    for node_cfg in node_defs:
        node_id = str(node_cfg.get("id"))  # 确保是字符串
        if not node_id:
            raise ValueError("Node missing 'id' field")

        name = node_cfg.get("name")
        if not name:
            raise ValueError("Node missing 'name' field")

        tool = node_cfg.get("tool")
        if not tool:
            raise ValueError(f"Node '{name}' missing 'tool' field")

        input_dir = node_cfg.get("input_dir")
        output_dir = node_cfg.get("output_dir")
        if not input_dir or not output_dir:
            raise ValueError(f"Node '{name}' missing input/output dir")

        log_dir = node_cfg.get("log_dir", "")
        parallelize = node_cfg.get("parallelize", False)

        # 合并 params
        params_list = node_cfg.get("params", [])
        params = {}
        for item in params_list:
            if isinstance(item, dict):
                params.update(item)
            else:
                raise TypeError(f"Invalid param item in node '{name}': {item}")

        node = WorkflowNode(
            id=node_id,
            name=name,
            tool=tool,
            commands=[],
            input_dir=Path(input_dir),
            output_dir=Path(output_dir),
            log_dir=Path(log_dir),
            params=params,
            parallelize=parallelize
        )

        adapter = get_adapter(node)
        node = adapter.adapt(node)

        id_to_node[node_id] = node

    return id_to_node