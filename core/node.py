import numbers
from pathlib import Path
from typing import List

class WorkflowNode:
    def __init__(
        self,
        subcommand: str,
        id: numbers,
        commands: List,
        input_dir,
        output_dir: Path,
        log_dir: Path,
        params: dict,
        tool: str,
        parallelize: bool = False,

    ):
        self.subcommand = subcommand
        self.id = id
        self.commands = commands
        self.params = params
        self.tool = tool
        self.parallelize = parallelize
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.log_dir = log_dir


    def __repr__(self):
        return (
            f"WorkflowNode(id='{self.id}', "
            f"subcommand='{self.subcommand}', "
            f"tool='{self.tool}', "
            f"commands={self.commands}, "
            f"parallelize={self.parallelize}, "
            f"log_dir='{self.log_dir}', "
            f"input_dir={self.input_dir},"
            f"output_dir={self.output_dir},"
            f"params={self.params})"
        )