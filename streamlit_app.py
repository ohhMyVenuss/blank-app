import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from community_detection import lar_initialization, calculate_modularity, topology_aware_mutation, population_wide_consolidation

st.set_page_config(page_title="NEW-EPWOCD Demo", layout="wide")

st.title("🌐 Demo Giải thuật NEW-EPWOCD")
st.markdown("Phát hiện cộng đồng dựa trên tối ưu hóa bầy đàn và nhận diện cấu trúc.")

# --- Sidebar: Cấu hình tham số ---
st.sidebar.header("Cấu hình giải thuật")
dataset_name = st.sidebar.selectbox("Chọn bộ dữ liệu", ["Karate Club", "Dolphins", "Football"])
pop_size = st.sidebar.slider("Quy mô quần thể (p)", 5, 50, 20)
generations = st.sidebar.slider("Số thế hệ tối ưu", 1, 50, 10)
mutation_prob = st.sidebar.slider("Xác suất đột biến (Pmut)", 0.1, 1.0, 0.3)

# --- Xử lý logic ---
if st.sidebar.button("Bắt đầu tối ưu hóa"):
    # 1. Khởi tạo đồ thị
    if dataset_name == "Karate Club":
        G = nx.karate_club_graph()
    elif dataset_name == "Dolphins":
        G = nx.dolphins_graph() # Cần file dữ liệu hoặc nx hỗ trợ
    else:
        G = nx.florentine_families_graph() # Ví dụ mẫu khác

    # 2. Khởi tạo quần thể (Bước 1 [cite: 378])
    with st.spinner('Đang khởi tạo quần thể LAR...'):
        population = lar_initialization(G, pop_size)
        
    st.success(f"Đã khởi tạo {pop_size} cá thể whale!")

    # 3. Vòng lặp tiến hóa
    progress_bar = st.progress(0)
    q_history = []

    for gen in range(generations):
        # Đột biến (Bước 4 [cite: 386])
        new_pop = []
        for ind in population:
            mutated = topology_aware_mutation(G, ind, mutation_prob)
            new_pop.append(mutated)
        population = new_pop
        
        # Ghi nhận Q tốt nhất
        current_q = max([calculate_modularity(G, ind) for ind in population])
        q_history.append(current_q)
        progress_bar.progress((gen + 1) / generations)

    # 4. Củng cố cuối cùng (Bước 7 [cite: 399])
    final_pop = population_wide_consolidation(G, population)
    best_ind = max(final_pop, key=lambda x: calculate_modularity(G, x))
    final_q = calculate_modularity(G, best_ind)

    # --- Hiển thị kết quả ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Biểu đồ hội tụ Modularity (Q)")
        st.line_chart(q_history)
        st.metric("Modularity cuối cùng", f"{final_q:.4f}")

    with col2:
        st.subheader("Trực quan hóa cộng đồng")
        fig, ax = plt.subplots()
        pos = nx.spring_layout(G)
        # Lấy màu theo cộng đồng
        node_colors = [best_ind[node] for node in G.nodes()]
        nx.draw(G, pos, node_color=node_colors, with_labels=True, cmap=plt.cm.rainbow, ax=ax)
        st.pyplot(fig)


