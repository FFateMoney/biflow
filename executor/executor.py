import logging
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List

import networkx as nx

from adapters.adapter_factory import get_adapter
from core.node import WorkflowNode
from util.log_util import timestamp


def ensure_dir(path: str | Path) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def load_status(status_path: Path) -> dict:
    if not status_path.exists():
        return {"completed": False, "completed_cmds": 0}
    with open(status_path, "r", encoding="utf-8") as f:
        status = dict(line.strip().split("=", 1) for line in f if "=" in line)
    return {
        "completed": status.get("completed", "false") == "true",
        "completed_cmds": int(status.get("completed_cmds", 0)),
    }


def save_status(status_path: Path, completed: bool, completed_cmds: int) -> None:
    with open(status_path, "w", encoding="utf-8") as f:
        f.write(f"completed = {'true' if completed else 'false'}\n")
        f.write(f"completed_cmds = {completed_cmds}\n")


def run_command(command: list[str], log_path: Path) -> None:
    """执行纯列表命令，无 shell"""
    ensure_dir(log_path.parent)
    with open(log_path, "a", encoding="utf-8") as log_f:
        log_f.write(f"{timestamp()} 开始执行命令：{' '.join(command)}\n")
        try:
            result = subprocess.run(
                command,
                check=True,
                text=True,
                capture_output=True,
            )
            log_f.write(result.stdout or "")
            log_f.write(f"{timestamp()} 命令执行完成\n\n")
        except subprocess.CalledProcessError as e:
            log_f.write(e.stdout or "")
            log_f.write(e.stderr or "")
            log_f.write(f"{timestamp()} 命令执行失败，错误如下：\n{e.stderr or '无错误输出'}")
            raise


def execute_node(
    node: WorkflowNode,
    workflow_logger: logging.Logger,
) -> None:
    """执行单个节点：先让适配器生成 list[str] 命令，再统一执行"""
    adapter = get_adapter(node)
    node = adapter.adapt(node)
    print(node)  # 调试用

    node_dir = node.log_dir / f"{node.name}({node.id})"
    ensure_dir(node_dir)
    run_log_path = node_dir / "run.log"
    status_path = node_dir / "status.log"

    workflow_logger.info(f"{timestamp()} 开始运行节点：{node.name}({node.id})")

    # 保证 commands 为 list[list[str]]
    if not node.commands:
        commands = []
    elif isinstance(node.commands[0], str):
        commands = [node.commands]  # 单条
    else:
        commands = node.commands

    status = load_status(status_path)
    if status["completed"]:
        workflow_logger.info(f"{timestamp()} 跳过节点：{node.name}({node.id})，已完成")
        return

    try:
        if node.parallelize:
            with ThreadPoolExecutor(max_workers=len(commands)) as executor:
                futures = [
                    executor.submit(run_command, cmd, node_dir / f"cmd{i+1}.log")
                    for i, cmd in enumerate(commands)
                ]
                for future in as_completed(futures):
                    future.result()

            # 合并日志
            with open(run_log_path, "a", encoding="utf-8") as run_log:
                for i in range(len(commands)):
                    part_log = node_dir / f"cmd{i+1}.log"
                    if part_log.exists():
                        run_log.write(part_log.read_text(encoding="utf-8"))
                        part_log.unlink()
            save_status(status_path, completed=True, completed_cmds=len(commands))
        else:
            for i, cmd in enumerate(commands[status["completed_cmds"]:], start=status["completed_cmds"]):
                run_command(cmd, run_log_path)
                save_status(status_path, completed=False, completed_cmds=i + 1)
            save_status(status_path, completed=True, completed_cmds=len(commands))

        workflow_logger.info(f"{timestamp()} 节点 {node.name}({node.id}) 执行完成")
    except Exception as e:
        workflow_logger.error(
            f"{timestamp()} 节点 {node.name}({node.id}) 执行失败，请查看 {run_log_path}"
        )
        raise


def execute_graph(G: nx.DiGraph) -> None:
    """按拓扑层执行整张图"""
    parallel_nodes = G.graph.get("parallel", False)
    workflow_name = G.graph.get("flow_name", "workflow")
    log_dir = Path(G.graph.get("log_dir", "logs"))
    ensure_dir(log_dir)

    workflow_log_path = log_dir / f"{workflow_name}.log"

    logger = logging.getLogger("workflow")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    handler = logging.FileHandler(workflow_log_path, mode="a", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)

    logger.info(f"\n\n{timestamp()} 启动工作流：{workflow_name}")
    assert nx.is_directed_acyclic_graph(G), "图中存在循环依赖"

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

    logger.info(f"{timestamp()} 工作流 {workflow_name} 执行结束\n\n")