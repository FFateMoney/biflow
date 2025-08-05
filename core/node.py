import numbers
from pathlib import Path
from typing import List

class WorkflowNode:
    def __init__(
        self,
        name: str,
        id: numbers,
        commands: List,
        input_dir,
        output_dir: Path,
        log_dir: Path,
        params: dict,
        tool: str,
        parallelize: bool = False,
        breeds: list = None,
        samples: list = None,
    ):
        self.name = name
        self.id = id
        self.commands = commands
        self.params = params
        self.tool = tool
        self.parallelize = parallelize
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.log_dir = log_dir
        self.breeds = breeds or []
        self.samples = samples or []

    def repr(self):
        return (
            f"WorkflowNode(id='{self.id}', "
            f"name='{self.name}', "
            f"tool='{self.tool}', "
            f"commands={self.commands}, "
            f"parallelize={self.parallelize}, "
            f"log_dir='{self.log_dir}', "
            f"input_dir={self.input_dir},"
            f"output_dir={self.output_dir},"
            f"breeds={self.breeds},"
            f"samples={self.samples},"
            f"params={self.params})"
        )