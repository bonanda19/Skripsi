import streamlit as st
import matplotlib.pyplot as plt
from basic_aco import BasicACO
from vrptw_base import VrptwGraph
from vrptw_aco_figure import VrptwFigure

st.set_page_config(page_title="VRPTW Ant Colony Optimization", layout="wide")
st.title("Optimasi VRPTW & Ant Colony Optimization ")

# Upload file
uploaded_file = st.file_uploader("Upload Data Pelanggan (.txt)", type=["txt"])

if uploaded_file:
    file_path = "uploaded_data.txt"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success("File uploaded successfully!")

    try:
        graph = VrptwGraph(file_path)
    except RuntimeError as e:
        st.error(str(e))
        st.stop()  # Hentikan eksekusi Streamlit jika file tidak valid


    # === Pilihan Tampilan (selectbox) ===
    st.subheader("Pilih Solusi Hasil")
    result_display = st.selectbox(
        "Silakan pilih solusi yang ingin ditampilkan:",
        ("Pilih solusi...", "Solusi Awal", "Solusi Akhir")
    )

    show_initial = result_display in ("Solusi Awal", "Solusi Akhir")
    show_optimized = result_display == "Solusi Akhir"

    # === Parameter ACO hanya jika memilih KEDUANYA ===
    if show_optimized:
        st.subheader("Parameter ACO")
        col1, col2, col3, col4 = st.columns(4)
        ants_num = col1.text_input("Jumlah Semut", "100")
        max_iter = col2.text_input("Maksimum Iterasi", "200")
        beta = col3.text_input("Beta (Pengaruh Jarak)", "1.0")
        q0 = col4.text_input("q0 (Probabilitas Eksploitasi)", "0.1")

    # Tombol proses
    if st.button("Jalankan proses"):
        if result_display == "Pilih solusi...":
            st.warning("Silakan pilih solusi terlebih dahulu.")
            
        elif result_display == "Solusi Awal":
            initial_path, initial_distance, initial_vehicle_num = graph.nearest_neighbor_heuristic()
            st.subheader("Solusi Awal")
            st.write(f"Total Jarak Tempuh: `{initial_distance:.2f}` km")
            st.write(f"Kendaraan Kembali Ke Depot: `{initial_vehicle_num}` xkali")
            st.write(f"Rute: {BasicACO.format_optimized_path(initial_path)}")
            vis = VrptwFigure(graph, initial_path, initial_distance, initial_vehicle_num, "Solusi Awal")
            vis.run_animation(filename="Solusi_Awal.gif")
            st.image("Solusi_Awal.gif", caption="🔹 Solusi Awal")

        elif result_display == "Solusi Akhir":
            try:
                ants_num = int(ants_num)
                max_iter = int(max_iter)
                beta = float(beta)
                q0 = float(q0)

                st.info("Menjalankan optimasi ACO...")
                basic_aco = BasicACO(
                    graph, ants_num=ants_num, max_iter=max_iter,
                    beta=beta, q0=q0, whether_or_not_to_show_figure=False
                )
                basic_aco.run_basic_aco()

                col1, col2 = st.columns(2)

                with col1:
                    initial_path, initial_distance, initial_vehicle_num = graph.nearest_neighbor_heuristic()
                    st.subheader("Solusi Awal")
                    st.write(f"Total Jarak Tempuh: `{initial_distance:.2f}` km")
                    st.write(f"Kendaraan Kembali Ke depot: `{initial_vehicle_num}`xkali")
                    st.write(f"Rute: {BasicACO.format_optimized_path(initial_path)}")
                    vis1 = VrptwFigure(graph, initial_path, initial_distance, initial_vehicle_num, "Solusi Awal")
                    vis1.run_animation(filename="Solusi_Awal.gif")
                    st.image("Solusi_Awal.gif", caption="🔹 Solusi Awal", use_container_width=True)

                with col2:
                    st.subheader("Solusi Akhir ACO")
                    st.write(f"Total Jarak Tempuh: `{basic_aco.best_path_distance:.2f}` km")
                    st.write(f"Kendaraan Kembali Ke Depot: `{basic_aco.best_vehicle_num}`xkali")
                    st.write(f"Rute Terbaik: {BasicACO.format_optimized_path(basic_aco.best_path)}")
                    vis2 = VrptwFigure(
                        graph, basic_aco.best_path, basic_aco.best_path_distance, basic_aco.best_vehicle_num, "Solusi Akhir"
                    )
                    vis2.run_animation(filename="Solusi_Akhir.gif")
                    st.image("Solusi_Akhir.gif", caption="🔸 Solusi Akhir ACO", use_container_width=True)

            except ValueError:
                st.error("Input parameter tidak valid. Pastikan semua diisi dengan angka.")
