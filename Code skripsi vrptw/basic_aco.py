import numpy as np
import random
from vrptw_aco_figure import  VrptwFigure
from vrptw_base import VrptwGraph, PathMessage
from ant import Ant
from threading import Thread
from queue import Queue
import time

class BasicACO:
    def __init__(self, graph: VrptwGraph, ants_num, max_iter, beta, q0,
                 whether_or_not_to_show_figure=True):
        super()
        self.alpha = 1
        # The graph includes the positions and service time information of the nodes.
        self.graph = graph
        # Number of ants.
        self.ants_num = ants_num
        # Maximum number of iterations.
        self.max_iter = max_iter
        # Maximum load capacity of each vehicle.
        self.max_load = graph.vehicle_capacity
        # Importance of heuristic information.
        self.beta = beta
        # Probability of directly choosing the next point with the highest likelihood.
        self.q0 = q0
        # Best path information.
        self.best_path_distance = None
        self.best_path = None
        self.best_vehicle_num = None

        self.whether_or_not_to_show_figure = whether_or_not_to_show_figure

    def run_basic_aco(self):
        """
        Menjalankan algoritma ACO tanpa visualisasi interaktif per iterasi.
        Akan menampilkan hasil akhir dengan VrptwFigure jika diaktifkan.
        """
        start_time_total = time.time()
        random.seed(42)
        np.random.seed(42)

        # Jalankan proses utama ACO (tanpa thread karena tidak perlu queue)
        self._basic_aco(path_queue_for_figure=None)

        if self.whether_or_not_to_show_figure and self.best_path is not None:
            final_visualizer = VrptwFigure(
                self.graph,
                self.best_path,
                self.best_path_distance,
                self.best_vehicle_num,
                title="ACO Final Solution"
            )
            final_visualizer.run_animation()


    def format_optimized_path(path):
        result = []
        sub_route = []
        for node in path:
            sub_route.append(node)
            if node == 0 and len(sub_route) > 1:
                result.append(sub_route)
                sub_route = []
        return result

    def _basic_aco(self, path_queue_for_figure: Queue):
        """
        The most basic ant colony algorithm.
        :return:
        """
       
        start_time_total = time.time()

        # Maximum number of iterations.
        start_iteration = 0
        for iter in range(self.max_iter):

            # Set the current vehicle load, travel distance, and time for each ant.
            ants = list(Ant(self.graph) for _ in range(self.ants_num))
            for k in range(self.ants_num):

                # Each ant needs to visit all the customers.
                while not ants[k].index_to_visit_empty():
                    next_index = self.select_next_index(ants[k])
                    # Check whether adding the next position still satisfies the constraints.
                    # If not, select another position and recheck.
                    if not ants[k].check_condition(next_index):
                        next_index = self.select_next_index(ants[k])
                        if not ants[k].check_condition(next_index):
                            next_index = 0

                    # Update the ant's path.
                    ants[k].move_to_next_index(next_index)
                    self.graph.local_update_pheromone(ants[k].current_index, next_index)

                # Finally return to position 0.
                ants[k].move_to_next_index(0)
                self.graph.local_update_pheromone(ants[k].current_index, 0)

            # Calculate the path lengths of all ants.
            paths_distance = np.array([ant.total_travel_distance for ant in ants])

            # Record the current best path.
            best_index = np.argmin(paths_distance)
            if self.best_path is None or paths_distance[best_index] < self.best_path_distance:
                self.best_path = ants[int(best_index)].travel_path
                self.best_path_distance = paths_distance[best_index]
                self.best_vehicle_num = self.best_path.count(0) - 1
                start_iteration = iter

                # Visualization display.
                if self.whether_or_not_to_show_figure and path_queue_for_figure:
                    path_queue_for_figure.put(PathMessage(self.best_path, self.best_path_distance))

                print('\n')
                print('[iteration %d]: find an improved path, its distance is %f' % (iter, self.best_path_distance))
                print('it takes %0.3f seconds for ant_colony_system to run' % (time.time() - start_time_total))

            # Update the pheromone table globally.
            self.graph.global_update_pheromone(self.best_path, self.best_path_distance)

            given_iteration = 100
            if iter - start_iteration > given_iteration:
                print('\n')
                print('iteration exit: could not find a better solution within %d iterations' % given_iteration)
                break

        print('\n')
        print('final best path distance is %f, number of vehicles is %d' % (self.best_path_distance, self.best_vehicle_num))
        print('it takes %0.3f seconds for ant_colony_system to run' % (time.time() - start_time_total))
        #**Menampilkan Solusi Awal**
        print("\n[VRPTW Initial Solution]")
        initial_path, initial_distance, initial_vehicle_num = self.graph.nearest_neighbor_heuristic()
        print(f"Total Travel Distance: {initial_distance:.2f}")
        print(f"Number of Vehicles Used: {initial_vehicle_num}")
        print(f"Initial Path: {BasicACO.format_optimized_path(initial_path)}\n")
        
        print(f"Final Best Travel Distance: {self.best_path_distance:.2f}")
        print(f"Number of Vehicles Used: {self.best_vehicle_num}")
        print(f"Optimized Path: {BasicACO.format_optimized_path(self.best_path)}\n")

    def select_next_index(self, ant):
        """
        Select the next node.
        :param ant:
        :return:
        """
        current_index = ant.current_index
        index_to_visit = ant.index_to_visit

        transition_prob = np.power(self.graph.pheromone_mat[current_index][index_to_visit], self.alpha) * \
            np.power(self.graph.heuristic_info_mat[current_index][index_to_visit], self.beta)
        transition_prob = transition_prob / np.sum(transition_prob)

        if np.random.rand() < self.q0:
            max_prob_index = np.argmax(transition_prob)
            next_index = index_to_visit[max_prob_index]
        else:
            # Use the roulette wheel algorithm.
            next_index = BasicACO.stochastic_accept(index_to_visit, transition_prob)
        return next_index

    @staticmethod
    def stochastic_accept(index_to_visit, transition_prob):
        """
        Roulette wheel selection.
        :param index_to_visit: a list of N indices (list or tuple).
        :param transition_prob:
        :return: selected index.
        """
        # Calculate N and the maximum fitness value.
        N = len(index_to_visit)

        # Normalize.
        sum_tran_prob = np.sum(transition_prob)
        norm_transition_prob = transition_prob / sum_tran_prob

        # Selection: O(1).
        while True:
            # Randomly select an individual with uniform probability.
            ind = int(N * random.random())
            if random.random() <= norm_transition_prob[ind]:
                return index_to_visit[ind]
