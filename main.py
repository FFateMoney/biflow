from util import yaml_util
from core import graph_manager
from executor.executor import execute_graph

def main():
    conf = yaml_util.load_yaml_to_dict("./config/ReadQC.yaml")
    graphy = graph_manager.build_graph(conf)
    print(" 图构建成功，节点如下：")
    for i in graphy.nodes:
        node_obj = graphy.nodes[i]["node"]
        print(f"{i} => {node_obj}")
    print("开始执行图...")
    execute_graph(graphy)

if __name__ == "__main__":
    main()