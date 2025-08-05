from abc import ABC, abstractmethod
from core.node import WorkflowNode

class BaseAdapter(ABC):
    def __init__(self, config=None, sample_data=None):
        self.config = config or {}  # 默认空字典
        self.sample_data = sample_data

    @abstractmethod
    def adapt(self, node: WorkflowNode) -> WorkflowNode:
     """
        接收一个 WorkflowNode，根据 node.pararm 拼接命令行，
        更新 node.commands 并返回。
        """
        pass