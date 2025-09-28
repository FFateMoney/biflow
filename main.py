import argparse
from util import yaml_util
from core import graph_manager
from executor.executor import execute_graph


'''
TODO： 
1、把name改为operator
2、统一参数风格
3、修改路径写死的部分
4、制定全流程图
'''
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="配置文件路径")
    arg = parser.parse_args()
    yaml = arg.config
    config = yaml_util.load_yaml_to_dict(yaml)
    print(" 配置文件加载成功")
    graphy = graph_manager.build_graph(config)
    print(" 图构建成功，节点如下：")
    for i in graphy.nodes:
        node_obj = graphy.nodes[i]["node"]
        print(f"{i} => {node_obj}")
    print(" 开始执行图...")
    execute_graph(graphy)

if __name__ == "__main__":
    main()