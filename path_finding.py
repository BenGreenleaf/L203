import heapq
import math

#neighbour node, weight
#all in cm

graph_list = {1: [(2, 10, "north")],
           2: [(1, 10, "south"), (3, 75.6, "east"), (42, 75.6, "west")],
           3: [(2, 75.6, "west"), (4, 26.5, "south"), (5, 30.4, "east")],
           4: [(3, 26.5, "north")],
           5: [(3, 30.4, "west"), (6, 26.5, "south"), (7, 82.7, "north")],
           6: [(5, 26.5, "north")],
           7: [(5, 82.7, "south"), (8, 10, "north")],
           8: [(7, 10, "south"), (9, 10, "north")],
           9: [(8, 10, "south"), (10, 9.5, "north")],
           10: [(9, 9.5, "south"), (11, 10, "north")],
           11: [(10, 10, "south"), (12, 9.5, "north")],
           12: [(11, 9.5, "south"), (13, 10, "north")],
           13: [(12, 10, "south"), (14, 40.8, "north")],
           14: [(13, 40.8, "south"), (15, 105, "west")],
           15: [(14, 105, "east"), (16, 139, "south"), (33, 107, "west")],
           
           33: [(15, 107, "east"), (40, 41.7, "south")],
           40: [(33, 41.7, "north"), (34, 9.6, "south")],
           34: [(40, 9.6, "north"), (35, 9, "south")],
           35: [(34, 9, "north"), (36, 10, "south")],
           36: [(35, 10, "north"), (37, 9.7, "south")],
           37: [(36, 9.7, "north"), (38, 10, "south")],
           38: [(37, 10, "north"), (39, 9.5, "south")],
           39: [(38, 9.5, "north"), (41, 81.7, "south")],
           41: [(39, 81.7, "north"), (44, 27, "south"), (42, 105.5, "east")],
           44: [(41, 27, "north")],
           42: [(41, 105.5, "west"), (43, 26.2, "south"), (2, 75.6, "east")],
           43: [(42, 26.2, "north")],

           }

graph = {
    node: {nbr: (dist, direction) for nbr, dist, direction in edges}
    for node, edges in graph_list.items()
}

def dijkstra_shortest_path(graph, start, goal):
    dist = {start: 0.0}
    parent = {start: None}
    pq = [(0.0, start)]

    while pq:
        d, u = heapq.heappop(pq)
        if u == goal:
            break
        if d != dist.get(u, float("inf")):
            continue

        for v, (w, _direction) in graph[u].items():
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                parent[v] = u
                heapq.heappush(pq, (nd, v))

    if goal not in parent:
        return None, None

    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    return path, dist[goal]

def turn_decider(graph, last_node, current_orientation, next_node):
    _dist, direction = graph[last_node][next_node]

    turn_map = {
        "north": {"north": "straight", "east": "left",     "south": "180 turn", "west": "right"},
        "east":  {"north": "right",    "east": "straight", "south": "left",     "west": "180 turn"},
        "south": {"north": "180 turn", "east": "right",    "south": "straight", "west": "left"},
        "west":  {"north": "left",     "east": "180 turn", "south": "right",    "west": "straight"},
    }

    return turn_map[direction][current_orientation]

def convert_path_to_actions(graph, path, current_orientation):
    actions = []
    for u, v in zip(path[:-1], path[1:]):
        actions.append(turn_decider(graph, u, current_orientation, v))
        _dist, direction = graph[u][v]
        current_orientation = direction
    return actions

path, total_dist = dijkstra_shortest_path(graph, 1, 16)
print("Shortest path:", path)
print("Total distance:", total_dist)
print("Directions:", convert_path_to_actions(graph, path, "north")[1:])