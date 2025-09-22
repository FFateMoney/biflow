import logging
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Union, List

import networkx as nx

from adapters.adapter_factory import get_adapter
from core.node import WorkflowNode
from util.log_util import timestamp

def ensure_dir(path: Union[str, Path]):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)

def load_status(status_path: Path) -> dict:
    if not status_path.exists():
        return {"completed": False, "completed_cmds": 0}
    with open(status_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        status = {k.strip(): v.strip() for k, v in (line.split("=") for line in lines)}
        return {
            "completed": status.get("completed", "false") == "true",
            "completed_cmds": int(status.get("completed_cmds", 0))
        }

def save_status(status_path: Path, completed: bool, completed_cmds: int):
    with open(status_path, "w", encoding="utf-8") as f:
        f.write(f"completed = {'true' if completed else 'false'}\n")
        f.write(f"completed_cmds = {completed_cmds}\n")

# def run_command(command: List[str], log_path: Path):
#     ensure_dir(log_path.parent)
#     with open(log_path, "a", encoding="utf-8") as log_f:
#         log_f.write(f"{timestamp()} 开始执行命令：{' '.join(command)}\n")
#         try:
#             result = subprocess.run(command, check=True, text=True, capture_output=True)
#             log_f.write(result.stdout or "")
#             log_f.write(f"{timestamp()} 命令执行完成\n\n")
#         except subprocess.CalledProcessError as e:
#             log_f.write(e.stdout or "")
#             log_f.write(e.stderr or "")
#             log_f.write(f"{timestamp()} 命令执行失败，错误如下：\n{e.stderr or '无错误输出'}")
#             raise e

def run_command(command, run_log_path, output_file=None, working_dir=None):
    """
    执行命令，支持输出重定向和工作目录设置
    """
    try:
        with open(run_log_path, 'a') as log_file:
            log_file.write(f"[{timestamp()}] 开始执行命令：{' '.join(command) if isinstance(command, list) else command}\n")
            
            if output_file:
                # 如果有输出文件，将stdout重定向到文件
                import os
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                with open(output_file, 'w') as output_f:
                    if isinstance(command, str):
                        result = subprocess.run(command, shell=True, check=True, text=True, 
                                              stdout=output_f, stderr=subprocess.PIPE, cwd=working_dir)
                    else:
                        result = subprocess.run(command, check=True, text=True, 
                                              stdout=output_f, stderr=subprocess.PIPE, cwd=working_dir)
                    if result.stderr:
                        log_file.write(result.stderr)
            else:
                # 没有输出文件，正常记录到日志
                if isinstance(command, str):
                    result = subprocess.run(command, shell=True, check=True, text=True, 
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=working_dir)
                else:
                    result = subprocess.run(command, check=True, text=True, 
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=working_dir)
                log_file.write(result.stdout)
                if result.stderr:
                    log_file.write(result.stderr)
            
            log_file.write(f"[{timestamp()}] 命令执行完成\n\n")
            
    except subprocess.CalledProcessError as e:
        with open(run_log_path, 'a') as log_file:
            log_file.write(f"[{timestamp()}] 命令执行失败，错误如下：\n{e.stderr}\n")
        raise e

def execute_node(node: WorkflowNode, workflow_logger: logging.Logger):
    adapter = get_adapter(node)
    node = adapter.adapt(node)
    print(node.__repr__())

    node_dir = node.log_dir / f"{node.name}({node.id})"
    ensure_dir(node_dir)
    run_log_path = node_dir / "run.log"
    status_path = node_dir / "status.log"

    workflow_logger.info(f"{timestamp()} 开始运行节点：{node.name}({node.id})")

    # 确保工作目录存在
    working_dir = getattr(node, 'working_directory', None)
    if working_dir:
        ensure_dir(working_dir)

    # 获取输出文件配置
    output_file = getattr(node, 'output_file', None)
    output_files = getattr(node, 'output_files', None)

    # 确保commands是一个命令列表
    if isinstance(node.commands, list) and len(node.commands) > 0:
        if isinstance(node.commands[0], str):
            # 如果是字符串列表，直接使用
            commands = node.commands
        else:
            # 如果是嵌套列表，取第一层
            commands = node.commands
    else:
        commands = [node.commands] if node.commands else []
    
    status = load_status(status_path)

    if status["completed"]:
        workflow_logger.info(f"{timestamp()} 跳过节点：{node.name}({node.id})，已完成")
        return

    try:
        if node.parallelize:
            with ThreadPoolExecutor(max_workers=len(commands)) as executor:
                futures = []
                for i, cmd in enumerate(commands):
                    cmd_log_path = node_dir / f"cmd{i+1}.log"
                    # 对于多输出文件，使用对应的输出文件
                    cmd_output_file = None
                    if output_files and i < len(output_files):
                        cmd_output_file = output_files[i]
                    elif output_file and len(commands) == 1:
                        cmd_output_file = output_file
                    
                    futures.append(executor.submit(run_command, cmd, cmd_log_path, cmd_output_file, working_dir))
                for future in as_completed(futures):
                    future.result()

            with open(run_log_path, "a", encoding="utf-8") as run_log:
                for i in range(len(commands)):
                    part_log = node_dir / f"cmd{i+1}.log"
                    if part_log.exists():
                        run_log.write(part_log.read_text(encoding="utf-8"))
                        part_log.unlink()
            save_status(status_path, completed=True, completed_cmds=len(commands))
        else:
            for i, cmd in enumerate(commands[status["completed_cmds"]:], start=status["completed_cmds"]):
                # 对于多输出文件，使用对应的输出文件
                cmd_output_file = None
                if output_files and i < len(output_files):
                    cmd_output_file = output_files[i]
                elif output_file and len(commands) == 1:
                    cmd_output_file = output_file
                    
                run_command(cmd, run_log_path, cmd_output_file, working_dir)
                save_status(status_path, completed=False, completed_cmds=i + 1)
            save_status(status_path, completed=True, completed_cmds=len(commands))

        workflow_logger.info(f"{timestamp()} 节点 {node.name}({node.id}) 执行完成")
    except Exception as e:
        workflow_logger.error(f"{timestamp()} 节点 {node.name}({node.id}) 执行失败，请查看 {run_log_path}")
        raise

def execute_graph(G: nx.DiGraph):
    parallel_nodes = G.graph.get("parallel", False)
    workflow_name = G.graph.get("flow_name", "workflow")
    log_dir = Path(G.graph.get("log_dir", "logs"))
    
    # 检查log_dir是否可写，如果不可写则使用用户可写的目录
    try:
        ensure_dir(log_dir)
        # 测试是否可写
        test_file = log_dir / "test_write.tmp"
        test_file.touch()
        test_file.unlink()
    except (PermissionError, OSError):
        # 如果原目录不可写，使用用户主目录下的日志目录
        import os
        user_log_dir = Path(os.path.expanduser("~")) / "biflow_logs"
        ensure_dir(user_log_dir)
        log_dir = user_log_dir
        print(f"警告：无法写入 {G.graph.get('log_dir', 'logs')}，使用 {log_dir} 作为日志目录")
        
        # 更新所有节点的log_dir
        for node_name in G.nodes:
            G.nodes[node_name]["node"].log_dir = log_dir

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
