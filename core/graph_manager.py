from typing import Dict

import networkx as nx

from node import WorkflowNode




def build_graph(config_dict: Dict) -> nx.DiGraph:
    """根据配置字典创建完整图结构（含依赖关系）"""
    G = nx.DiGraph()

    # 保存全局字段（如 parallel）
    global_config = config_dict.get("global", {})
    G.graph.update(global_config)

    # 生成所有节点
    name_to_node = WorkflowNode.built_nodes(config_dict)

    # 加入节点到图
    for name, node in name_to_node.items():
        G.add_node(name, node=node)

    # 添加依赖边
    node_defs = config_dict.get("nodes", [])
    for node_cfg in node_defs:
        name = node_cfg["name"]
        deps = node_cfg.get("dependencies")

        if deps is None:
            continue
        if isinstance(deps, str):
            deps = [deps]
        elif not isinstance(deps, list):
            raise TypeError(f"Invalid dependencies format for node '{name}'")

        for dep in deps:
            G.add_edge(dep, name)

    return G

