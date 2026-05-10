import streamlit as st
import networkx as nx
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import engine
import os

st.set_page_config(page_title="Community Detection Demo", layout="wide")

# Giao diện chuyên nghiệp
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
    .stTextArea textarea { font-family: 'Courier New', Courier, monospace; font-size: 14px; }
    h1, h2, h3 { color: #343a40; font-family: 'Segoe UI', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

st.title("Phát hiện cộng đồng trong mạng lưới")
st.write("Sử dụng thuật toán Leiden để phân tích cấu trúc cộng đồng (Karate, Dolphins & Football).")

# --- CẬP NHẬT ĐẦY ĐỦ 3 DATASET MẪU ---
DATASETS = {
    "Tùy chỉnh (Nhập tay)": "",
    "Zachary's Karate Club (n=34)": "2 1\n3 1\n4 1\n5 1\n6 1\n7 1\n8 1\n9 1\n11 1\n12 1\n13 1\n14 1\n18 1\n20 1\n22 1\n32 1\n3 2\n4 2\n8 2\n14 2\n18 2\n20 2\n22 2\n31 2\n4 3\n8 3\n9 3\n10 3\n14 3\n28 3\n29 3\n33 3\n8 4\n13 4\n14 4\n7 5\n11 5\n7 6\n11 6\n17 6\n17 7\n31 9\n33 9\n34 9\n34 10\n34 14\n33 15\n34 15\n33 16\n34 16\n33 19\n34 19\n34 20\n33 21\n34 21\n33 23\n34 23\n26 24\n28 24\n30 24\n33 24\n34 24\n26 25\n28 25\n32 25\n32 26\n30 27\n34 27\n34 28\n32 29\n34 29\n33 30\n34 30\n33 31\n34 31\n33 32\n34 32\n34 33",
    "Dolphins Social Network (n=62)": "1 11\n1 15\n1 16\n1 41\n1 43\n1 48\n2 18\n2 20\n2 27\n2 28\n2 29\n2 37\n2 42\n2 55\n3 11\n3 43\n3 45\n3 62\n4 9\n4 15\n4 60\n5 52\n6 10\n6 14\n6 57\n6 58\n7 10\n7 14\n7 18\n7 55\n7 57\n7 58\n8 20\n8 28\n8 31\n8 41\n8 55\n9 21\n9 29\n9 38\n9 46\n9 60\n10 14\n10 18\n10 33\n10 42\n10 58\n11 30\n11 43\n11 48\n12 52\n13 34\n14 18\n14 33\n14 42\n14 55\n14 58\n15 17\n15 25\n15 34\n15 35\n15 38\n15 39\n15 41\n15 44\n15 51\n15 53\n16 19\n16 25\n16 41\n16 46\n16 56\n16 60\n17 21\n17 34\n17 38\n17 39\n17 51\n18 23\n18 26\n18 28\n18 32\n18 58\n19 21\n19 22\n19 25\n19 30\n19 46\n19 52\n20 31\n20 55\n21 29\n21 37\n21 39\n21 45\n21 48\n21 51\n22 30\n22 34\n22 38\n22 46\n22 52\n24 37\n24 46\n24 52\n25 30\n25 46\n25 52\n26 27\n26 28\n27 28\n29 31\n29 48\n30 36\n30 44\n30 46\n30 52\n30 53\n31 43\n31 48\n33 61\n34 35\n34 38\n34 39\n34 41\n34 44\n34 51\n35 38\n35 45\n35 50\n37 38\n37 40\n37 41\n37 60\n38 41\n38 44\n38 46\n38 62\n39 44\n39 45\n39 53\n39 59\n40 58\n41 53\n42 55\n42 58\n43 48\n43 51\n44 47\n44 54\n46 51\n46 52\n46 60\n47 50\n49 58\n51 52\n52 56\n54 62\n55 58",
    "College Football (n=115)": "BrighamYoung FloridaState\nBrighamYoung NewMexico\nBrighamYoung SanDiegoState\nBrighamYoung Wyoming\nBrighamYoung Utah\nBrighamYoung AirForce\nFloridaState NorthCarolinaState\nFloridaState Virginia\nFloridaState GeorgiaTech\nFloridaState Duke\nFloridaState Maryland\nFloridaState Clemson\nFloridaState MiamiFlorida\nFloridaState Florida\nIowaState TexasA&M\nIowaState UNLV\nIowaState Missouri\nIowaState OklahomaState\nIowaState Colorado\nIowaState Nebraska\nIowaState KansasState\nIowaState Kansas\nNewMexico SanDiegoState\nNewMexico Wyoming\nNewMexico Utah\nNewMexico AirForce\nNewMexico ColoradoState\nTexasA&M OklahomaState\nTexasA&M Colorado\nTexasA&M Nebraska\nTexasA&M KansasState\nTexasA&M Kansas\nTexasA&M Texas\nTexasA&M Baylor\nTexasA&M Oklahoma\nTexasA&M TexasTech\nNorthCarolinaState Virginia\nNorthCarolinaState GeorgiaTech\nNorthCarolinaState Duke\nNorthCarolinaState Maryland\nNorthCarolinaState Clemson\nNorthCarolinaState WakeForest\nNorthCarolinaState NorthCarolina\nVirginia GeorgiaTech\nVirginia Duke\nVirginia Maryland\nVirginia Clemson\nVirginia WakeForest\nVirginia NorthCarolina\nGeorgiaTech Duke\nGeorgiaTech Maryland\nGeorgiaTech Clemson\nGeorgiaTech WakeForest\nGeorgiaTech NorthCarolina\nDuke Maryland\nDuke Clemson\nDuke WakeForest\nDuke NorthCarolina\nMaryland Clemson\nMaryland WakeForest\nMaryland NorthCarolina\nClemson WakeForest\nClemson NorthCarolina\nWakeForest NorthCarolina"
}

# --- Bố cục ---
col_input, col_viz = st.columns([1, 2])

with col_input:
    st.subheader("Cấu hình dữ liệu")
    selected_template = st.selectbox("Chọn mạng mẫu để demo", list(DATASETS.keys()))
    
    input_text = st.text_area(
        label="Dữ liệu cạnh (Graph Data)",
        value=DATASETS[selected_template],
        height=400
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

with col_viz:
    st.subheader("Đồ thị tương tác")
    run_btn = st.button("Bắt đầu phát hiện cộng đồng")
    
    partition = {node: 0 for node in G.nodes()}
    if run_btn:
        if G.number_of_edges() > 0:
            with st.spinner('Leiden đang tính toán...'):
                partition = engine.run_leiden(G)
                q = engine.calculate_modularity(G, partition)
                st.success(f"Chỉ số Modularity Q: {q:.4f}")

    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="#343a40")
    palette = ["#e6194B", "#3cb44b", "#ffe119", "#4363d8", "#f58231", "#911eb4", "#42d4f4", "#f032e6", "#bfef45", "#fabed4", "#469990", "#dcbeff", "#9A6324", "#fffac8"]

    for node in G.nodes():
        comm_id = partition.get(node, 0)
        color = palette[comm_id % len(palette)]
        net.add_node(node, label=str(node), title=f"Đội: {node}\nConference: {comm_id}", color=color)

    for u, v in G.edges():
        net.add_edge(u, v)

    net.toggle_physics(True)
    path = "football_graph.html"
    net.save_graph(path)
    with open(path, 'r', encoding='utf-8') as f:
        components.html(f.read(), height=650)
    
    if os.path.exists(path):
        os.remove(path)