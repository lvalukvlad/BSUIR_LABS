# utils/graph_io.py
import networkx as nx
import json
from networkx.readwrite import json_graph

def save_graph(graph, filename):
    data = json_graph.node_link_data(graph)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_graph(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    graph = json_graph.node_link_graph(data)
    return graph