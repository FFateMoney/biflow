import datetime
from pathlib import Path


def assign_unique_log_dir(base_log_dir: Path, node_name: str) -> Path:
    """
    返回 node 的唯一日志目录路径，如：
    base_log_dir / node_name
    base_log_dir / node_name(2)
    base_log_dir / node_name(3)
    """
    base = base_log_dir / node_name
    if not base.exists():
        return base

    index = 2
    while True:
        candidate = base_log_dir / f"{node_name}({index})"
        if not candidate.exists():
            return candidate
        index += 1


def timestamp():
    return datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
