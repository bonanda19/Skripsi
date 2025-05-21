import os
import random
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from multiprocessing import Queue as MPQueue




# class VrptwAcoFigure:
#     def __init__(self, nodes: list, path_queue, bg_color="white"):
#         """
#         Class untuk menggambar dan menyimpan animasi solusi VRPTW menggunakan ACO.

#         :param nodes: daftar node, termasuk depot.
#         :param path_queue: antrian yang berisi path hasil komputasi.
#         :param bg_color: warna latar belakang gambar.
#         """
#         self.nodes = nodes
#         self.figure, self.figure_ax = plt.subplots(figsize=(10, 6))
#         self.bg_color = bg_color
#         self.path_queue = path_queue
#         self._depot_color = 'k'
#         self._customer_color = 'steelblue'
#         self.vehicle_colors = {}  # Warna untuk setiap kendaraan
#         self.path = []
#         self.distance = 0
#         self.used_vehicle_num = 0

#     def _generate_random_color(self):
#         """ Menghasilkan warna acak dalam format RGB """
#         return (random.random(), random.random(), random.random())

#     def _draw_point(self):
#         """ Gambar depot dan pelanggan dengan ID di atasnya """
#         self.figure_ax.clear()
#         self.figure_ax.set_facecolor(self.bg_color)

#         # Gambar depot
#         self.figure_ax.scatter([self.nodes[0].x], [self.nodes[0].y], c=self._depot_color, label='Depot', s=40)
#         self.figure_ax.text(self.nodes[0].x, self.nodes[0].y + 0.005, str(self.nodes[0].id), 
#                             fontsize=9, ha='center', color='black')

#         # Gambar pelanggan dengan ID
#         for node in self.nodes[1:]:
#             self.figure_ax.scatter(node.x, node.y, c=self._customer_color, label='Customer', s=20)
#             self.figure_ax.text(node.x, node.y + 0.002, str(node.id), fontsize=7, ha='center', color='black')

#     def _draw_line(self, frame):
#         """ Menggambar jalur kendaraan hingga frame tertentu """
#         self.figure_ax.clear()
#         self._draw_point()
#         self.figure_ax.set_title(f"Travel Distance: {self.distance:.2f}, Vehicles: {self.used_vehicle_num}")

#         vehicle_id = 0
#         used_labels = set()

#         for i in range(1, min(frame + 1, len(self.path))):
#             x1, y1 = self.nodes[self.path[i - 1]].x, self.nodes[self.path[i - 1]].y
#             x2, y2 = self.nodes[self.path[i]].x, self.nodes[self.path[i]].y

#             if self.path[i - 1] == 0:
#                 vehicle_id += 1  # Kendaraan baru

#             if vehicle_id not in self.vehicle_colors:
#                 self.vehicle_colors[vehicle_id] = self._generate_random_color()

#             label = f'Vehicle {vehicle_id}' if f'Vehicle {vehicle_id}' not in used_labels else "_nolegend_"
#             used_labels.add(label)

#             self.figure_ax.plot([x1, x2], [y1, y2], color=self.vehicle_colors[vehicle_id], linewidth=1.5, label=label)

#         handles, labels = self.figure_ax.get_legend_handles_labels()
#         unique_labels = dict(zip(labels, handles))
#         if unique_labels:
#             self.figure_ax.legend(unique_labels.values(), unique_labels.keys())

#     def run(self, save_as_gif=True):
#         """ 
#         Menjalankan animasi jalur VRPTW dan menyimpan sebagai GIF jika diperlukan 
#         """
#         while not self.path_queue.empty():
#             info = self.path_queue.get()
#             while not self.path_queue.empty():
#                 info = self.path_queue.get()

#             path, distance, used_vehicle_num = info.get_path_info()
#             if path is None:
#                 print('[draw figure]: exit')
#                 return

#             self.path = path
#             self.distance = distance
#             self.used_vehicle_num = used_vehicle_num

#             ani = FuncAnimation(self.figure, self._draw_line, frames=len(path), interval=500, repeat=False)

#             if os.path.exists("vrptw_aco_animation.gif"):
#                 os.remove("vrptw_aco_animation.gif")

#             if save_as_gif:
#                 ani.save("vrptw_aco_animation.gif", writer="pillow", fps=2)
#                 print("GIF animation saved as vrptw_aco_animation.gif")
            
#             plt.close(self.figure)


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