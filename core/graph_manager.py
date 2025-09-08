from pathlib import Path
from typing import Dict, List

import networkx as nx

from adapters.adapter_factory import get_adapter
from core.node import WorkflowNode

def build_graph(config_dict: Dict) -> nx.DiGraph:
    G = nx.DiGraph()
    G.graph.update(config_dict.get("global", {}))
    id_to_node = built_nodes(config_dict)

    for node_id, node in id_to_node.items():
        G.add_node(node_id, node=node)

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
    node_defs = config_dict.get("nodes", [])
    id_to_node = {}
    for node_cfg in node_defs:
        node_id = str(node_cfg.get("id"))
        name = node_cfg.get("name")
        tool = node_cfg.get("tool")
        input_dir = node_cfg.get("input_dir")
        output_dir = node_cfg.get("output_dir")
        log_dir = node_cfg.get("log_dir", "")
        parallelize = node_cfg.get("parallelize", False)

        params_list = node_cfg.get("params", [])
        params = {}
        for item in params_list:
            if isinstance(item, dict):
                params.update(item)
            else:
                raise TypeError(f"Invalid param item in node '{name}': {item}")

        processed_input_dir = built_input_path(input_dir)

        node = WorkflowNode(
            id=node_id,
            name=name,
            tool=tool,
            commands=[],
            input_dir=processed_input_dir,
            output_dir=Path(output_dir),
            log_dir=Path(log_dir),
            params=params,
            parallelize=parallelize
        )

        id_to_node[node_id] = node

    return id_to_node

def built_input_path(input_dir):
    processed_input_dir = None
    if isinstance(input_dir, str):
        processed_input_dir = Path(input_dir)
    elif isinstance(input_dir, list) and all(isinstance(item, dict) for item in input_dir):
        merged_dict = {}
        for item in input_dir:
            for key, value in item.items():
                if isinstance(value, str):
                    merged_dict[key] = Path(value)
                else:
                    merged_dict[key] = value
        processed_input_dir = merged_dict
    else:
        processed_input_dir = input_dir
    return processed_input_dir
