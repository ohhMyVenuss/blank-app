import streamlit as st
import networkx as nx
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import engine
import os

st.set_page_config(page_title="Community Detection Demo", layout="wide")

# Tinh chỉnh giao diện chuyên nghiệp
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
    }
    .stButton>button:hover { background-color: #0056b3; color: white; }
    .stTextArea textarea { font-family: 'Courier New', Courier, monospace; }
    h1, h2, h3 { color: #343a40; font-family: 'Segoe UI', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

st.title("Phát hiện cộng đồng trong mạng lưới")
st.write("Giải thuật Leiden tối ưu hóa Modularity Q để phân tách cấu trúc đồ thị.")

# Định nghĩa các bộ dữ liệu mẫu (Edge Lists)
DATASETS = {
    "Tùy chỉnh (Nhập tay)": "",
    "Zachary's Karate Club (n=34)": "1 2\n1 3\n1 4\n1 5\n1 6\n1 7\n1 8\n1 9\n1 11\n1 12\n1 13\n1 14\n1 18\n1 20\n1 22\n1 32\n2 3\n2 4\n2 8\n2 14\n2 18\n2 20\n2 22\n3 4\n3 8\n3 9\n3 10\n3 14\n3 28\n3 29\n3 33\n4 8\n4 13\n4 14\n5 7\n5 11\n6 7\n6 11\n6 17\n7 11\n9 31\n9 33\n9 34\n10 34\n14 34\n15 33\n15 34\n16 33\n16 34\n19 33\n19 34\n20 34\n21 33\n21 34\n23 33\n23 34\n24 26\n24 28\n24 30\n24 33\n24 34\n25 26\n25 28\n25 32\n26 32\n27 30\n27 34\n28 34\n29 32\n29 34\n30 33\n30 34\n31 33\n31 34\n32 33\n32 34\n33 34",
    "Dolphins Social Network (n=62)": "Beak Fish\nBeak Grin\nBeak SN9\nBeak TR75\nBeak TR99\nBumper Fish\nBumper SN96\nBumper Thumper\nBumper Zipfel\nDouble Oscar\nDouble SN4\nDouble Topless\nDouble TR99\nDouble Zap\nFeather Gallatin\nFeather Jet\nFeather Ripple\nFeather SN9\nFeather TR99\nGallatin Jet\nGallatin Ripple\nGallatin SN9\nGallatin SN96\nGallatin TR75\nGrin Hook\nGrin Shmuddel\nGrin SN4\nGrin SN63\nGrin SN9\nGrin Stripquies\nGrin TR99\nGrin TS71\nHook KNOT\nHook Scabs\nHook Shmuddel\nHook SN4\nHook SN63\nHook TR99\nJet Mn83\nJet Mus\nJet Number1\nJet Quini\nJet Ripple\nJet TR99\nKNOT Mus\nKNOT Oscar\nKNOT SN9\nKNOT Topless\nKNOT TR99",
    "American College Football (n=115)": "BrighamYoung FloridaState\nBrighamYoung NewMexico\nBrighamYoung SanDiegoState\nBrighamYoung Wyoming\nBrighamYoung Utah\nBrighamYoung AirForce\nFloridaState NorthCarolinaState\nFloridaState Virginia\nFloridaState GeorgiaTech\nFloridaState Duke\nFloridaState Maryland\nFloridaState Clemson\nFloridaState MiamiFlorida\nFloridaState Florida\nIowaState TexasA&M\nIowaState UNLV\nIowaState Missouri\nIowaState OklahomaState\nIowaState Colorado\nIowaState Nebraska\nIowaState KansasState\nIowaState Kansas\nNewMexico SanDiegoState\nNewMexico Wyoming\nNewMexico Utah\nNewMexico AirForce\nNewMexico ColoradoState\nTexasA&M OklahomaState\nTexasA&M Colorado\nTexasA&M Nebraska\nTexasA&M KansasState\nTexasA&M Kansas\nTexasA&M Texas\nTexasA&M Baylor\nTexasA&M Oklahoma\nTexasA&M TexasTech"
}

# --- Bố cục 2 cột ---
col_input, col_viz = st.columns([1, 2])

with col_input:
    st.subheader("Cấu hình dữ liệu")
    
    # Chọn bộ dữ liệu mẫu
    selected_template = st.selectbox("Chọn mạng mẫu để demo", list(DATASETS.keys()))
    
    # Cập nhật nội dung dựa trên lựa chọn
    input_text = st.text_area(
        label="Dữ liệu cạnh (Graph Data)",
        value=DATASETS[selected_template],
        height=350,
        placeholder="Nhập: NútA NútB"
    )

    def parse_graph(text):
        G = nx.Graph()
        lines = text.strip().split('\n')
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                G.add_edge(parts[0], parts[1])
            elif len(parts) == 1:
                G.add_node(parts[0])
        return G

    G = parse_graph(input_text)
    st.write(f"Trạng thái: **{G.number_of_nodes()}** nút, **{G.number_of_edges()}** cạnh.")

# --- Trực quan hóa ---
with col_viz:
    st.subheader("Đồ thị tương tác")
    
    run_btn = st.button("Bắt đầu phát hiện cộng đồng")
    
    partition = {node: 0 for node in G.nodes()}
    if run_btn:
        if G.number_of_edges() > 0:
            with st.spinner('Đang chạy Leiden...'):
                partition = engine.run_leiden(G)
                q = engine.calculate_modularity(G, partition)
                st.success(f"Chỉ số Modularity Q: {q:.4f}")
        else:
            st.error("Dữ liệu trống!")

    # Hiển thị đồ thị tương tác Pyvis
    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="#343a40")
    palette = ["#e6194B", "#3cb44b", "#ffe119", "#4363d8", "#f58231", "#911eb4", "#42d4f4", "#f032e6", "#bfef45", "#fabed4"]

    for node in G.nodes():
        comm_id = partition.get(node, 0)
        color = palette[comm_id % len(palette)]
        net.add_node(node, label=str(node), title=f"Node: {node}\nComm: {comm_id}", color=color)

    for u, v in G.edges():
        net.add_edge(u, v)

    net.toggle_physics(True)
    
    path = "demo_graph.html"
    net.save_graph(path)
    with open(path, 'r', encoding='utf-8') as f:
        components.html(f.read(), height=650)
    
    if os.path.exists(path):
        os.remove(path)