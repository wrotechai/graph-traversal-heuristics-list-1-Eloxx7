from graph import create_and_show_graph, convert_to_seconds, convert_format, is_service_active
from heapq import heappush, heappop, heapify



def dijkstra(G, ini, end, initial_time, criterion, target_parent_station=None):
    visited = set()
    distance = {}
    previous = {}
    end_trip = None
    for node in G.nodes:
        if criterion == 't':
            distance[node] = float("inf")
        else:
            distance[node] = (float("inf"), float("inf"))

    if criterion =='t':
        pq = [(initial_time, ini)]
        distance[ini] = initial_time
    else:
        pq = [(0,initial_time,ini,None)]
        distance[ini] = (0, 0)
    heapify(pq)

    while pq:
        if criterion == 't':
            current_time, current = heappop(pq)
            current_parent = G.nodes[current].get('parent_station')
            if current == end or current_parent == target_parent_station:
                end = current
                break
            if current in visited:
                continue
            visited.add(current)
            for edge in G.out_edges(current, data=True):
                neighbor = edge[1]
                if not edge[2]['isTransfer']:
                    if edge[2]['departure'] >= current_time:
                        if edge[2]['arrival'] < distance[neighbor]:
                            distance[neighbor] = edge[2]['arrival']
                            previous[neighbor] = (current, edge[2]['departure'], edge[2]['arrival'], edge[2]['trip_id'])
                            heappush(pq, (edge[2]['arrival'], neighbor))
                else:
                    if current_time < distance[neighbor]:
                        distance[neighbor] = current_time
                        previous[neighbor] = (current, None, current_time, None)
                        heappush(pq, (current_time, neighbor))
        else:
            current_num_transfer, current_time, current, current_trip = heappop(pq)
            if (current, current_num_transfer, current_trip) in visited:
                continue
            visited.add((current, current_num_transfer, current_trip))
            current_parent = G.nodes[current].get('parent_station')
            if current == end or current_parent == target_parent_station:
                end = current
                end_trip = current_trip
                break
            for edge in G.out_edges(current, data=True):
                neighbor = edge[1]
                if not edge[2]['isTransfer']:
                    if edge[2]['departure'] >= current_time:
                        is_new_transfer = current_trip is not None and current_trip != edge[2]['trip_id']
                        new_num_transfer = current_num_transfer + (1 if is_new_transfer else 0)
                        new_cost = (new_num_transfer, edge[2]['arrival'])
                        if new_cost < distance[neighbor]:
                            distance[neighbor] = new_cost
                            previous[(neighbor, edge[2]['trip_id'])] = (current, current_trip, edge[2]['departure'], edge[2]['arrival'], edge[2]['trip_id'])
                            heappush(pq, (new_num_transfer, edge[2]['arrival'], neighbor, edge[2]['trip_id']))
                else:
                    if (current_num_transfer, current_time) < distance[neighbor]:
                        distance[neighbor] = (current_num_transfer, current_time)
                        previous[(neighbor, current_trip)] = (current, current_trip, None, current_time, current_trip)
                        heappush(pq, (current_num_transfer, current_time, neighbor, current_trip))
    return distance, previous, end_trip, end

def reconstruct(start, end, previous, end_trip=None):
    path = []
    current = end
    current_trip = end_trip
    while start != current:
        if end_trip is not None:  # p criterion - keyed by (node, trip)
            prev_node, prev_trip, departure, arrival, trip_id = previous[(current, current_trip)]
            path.insert(0, (current, departure, arrival, trip_id))
            current = prev_node
            current_trip = prev_trip
        else:  # t criterion - keyed by node
            prev_node, departure, arrival, trip_id = previous[current]
            path.insert(0, (current, departure, arrival, trip_id))
            current = prev_node
    path.insert(0, (start, None, None, None))
    return path