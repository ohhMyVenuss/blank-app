import networkx as nx
import igraph as ig
import leidenalg

def calculate_modularity(G, partition):
    m = G.number_of_edges()
    if m == 0: return 0
    communities = {}
    for node, comm_id in partition.items():
        communities.setdefault(comm_id, []).append(node)
    q = 0
    for nodes in communities.values():
        lk = G.subgraph(nodes).number_of_edges()
        dk = sum(dict(G.degree(nodes)).values())
        q += (lk / m) - (dk / (2 * m))**2
    return q

def run_leiden(G):
    mapping = {node: i for i, node in enumerate(G.nodes())}
    reverse_mapping = {i: node for node, i in mapping.items()}
    edges = [(mapping[u], mapping[v]) for u, v in G.edges()]
    ig_g = ig.Graph(len(G.nodes()), edges)
    partition = leidenalg.find_partition(ig_g, leidenalg.ModularityVertexPartition)
    
    result_partition = {}
    for comm_id, nodes in enumerate(partition):
        for node_idx in nodes:
            result_partition[reverse_mapping[node_idx]] = comm_id
    return result_partition