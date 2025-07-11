from adapters.base_adapter import BaseAdapter
from core.node import WorkflowNode

class TestAdapter(BaseAdapter):
    def adapt(self, node: WorkflowNode) -> WorkflowNode:
        operation = node.name.lower()

        # 映射操作名到函数
        operation_map = {
            "writea": self.writeA,
            "writeb": self.writeB,
            "writeab": self.writeAB
        }

        if operation not in operation_map:
            raise ValueError(f"Unsupported Test operation: {operation}")

        return operation_map[operation](node)

    def writeA(self, node: WorkflowNode) -> WorkflowNode:
        file_name = node.params.get("file")
        file_path = node.input_dir / file_name
        file_str = file_path.as_posix()  # 使用斜杠风格（跨平台且不会触发转义）

        command = [
            "python",
            "-c",
            f"with open('{file_str}', 'w') as f: f.write('A'*10)"
        ]
        node.commands=command
        return node

    def writeB(self, node: WorkflowNode) -> WorkflowNode:
        file_name = node.params.get("file")
        file_path = node.input_dir / file_name
        file_str = file_path.as_posix()  # 使用斜杠风格（跨平台且不会触发转义）

        command = [
            "python",
            "-c",
            f"with open('{file_str}', 'w') as f: f.write('B'*10)"
        ]

        node.commands.append(command)
        return node

    def writeAB(self, node: WorkflowNode) -> WorkflowNode:
        file_pathA = node.input_dir / node.params.get("fileA")
        file_pathB = node.input_dir / node.params.get("fileB")
        file_strA = file_pathA.as_posix()
        file_strB = file_pathB.as_posix()

        # 用循环写入大文件模拟耗时
        commandA = [
            "python",
            "-c",
            (
                f"with open('{file_strA}', 'w') as f:\n"
                "    for _ in range(10**7): f.write('A')\n"
                "import time; time.sleep(2)"  # 写完休眠2秒
            )
        ]

        commandB = [
            "python",
            "-c",
            (
                f"with open('{file_strB}', 'w') as f:\n"
                "    for _ in range(10**7): f.write('B')\n"
                "import time; time.sleep(2)"
            )
        ]

        node.commands.append(commandA)
        node.commands.append(commandB)
        return node
