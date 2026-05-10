import networkx as nx
import numpy as np
import random

def calculate_modularity(G, partition):
    """
    Tính chỉ số Modularity (Q) theo công thức (2) trong NEW-EPWOCD:
    Q = sum_{k=1}^S [ (lk/m) - (dk/2m)^2 ]
    
    Args:
        G (nx.Graph): Đồ thị mạng lưới (undirected, unweighted)
        partition (dict): Mapping node -> community_id
    
    Returns:
        float: Giá trị Modularity Q
    """
    m = G.number_of_edges()
    if m == 0:
        return 0
    
    communities = {}
    for node, comm_id in partition.items():
        if comm_id not in communities:
            communities[comm_id] = []
        communities[comm_id].append(node)
    
    modularity_q = 0
    for comm_id, nodes in communities.items():
        # lk: số cạnh nội bộ trong cộng đồng k
        subgraph = G.subgraph(nodes)
        lk = subgraph.number_of_edges()
        
        # dk: tổng bậc của các nút trong cộng đồng k
        dk = sum(dict(G.degree(nodes)).values())
        
        # Công thức (2)
        term1 = lk / m
        term2 = (dk / (2 * m)) ** 2
        modularity_q += (term1 - term2)
        
    return modularity_q

def lar_initialization(G, population_size):
    """
    Khởi tạo quần thể bằng phương pháp LAR (Locus-based Adjacency Representation).
    Mỗi cá thể đại diện cho một phân hoạch cộng đồng.
    
    Args:
        G (nx.Graph): Đồ thị mạng lưới
        population_size (int): Số lượng cá thể trong quần thể
        
    Returns:
        list: Danh sách các cá thể (mỗi cá thể là một dictionary node -> community_id)
    """
    nodes = list(G.nodes())
    num_nodes = G.number_of_nodes()
    population = []
    
    for _ in range(population_size):
        # LAR: Mỗi gene i trỏ tới một neighbor j của i
        individual_lar = {}
        for node in nodes:
            neighbors = list(G.neighbors(node))
            if neighbors:
                individual_lar[node] = random.choice(neighbors)
            else:
                individual_lar[node] = node # Isolated node
        
        # Giải mã LAR sang phân hoạch cộng đồng (Connected Components)
        # Tạo đồ thị phụ từ các liên kết LAR
        temp_graph = nx.Graph()
        temp_graph.add_nodes_from(nodes)
        for u, v in individual_lar.items():
            temp_graph.add_edge(u, v)
        
        # Các thành phần liên thông đại diện cho các cộng đồng
        components = list(nx.connected_components(temp_graph))
        partition = {}
        for comm_id, component in enumerate(components):
            for node in component:
                partition[node] = comm_id
                
        population.append(partition)
        
    return population

def topology_aware_mutation(G, individual, mutation_prob=0.1):
    """
    Algorithm 2: Topology-aware Enhanced Mutation
    
    Args:
        G (nx.Graph): Đồ thị đầu vào.
        individual (dict): Phân hoạch hiện tại (node -> community_id).
        mutation_prob (float): Xác suất đột biến.
        
    Returns:
        dict: Phân hoạch sau khi đột biến.
    """
    # 1. Kiểm tra xác suất đột biến
    if random.random() >= mutation_prob:
        return individual.copy()
    
    partition = individual.copy()
    nodes = list(G.nodes())
    
    # 5. Chọn ngẫu nhiên một nút u
    u = random.choice(nodes)
    
    # 6. Xác định cộng đồng hiện tại của u
    old_community_id = partition[u]
    
    # Lấy danh sách các nút cùng cộng đồng với u (không bao gồm u)
    c_old_nodes = [v for v, comm_id in partition.items() if comm_id == old_community_id and v != u]
    
    # 7. Tạo ID cộng đồng mới (đảm bảo không trùng)
    new_community_id = max(partition.values()) + 1
    
    # Tách u ra cộng đồng mới
    partition[u] = new_community_id
    
    # 8. Sinh số ngẫu nhiên s để chọn chiến lược
    s = random.random()
    
    if s < 0.5:
        # Strategy 1: Stochastic intra-community reassignment
        # Chuyển các nút trong cộng đồng cũ sang cộng đồng mới với xác suất 0.5
        for v in c_old_nodes:
            if random.random() < 0.5:
                partition[v] = new_community_id
    else:
        # Strategy 2: Neighborhood-based community formation
        # Gom tất cả hàng xóm của u vào cộng đồng mới
        neighbors = list(G.neighbors(u))
        for v in neighbors:
            partition[v] = new_community_id
            
    return partition

def refine_partition(G, partition):
    """
    Thực hiện tinh chỉnh một phân hoạch (Greedy refinement).
    Duyệt qua các nút và thử di chuyển chúng sang cộng đồng của hàng xóm 
    nếu điều đó làm tăng Modularity (Q).
    """
    current_partition = partition.copy()
    current_q = calculate_modularity(G, current_partition)
    
    nodes = list(G.nodes())
    random.shuffle(nodes)
    
    # Một vòng lặp đơn giản để tinh chỉnh các nút biên
    improved = True
    max_iterations = 2 # Giới hạn để đảm bảo tốc độ
    iteration = 0
    
    while improved and iteration < max_iterations:
        improved = False
        iteration += 1
        for node in nodes:
            neighbor_communities = set()
            for neighbor in G.neighbors(node):
                neighbor_communities.add(current_partition[neighbor])
            
            best_comm = current_partition[node]
            best_q = current_q
            
            original_comm = current_partition[node]
            for comm_id in neighbor_communities:
                if comm_id == original_comm:
                    continue
                
                current_partition[node] = comm_id
                new_q = calculate_modularity(G, current_partition)
                
                if new_q > best_q:
                    best_q = new_q
                    best_comm = comm_id
                else:
                    current_partition[node] = original_comm # Hoàn tác
            
            if best_comm != original_comm:
                current_partition[node] = best_comm
                current_q = best_q
                improved = True
                
    return current_partition, current_q

def population_wide_consolidation(G, population):
    """
    Step 7: Population-wide Community Consolidation.
    Áp dụng tinh chỉnh cho toàn bộ quần thể.
    """
    refined_population = []
    
    for individual in population:
        q_before = calculate_modularity(G, individual)
        refined_ind, q_after = refine_partition(G, individual)
        
        # So sánh fitness và chỉ giữ lại nếu tốt hơn
        if q_after > q_before:
            refined_population.append(refined_ind)
        else:
            refined_population.append(individual.copy())
            
    return refined_population

# Ví dụ sử dụng:
if __name__ == "__main__":
    # Tạo đồ thị mẫu (Karate Club)
    G = nx.karate_club_graph()
    
    # Khởi tạo quần thể
    pop_size = 10
    initial_population = lar_initialization(G, pop_size)
    
    print(f"Khởi tạo quần thể quy mô {pop_size} thành công.")
    
    # Tính Modularity cho cá thể đầu tiên
    first_individual = initial_population[0]
    q_value = calculate_modularity(G, first_individual)
    
    print(f"Modularity (Q) của cá thể đầu tiên: {q_value:.4f}")
    
    # Kiểm tra số lượng cộng đồng trong cá thể đầu tiên
    num_comm = len(set(first_individual.values()))
    print(f"Số lượng cộng đồng tìm thấy: {num_comm}")
