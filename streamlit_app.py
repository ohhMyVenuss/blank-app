import streamlit as st
import networkx as nx
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import engine
import os

st.set_page_config(page_title="Community Detection Demo", layout="wide")

# (1) Tinh chỉnh giao diện chuyên nghiệp, không dùng icon
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        width: 100%; 
        background-color: #007bff; 
        color: white; 
        border-radius: 4px;
        border: none;
        padding: 0.6rem;
        font-weight: 600;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #0056b3; color: white; border: none; }
    .stTextArea textarea { font-family: 'Courier New', Courier, monospace; }
    h1, h2, h3 { color: #343a40; font-family: 'Segoe UI', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

st.title("Phát hiện cộng đồng trong mạng lưới")
st.write("Giải thuật Leiden tối ưu hóa Modularity Q để phân tách cấu trúc đồ thị.")

# (2) Cải thiện UI/UX nhập liệu: Copy & Paste nội dung (Graph Data)
col_input, col_viz = st.columns([1, 2])

with col_input:
    st.subheader("Dữ liệu đầu vào")
    st.write("Nhập danh sách cạnh (mỗi dòng một cạnh, ví dụ: 0 3):")
    
    # Khung nhập liệu cho phép paste toàn bộ dataset
    input_data = st.text_area(
        label="Graph Data",
        value="0 3\n0 4\n0 5\n1 4\n1 5\n2 3\n2 4\n4 5",
        height=400,
        help="Định dạng: node_nguon node_dich"
    )

    def build_graph_from_text(text):
        G = nx.Graph()
        lines = text.strip().split('\n')
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                u, v = parts[0], parts[1]
                G.add_edge(u, v)
            elif len(parts) == 1:
                G.add_node(parts[0])
        return G

    G = build_graph_from_text(input_data)
    st.write(f"Trạng thái: {G.number_of_nodes()} nút, {G.number_of_edges()} cạnh.")

# (3) Trực quan hóa tương tác (Màu riêng + Hover từng node)
with col_viz:
    st.subheader("Trực quan hóa mạng lưới")
    
    run_btn = st.button("Bắt đầu tối ưu hóa cộng đồng")
    
    # Mặc định tất cả thuộc cùng 1 cộng đồng nếu chưa chạy giải thuật
    partition = {node: 0 for node in G.nodes()}
    
    if run_btn:
        if G.number_of_edges() > 0:
            with st.spinner('Đang tính toán...'):
                partition = engine.run_leiden(G)
                mod_q = engine.calculate_modularity(G, partition)
                st.success(f"Chỉ số Modularity Q đạt được: {mod_q:.4f}")
        else:
            st.error("Vui lòng nhập dữ liệu cạnh hợp lệ.")

    # Sử dụng Pyvis để tạo đồ thị tương tác
    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="#343a40")
    
    # Bảng màu rực rỡ để phân biệt các cộng đồng
    color_palette = [
        "#e6194B", "#3cb44b", "#ffe119", "#4363d8", "#f58231", 
        "#911eb4", "#42d4f4", "#f032e6", "#bfef45", "#fabed4",
        "#469990", "#dcbeff", "#9A6324", "#fffac8", "#800000"
    ]

    for node in G.nodes():
        comm_id = partition.get(node, 0)
        # Gán màu riêng cho mỗi cộng đồng
        color = color_palette[comm_id % len(color_palette)]
        
        # Thiết lập tính năng Hover (title) và nhãn hiển thị
        net.add_node(
            node, 
            label=str(node), 
            title=f"Node ID: {node}\nCommunity: {comm_id}", # Hiện thông tin khi hover
            color=color,
            borderWidth=2
        )

    for u, v in G.edges():
        net.add_edge(u, v)

    # Cấu hình vật lý để các nút tự động sắp xếp khoa học
    net.toggle_physics(True)
    
    # Xuất và hiển thị đồ thị
    path = "graph_output.html"
    net.save_graph(path)
    with open(path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    components.html(html_content, height=650)
    
    # Dọn dẹp file tạm
    if os.path.exists(path):
        os.remove(path)

st.info("Hướng dẫn: Di chuột vào các nút để xem ID và Cộng đồng. Bạn có thể kéo thả các nút để thay đổi bố cục.")