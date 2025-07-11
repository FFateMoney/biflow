from util import yaml_util
from core import graph_manager
from executor.executor import execute_graph
def main():
    conf = yaml_util.load_yaml_to_dict("./config/test_flow.yaml")
    graphy = graph_manager.build_graph(conf)
    for i in graphy.nodes:
        node_obj = graphy.nodes[i]["node"]
        print(f"{i} => {node_obj}")
    execute_graph(graphy)
if __name__ == "__main__":
    main()