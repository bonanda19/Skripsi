import os
import random
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from multiprocessing import Queue as MPQueue




class VrptwFigure:
    """ Kelas untuk menangani animasi jalur kendaraan dengan warna tetap untuk setiap kendaraan """

    def __init__(self, graph, path, distance, vehicles, title, bg_color="white"):
        self.graph = graph
        self.path = path
        self.distance = distance
        self.vehicles = vehicles
        self.title = title
        self.bg_color = bg_color
        self.vehicle_colors = {}  # Dictionary untuk menyimpan warna setiap kendaraan

    def generate_random_color(self):
        """ Menghasilkan warna acak dalam format RGB """
        return (random.random(), random.random(), random.random())

    def run_animation(self, filename=""):
        """ Menyimpan animasi jalur kendaraan sebagai GIF """
        fig, ax = plt.subplots(figsize=(10, 6))  # Ukuran tetap
        ax.set_facecolor(self.bg_color)

        def update(frame):
            ax.clear()
            ax.set_title(f"{self.title}\nTravel Distance: {self.distance:.2f} | Vehicles: {self.vehicles}")
            ax.set_facecolor(self.bg_color)

            # Gambar depot dan pelanggan
            for node in self.graph.nodes:
                color = 'black' if node.is_depot else 'blue'
                ax.scatter(node.x, node.y, c=color, s=100 if node.is_depot else 40)
                ax.text(node.x, node.y + 0.002, str(node.id), fontsize=9, ha='center', color='black')

            # Simpan label yang sudah dipakai untuk mencegah duplikasi
            used_labels = set()

            # Animasi bertahap untuk solusi awal
            vehicle_id = 0  # ID kendaraan (reset setiap kembali ke depot)
            for i in range(1, min(frame + 1, len(self.path))):
                x1, y1 = self.graph.nodes[self.path[i - 1]].x, self.graph.nodes[self.path[i - 1]].y
                x2, y2 = self.graph.nodes[self.path[i]].x, self.graph.nodes[self.path[i]].y

                # Jika kendaraan kembali ke depot, ubah kendaraan ID
                if self.path[i - 1] == 0:
                    vehicle_id += 1  

                # Jika kendaraan ini belum memiliki warna, buat warna baru
                if vehicle_id not in self.vehicle_colors:
                    self.vehicle_colors[vehicle_id] = self.generate_random_color()

                # Gunakan warna yang sesuai dengan kendaraan ID
                label = f'Vehicle {vehicle_id}' if f'Vehicle {vehicle_id}' not in used_labels else "_nolegend_"
                used_labels.add(label)

                ax.plot([x1, x2], [y1, y2], color=self.vehicle_colors[vehicle_id], linewidth=2, label=label)

            # Pastikan hanya label unik yang masuk ke legenda
            handles, labels = ax.get_legend_handles_labels()
            unique_labels = dict(zip(labels, handles))
            if unique_labels:  # Hanya tampilkan legenda jika ada elemen dengan label
                ax.legend(unique_labels.values(), unique_labels.keys())

        # Buat animasi
        ani = FuncAnimation(fig, update, frames=len(self.graph.nodes) * 2, interval=500, repeat=False)

        

        # Simpan sebagai GIF
        ani.save(filename, writer="pillow", fps=2)
        plt.close(fig)  # Tutup figure untuk menghindari masalah tampilan