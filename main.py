import sys
import time
import pandas as pd
from astar import astar, reconstruct
from dijkstra import dijkstra, reconstruct as reconstruct_dijkstra
from graph import create_and_show_graph, convert_to_seconds, convert_format
from graph import trips, routes
from tabu import tabu_search

stops = pd.read_csv('stops.txt')


def get_stop_id(stop_name):
    parent = stops[stops['stop_name'] == stop_name]
    if len(parent) == 0:
        print(f"Stop '{stop_name}' not found.", file=sys.stderr)
        sys.exit(1)
    parent_id = parent[parent['location_type'] == 1].iloc[0]['stop_id']
    platform = stops[(stops['parent_station'] == parent_id) & (stops['location_type'] == 0)].iloc[0]['stop_id']
    return platform, parent_id


def get_line_name(trip_id):
    if trip_id is None:
        return "transfer"
    route_id = trips[trips['trip_id'] == trip_id].iloc[0]['route_id']
    route = routes[routes['route_id'] == route_id].iloc[0]
    return route['route_short_name'] if pd.notna(route['route_short_name']) else route['route_long_name']


def run_algorithm(algorithm, G, initial_stop, last_stop, initial_time, criterion, target_parent_station):
    if algorithm == 'dijkstra':
        distances, previous, end_trip, end = dijkstra(G, initial_stop, last_stop, initial_time, criterion, target_parent_station)
        path = reconstruct_dijkstra(initial_stop, end, previous, end_trip=end_trip if criterion == 'p' else None)
    else:
        distances, previous, end_trip, end = astar(G, initial_stop, last_stop, initial_time, criterion, target_parent_station)
        path = reconstruct(initial_stop, end, previous, end_trip=end_trip if criterion == 'p' else None)
    return distances, path, end


# --- TASK 1 INPUT ---
stop_a = input("Starting stop: ")
stop_b = input("Ending stop: ")
criterion = input("Criterion (t/p): ")
algorithm = input("Algorithm (dijkstra/astar): ")
start_time_str = input("Start time (HH:MM:SS): ")
input_date = input("Date (YYYYMMDD): ")

initial_time = convert_to_seconds(start_time_str)
G = create_and_show_graph(input_date)

initial_stop, _ = get_stop_id(stop_a)
last_stop, target_parent_station = get_stop_id(stop_b)

# --- TASK 1 RUN ---
calc_start = time.time()
distances, path, end = run_algorithm(algorithm, G, initial_stop, last_stop, initial_time, criterion, target_parent_station)
calc_time = time.time() - calc_start

# --- STDOUT: path details ---
for i in range(len(path) - 1):
    stop_id, departure, arrival, trip_id = path[i]
    next_stop_id, _, next_arrival, next_trip_id = path[i + 1]

    if trip_id is None and next_trip_id is None:
        continue

    start_name = stops[stops['stop_id'] == stop_id].iloc[0]['stop_name']
    end_name = stops[stops['stop_id'] == next_stop_id].iloc[0]['stop_name']
    dep_str = convert_format(departure) if departure is not None else start_time_str
    arr_str = convert_format(next_arrival) if next_arrival is not None else start_time_str
    line = get_line_name(next_trip_id or trip_id)

    print(f"{start_name} -> {end_name} | line: {line} | dep: {dep_str} | arr: {arr_str}")

# --- STDERR: criterion value + calc time ---
if criterion == 't':
    print(f"Criterion: arrival time = {convert_format(distances[end])}", file=sys.stderr)
else:
    transfers, arrival = distances[end]
    print(f"Criterion: transfers = {transfers}, arrival = {convert_format(arrival)}", file=sys.stderr)
print(f"Calculation time: {calc_time:.4f}s", file=sys.stderr)


# --- TASK 2 INPUT ---
print("\n=== TASK 2: TSP with Tabu Search ===")
stop_a_tsp = input("Starting stop: ")
stops_l_str = input("Stops to visit (semicolon separated): ")
criterion_tsp = input("Criterion (t/p): ")
algorithm_tsp = input("Algorithm (dijkstra/astar): ")
start_time_tsp = input("Start time (HH:MM:SS): ")
date_tsp = input("Date (YYYYMMDD): ")

initial_time_tsp = convert_to_seconds(start_time_tsp)
G_tsp = create_and_show_graph(date_tsp)

stops_to_visit = [stop_a_tsp] + stops_l_str.split(';')

stops_ids = []
parent_stations_list = []
for name in stops_to_visit:
    name = name.strip()
    platform, parent = get_stop_id(name)
    stops_ids.append(platform)
    parent_stations_list.append(parent)

# --- TASK 2 RUN ---
calc_start = time.time()
best_route, best_cost, path_matrix = tabu_search(
    G_tsp, stops_ids, initial_time_tsp, criterion_tsp, parent_stations_list,
    step_limit=50, algorithm=algorithm_tsp
)
calc_time = time.time() - calc_start

# --- STDOUT: route details ---
print("\nBest route:")
route_names = [stops_to_visit[i].strip() for i in best_route]
route_names.append(route_names[0])
for i in range(len(route_names) - 1):
    print(f"{route_names[i]} -> {route_names[i+1]}")

# --- STDERR: criterion value + calc time ---
if criterion_tsp == 't':
    print(f"Total cost: {convert_format(best_cost)}", file=sys.stderr)
else:
    print(f"Total transfers: {best_cost}", file=sys.stderr)
print(f"Calculation time: {calc_time:.4f}s", file=sys.stderr)