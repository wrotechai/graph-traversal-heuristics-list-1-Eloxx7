
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime

stops = pd.read_csv('stops.txt')
stop_times = pd.read_csv('stop_times.txt')
trips = pd.read_csv('trips.txt')
calendar = pd.read_csv('calendar.txt')
calendar_dates = pd.read_csv('calendar_dates.txt')
routes = pd.read_csv('routes.txt')
pd.set_option('display.max_columns', None)

weekday = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

def is_service_active(service_id, date, index_weekday):
    exceptions = calendar_dates[(calendar_dates['service_id'] == service_id) & (calendar_dates['date'] == date)]

    if len(exceptions) > 0:
        return exceptions.iloc[0]['exception_type'] == 1

    service = calendar[calendar['service_id'] == service_id]

    if len(service) == 0:
        return False

    service = service.iloc[0]

    if not service['end_date'] >= date >= service['start_date']:
        return False

    return service[weekday[index_weekday]] == 1

def convert_format(time):
    hours, remainder = divmod(time, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
def convert_to_seconds(time):
    return int(time.split(':')[0]) * 3600 + int(time.split(':')[1]) * 60 + int(time.split(':')[2])

def create_and_show_graph(input_date):
    G = nx.MultiDiGraph()
    positions = {}
    dt = datetime.strptime(input_date, '%Y%m%d')
    index_weekday = dt.weekday()
    active_trips = []

    for _ ,row in trips.iterrows():
        if is_service_active(row['service_id'], int(input_date), index_weekday):
            active_trips.append(row['trip_id'])

    # create the nodes and visualize them like it will be in real life
    for _, row in stops.iterrows():
        if row['location_type'] == 0:
            G.add_node(int(row['stop_id']), name=row['stop_name'], lat=row['stop_lat'], lon=row['stop_lon'], parent_station=row['parent_station'])
            positions[row['stop_id']] = (row['stop_lon'], row['stop_lat'])


    active_stop_times = stop_times[stop_times['trip_id'].isin(active_trips)]
    for trip_id, group in active_stop_times.groupby('trip_id'):
        for n in range(len(group ) -1):
            current = group.iloc[n]
            next_stop = group.iloc[ n +1]
            t1 = current['departure_time']
            t2 = next_stop['arrival_time']
            t1_sec = convert_to_seconds(t1)
            t2_sec = convert_to_seconds(t2)
            G.add_edge(int(current['stop_id']), int(next_stop['stop_id']), departure=t1_sec, arrival=t2_sec, weight=t2_sec -t1_sec, isTransfer=False, trip_id=trip_id)
    '''
    Create the table with all the departure times of all platforms
    '''
    departures = {}
    for _, row in active_stop_times.iterrows():
        stop_id = row['stop_id']
        departure_time_sec = convert_to_seconds(row['departure_time'])
        if stop_id not in departures:
            departures[stop_id] = []
        departures[stop_id].append(departure_time_sec)

    for stop_id in departures:
        departures[stop_id].sort()


    for _, group in stops.groupby('parent_station'):
        platform_ids = group['stop_id'].tolist()
        for i in range(len(platform_ids)):
            for j in range(len(platform_ids)):
                if i != j:
                    G.add_edge(platform_ids[i], platform_ids[j], weight=0, isTransfer=True)

    trip_edges = [(u, v) for u, v, d in G.edges(data=True) if d['isTransfer'] == False]
    transfer_edges = [(u, v) for u, v, d in G.edges(data=True) if d['isTransfer'] == True]

    # plt.figure()
    # nx.draw_networkx_edges(G, pos=positions, edgelist=trip_edges, edge_color='black')
    # nx.draw_networkx_edges(G, pos=positions, edgelist=transfer_edges, edge_color='yellow')
    # nx.draw_networkx_nodes(G, pos=positions, node_size=10)
    # plt.show(block=False)
    return G