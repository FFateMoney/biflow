from typing import Dict

import yaml


def load_yaml_to_dict(yaml_path: str) -> Dict:
    """从 YAML 文件加载为 Python 字典"""
    with open(yaml_path, "r") as f:
        config = yaml.safe_load(f)
    return config
