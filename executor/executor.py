import logging
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

import networkx as nx

from core.node import WorkflowNode  # 你的节点类


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def run_command(step_name: str, command: List[str], log_dir: str, index: int):
    cmd_dir = os.path.join(log_dir, f"cmd_{index}")
    ensure_dir(cmd_dir)

    stdout_path = os.path.join(cmd_dir, "stdout.log")
    stderr_path = os.path.join(cmd_dir, "stderr.log")

    logging.info(f"[{step_name}] Running command[{index}]: {' '.join(command)}")
    logging.info(f"[{step_name}] Logs: stdout -> {stdout_path}, stderr -> {stderr_path}")

    with open(stdout_path, "w") as out_f, open(stderr_path, "w") as err_f:
        try:
            subprocess.run(
                command,
                check=True,
                stdout=out_f,
                stderr=err_f
            )
            logging.info(f"[{step_name}] Command[{index}] completed.")
        except subprocess.CalledProcessError as e:
            logging.error(f"[{step_name}] Command[{index}] failed with return code {e.returncode}")
            raise e
def execute_node(node: WorkflowNode):
    logging.info(f"===> Executing Node: {node.name} (parallel={node.parallelizable})")
    ensure_dir(node.log_dir)

    if node.parallelizable:
        with ThreadPoolExecutor(max_workers=len(node.commands)) as executor:
            futures = [
                executor.submit(run_command, node.name, cmd, node.log_dir, idx)
                for idx, cmd in enumerate(node.commands)
            ]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logging.error(f"[{node.name}] One command failed: {e}")
                    raise
    else:
        for idx, cmd in enumerate(node.commands):
            run_command(node.name, cmd, node.log_dir, idx)

def execute_graph(G: nx.DiGraph):

    parallel_nodes = G.graph.get("parallel")

    """
    参数：
        G: networkx.DiGraph，图中每个节点名应有属性 "node" = WorkflowNode 实例
        parallel_nodes: 是否并行执行同一层（图级并行）
    """
    assert nx.is_directed_acyclic_graph(G), "图中存在循环依赖，不能执行"

    layers = list(nx.topological_generations(G))  # 一层一层拓扑层次
    for i, layer in enumerate(layers):
        logging.info(f"--> Executing layer {i+1}/{len(layers)}: {layer}")
        if parallel_nodes:
            with ThreadPoolExecutor(max_workers=len(layer)) as executor:
                futures = [
                    executor.submit(execute_node, G.nodes[name]["node"])
                    for name in layer
                ]
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logging.error(f"[Layer {i+1}] Node execution failed: {e}")
                        raise
        else:
            for name in layer:
                execute_node(G.nodes[name]["node"])
