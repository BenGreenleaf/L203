import heapq
import math

#neighbour node, weight


graph_w = {1: [(2, 0, "north")],
           2: [(1, 0)]
           }

def dijkstra_shortest_path(graph_w, start, goal):
    dist = {start: 0.0}
    parent = {start: None}
    pq = [(0.0, start)]

    while pq:
        d, u = heapq.heappop(pq)
        if u == goal:
            break
        if d != dist.get(u, float("inf")):
            continue
        for v, w in graph_w[u]:
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

def turn_decider(last_node, current_orientation, next_node):
    for i in graph_w[last_node]:
        if i[0] == next_node:
            direction = i[2]
            break
    
    if direction == "north":
        if current_orientation == "north":
            return "straight"
        elif current_orientation == "east":
            return "left"
        elif current_orientation == "south":
            return "180 turn"
        elif current_orientation == "west":
            return "right"
    elif direction == "east":
        if current_orientation == "north":
            return "right"
        elif current_orientation == "east":
            return "straight"
        elif current_orientation == "south":
            return "left"
        elif current_orientation == "west":
            return "180 turn"
    elif direction == "south":
        if current_orientation == "north":
            return "180 turn"
        elif current_orientation == "east":
            return "right"
        elif current_orientation == "south":
            return "straight"
        elif current_orientation == "west":
            return "left"
    elif direction == "west":
        if current_orientation == "north":
            return "left"
        elif current_orientation == "east":
            return "180 turn"
        elif current_orientation == "south":
            return "right"
        elif current_orientation == "west":
            return "straight"
        
def convert_path_to_actions(path, current_orientation):
    actions = []
    for i in range(1, len(path)-1):
        last_node = path[i]
        next_node = path[i+1]
        action = turn_decider(last_node, current_orientation, next_node)
        actions.append(action)
        current_orientation = graph_w[last_node][next_node][2] # update orientation based on the direction of the next node
    return actions


