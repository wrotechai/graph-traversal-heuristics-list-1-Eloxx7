from astar import astar, reconstruct
import random

def compute_cost_matrix(G, stops_list, initial_time, criterion, parent_stations, algorithm='astar'):
    n = len(stops_list)
    cost_matrix = [[float('inf')] * n for _ in range(n)]
    path_matrix = [[None] * n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if i != j:
                if algorithm == 'dijkstra':
                    from dijkstra import dijkstra
                    distances, previous, end_trip, end = dijkstra(
                        G, stops_list[i], stops_list[j], initial_time, criterion, parent_stations[j]
                    )
                else:
                    distances, previous, end_trip, end = astar(
                        G, stops_list[i], stops_list[j], initial_time, criterion, parent_stations[j]
                    )

    return cost_matrix, path_matrix


def total_cost(route, cost_matrix):
    total = 0
    for i in range(len(route)):
        total += cost_matrix[route[i]][route[(i + 1) % len(route)]]
    return total


def get_neighbors_2opt_sampled(route, sample_size=None):
    n = len(route)
    all_pairs = [(i, j) for i in range(1, n - 1) for j in range(i + 1, n)]

    if sample_size is None or sample_size >= len(all_pairs):
        pairs = all_pairs
    else:
        pairs = random.sample(all_pairs, sample_size)

    neighbors = []
    for i, j in pairs:
        new_route = route[:i] + route[i:j + 1][::-1] + route[j + 1:]
        neighbors.append((new_route, (i, j)))
    return neighbors


def tabu_search(G, stops_list, initial_time, criterion, parent_stations, step_limit=100, algorithm='astar'):
    L = len(stops_list)
    tabu_size = L # variable size based on length of L
    print("Computing cost matrix...")
    cost_matrix, path_matrix = compute_cost_matrix(G, stops_list, initial_time, criterion, parent_stations, algorithm)
    # initial solution: 0 -> 1 -> 2 -> ... -> n-1 -> 0
    current = list(range(L))
    random.shuffle(current)
    best = current[:]
    best_cost = total_cost(best, cost_matrix)

    tabu_list = []

    for step in range(step_limit):
        sample_size = len(stops_list) * 2
        neighbors = get_neighbors_2opt_sampled(current, sample_size)
        best_neighbor = None
        best_neighbor_cost = float('inf')
        best_move = None

        for neighbor, move in neighbors:
            cost = total_cost(neighbor, cost_matrix)
            if (move not in tabu_list or cost < best_cost) and cost < best_neighbor_cost:
                best_neighbor = neighbor
                best_neighbor_cost = cost
                best_move = move

        if best_neighbor is None:
            break

        current = best_neighbor
        tabu_list.append(best_move)
        if len(tabu_list) > tabu_size:
            tabu_list.pop(0)

        if best_neighbor_cost < best_cost:
            best = best_neighbor[:]
            best_cost = best_neighbor_cost

        print(f"Step {step+1}: cost={best_cost}")

    return best, best_cost, path_matrix