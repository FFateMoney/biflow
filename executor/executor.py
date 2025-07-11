import logging
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Union

import networkx as nx

from core.node import WorkflowNode  # 你的节点类
from util.log_util import timestamp


def ensure_dir(path: Union[str, Path]):
    path = Path(path)  # 无论是 str 还是 Path，统一转为 Path
    path.mkdir(parents=True, exist_ok=True)


def run_command(command: list[str], log_path: Path):
    ensure_dir(log_path.parent)  # 确保日志目录存在

    with open(log_path, "a", encoding="utf-8") as log_f:
        log_f.write(f"{timestamp()} 开始执行命令：{' '.join(command)}\n")

        try:
            result = subprocess.run(
                command,
                check=True,
                text=True,
                capture_output=True
            )
            if result.stdout:
                log_f.write(result.stdout)
            log_f.write(f"{timestamp()} 命令执行完成\n\n")

        except subprocess.CalledProcessError as e:
            log_f.write(e.stdout or "")
            log_f.write(e.stderr or "")
            log_f.write(f"{timestamp()} 命令执行失败，错误如下：\n")
            log_f.write((e.stderr or "无错误输出") + "\n")
            log_f.write("\n")
            raise e


def execute_node(node: WorkflowNode, workflow_logger: logging.Logger):
    workflow_logger.info(f"{timestamp()} 开始运行节点：{node.name}({node.id})")

    node_log_path = node.log_dir / f"{node.name}({node.id}).log"
    if isinstance(node.commands[0], str):
        commands = [node.commands]
    else:
        commands = node.commands

    try:
        if node.parallelize:
            workflow_logger.info("并行运行节点")
            with ThreadPoolExecutor(max_workers=len(commands)) as executor:
                futures = []
                for i, cmd in enumerate(commands):
                    cmd_log_path = node.log_dir / f"{node.name}({node.id})_cmd{i+1}.log"
                    futures.append(executor.submit(run_command, cmd, cmd_log_path))
                for future in as_completed(futures):
                    future.result()
            # 合并所有日志
            with open(node_log_path, "a", encoding="utf-8") as merged_log:
                for i in range(len(commands)):
                    cmd_log_path = node.log_dir / f"{node.name}({node.id})_cmd{i+1}.log"
                    if cmd_log_path.exists():
                        with open(cmd_log_path, "r", encoding="utf-8") as part_log:
                            merged_log.write(part_log.read())
                        cmd_log_path.unlink()
        else:
            for command in commands:
                run_command(command, node_log_path)

        workflow_logger.info(f"{timestamp()} 节点 {node.name}({node.id}) 执行完成")
    except Exception as e:
        workflow_logger.error(
            f"{timestamp()} 节点 {node.name}({node.id}) 执行失败，请查看 {node_log_path} 以获取详细信息"
        )
        raise



def execute_graph(G: nx.DiGraph):
    parallel_nodes = G.graph.get("parallel", False)
    workflow_name = G.graph.get("flow_name", "workflow")
    log_dir = Path(G.graph.get("log_dir", "logs"))
    ensure_dir(log_dir)

    # 图级日志文件路径为 logs/workflow_name.log
    workflow_log_path = log_dir / f"{workflow_name}.log"

    # 配置全局日志记录器
    logger = logging.getLogger("workflow")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()  # 避免重复添加 handler

    file_handler = logging.FileHandler(workflow_log_path, mode="a", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(file_handler)

    logger.info(f"{timestamp()} 启动工作流：{workflow_name}")

    assert nx.is_directed_acyclic_graph(G), "图中存在循环依赖，不能执行"

    layers = list(nx.topological_generations(G))

    for i, layer in enumerate(layers):
        logger.info(f"{timestamp()} 执行第 {i + 1}/{len(layers)} 层：{layer}")
        if parallel_nodes:
            with ThreadPoolExecutor(max_workers=len(layer)) as executor:
                futures = [
                    executor.submit(execute_node, G.nodes[name]["node"], logger)
                    for name in layer
                ]
                for future in as_completed(futures):
                    future.result()
        else:
            for name in layer:
                execute_node(G.nodes[name]["node"], logger)

    logger.info(f"{timestamp()} 工作流 {workflow_name} 执行结束")
