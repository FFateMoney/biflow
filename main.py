from util import yaml_util
from core import graph_manager
def main():
    conf = yaml_util.load_yaml_to_dict("./config/work_flow1.yaml")
    graphy = graph_manager.build_graph(conf)
    for i in graphy.nodes:
        node_obj = graphy.nodes[i]["node"]
        print(f"{i} => {node_obj}")
if __name__ == "__main__":
    main()