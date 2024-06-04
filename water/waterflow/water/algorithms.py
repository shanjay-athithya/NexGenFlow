import heapq
from .models import Node, Edge
from collections import deque
import logging

logging.basicConfig(level=logging.DEBUG)

def dijkstra(graph, start_node, target_node=None):
    """Finds the shortest path from start node to target node using Dijkstra's algorithm."""
    # Create a priority queue (min-heap)
    priority_queue = []
    
    # Initialize distances and previous nodes
    distances = {node: float('inf') for node in graph}
    distances[start_node] = 0  # Distance from start node to itself is 0
    previous_nodes = {node: None for node in graph}
    
    # Push start node with distance 0 into the queue
    heapq.heappush(priority_queue, (0, start_node.id))
    
    while priority_queue:
        # Pop the node with the smallest distance
        current_distance, current_node_id = heapq.heappop(priority_queue)
        current_node = Node.objects.get(id=current_node_id)
        
        # If the target node is reached, stop the search
        if target_node and current_node == target_node:
            break
        
        # Get all the edges from the current node
        edges = Edge.objects.filter(source=current_node)
        
        for edge in edges:
            neighbor = edge.target
            weight = edge.length  # Adjust this to your model's attribute name
            
            # Calculate the new distance to the neighbor
            distance = current_distance + weight
            
            # Check if we have found a shorter path
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                
                # Push the new distance and neighbor node into the priority queue
                heapq.heappush(priority_queue, (distance, neighbor.id))
    
    # Return the shortest distances and paths
    if target_node:
        # Calculate path to target node
        path = []
        current_node = target_node
        while current_node:
            path.append(current_node)
            current_node = previous_nodes[current_node]
        path.reverse()
        return distances[target_node], path
    
    # If no specific target, return distances and previous nodes
    return distances, previous_nodes

def bfs_capacity(graph, source, sink, parent):
    visited = set()
    queue = deque([source])
    visited.add(source)
    
    while queue:
        current_node = queue.popleft()
        
        # Ensure that `graph[current_node]` is a dictionary
        if isinstance(graph[current_node], dict):
            for neighbor, capacity in graph[current_node].items():
                if neighbor not in visited and capacity > 0:
                    queue.append(neighbor)
                    visited.add(neighbor)
                    parent[neighbor] = current_node
                    
                    if neighbor == sink:
                        return True
    
    return False

def edmonds_karp(graph, source, sink):
    """Implements the Edmonds-Karp algorithm for finding the maximum flow in a network."""
    try:
        logging.debug(f"Starting Edmonds-Karp algorithm with source {source} and sink {sink}")
        flow = 0
        parent = {}

        while bfs_capacity(graph, source, sink, parent):
            path_flow = float('inf')
            s = sink
            while s != source:
                u = parent[s]
                path_flow = min(path_flow, graph[u][s])
                s = u

            v = sink
            while v != source:
                u = parent[v]
                graph[u][v] -= path_flow
                graph[v][u] += path_flow
                v = u

            flow += path_flow

        # Extract nodes in the maximum flow path
        max_flow_path = []
        s = sink
        while s != source:
            if s in parent:
                max_flow_path.append(s)
                s = parent[s]
            else:
                break
        max_flow_path.append(source)
        max_flow_path.reverse()

        logging.debug(f"Completed Edmonds-Karp algorithm with flow: {flow}")
        return flow, max_flow_path

    except KeyError as e:
        logging.error(f"KeyError: {e}")
        raise ValueError("Invalid graph structure: missing edges or nodes.") from e
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise ValueError("An error occurred during the algorithm execution.") from e

def ford_fulkerson(graph, source, sink):
    parent = {}
    max_flow = 0

    def bfs(source, sink):
        visited = set()
        queue = [source]
        visited.add(source)
        
        while queue:
            u = queue.pop(0)
            for v in graph[u]:
                if v not in visited and graph[u][v] > 0:
                    queue.append(v)
                    visited.add(v)
                    parent[v] = u
                    if v == sink:
                        return True
        return False
    
    while bfs(source, sink):
        path_flow = float('Inf')
        s = sink
        while s != source:
            path_flow = min(path_flow, graph[parent[s]][s])
            s = parent[s]
        
        v = sink
        while v != source:
            u = parent[v]
            graph[u][v] -= path_flow
            graph[v][u] += path_flow
            v = parent[v]
        
        max_flow += path_flow
    
    # Extract nodes in the maximum flow path
    max_flow_path = []
    s = sink
    while s != source:
        if s in parent:
            max_flow_path.append(s)
            s = parent[s]
        else:
            break
    max_flow_path.append(source)
    max_flow_path.reverse()

    return max_flow, max_flow_path

def dinic(graph, source, sink):
    level = {}
    parent = {}

    def bfs_level_graph():
        for node in graph:
            level[node] = -1
        level[source] = 0
        
        queue = [source]
        while queue:
            u = queue.pop(0)
            for v in graph[u]:
                if level[v] < 0 and graph[u][v] > 0:
                    level[v] = level[u] + 1
                    queue.append(v)
                    parent[v] = u
        return level[sink] >= 0
    
    def dfs_flow(u, flow):
        if u == sink:
            return flow
        for v in graph[u]:
            if level[v] == level[u] + 1 and graph[u][v] > 0:
                min_flow = min(flow, graph[u][v])
                result = dfs_flow(v, min_flow)
                if result > 0:
                    graph[u][v] -= result
                    graph[v][u] += result
                    return result
        return 0
    
    max_flow = 0
    while bfs_level_graph():
        while True:
            flow = dfs_flow(source, float('Inf'))
            if flow == 0:
                break
            max_flow += flow

    # Extract nodes in the maximum flow path
    max_flow_path = []
    s = sink
    while s != source:
        if s in parent:
            max_flow_path.append(s)
            s = parent[s]
        else:
            break
    max_flow_path.append(source)
    max_flow_path.reverse()

    return max_flow, max_flow_path

def push_relabel(graph, source, sink):
    n = len(graph)
    excess = {u: 0 for u in graph}
    height = {u: 0 for u in graph}
    height[source] = n
    excess[source] = float('Inf')
    parent = {}

    for v in graph[source]:
        graph[source][v] -= excess[source]
        graph[v][source] += excess[source]
        excess[v] += excess[source]
        parent[v] = source

    def push(u):
        for v in graph[u]:
            if graph[u][v] > 0 and height[u] > height[v]:
                flow = min(excess[u], graph[u][v])
                graph[u][v] -= flow
                graph[v][u] += flow
                excess[u] -= flow
                excess[v] += flow
                parent[v] = u
                return True
        return False
    
    def relabel(u):
        min_height = float('Inf')
        for v in graph[u]:
            if graph[u][v] > 0:
                min_height = min(min_height, height[v])
        height[u] = min_height + 1
    
    active = [u for u in graph if u != source and u != sink]
    while active:
        u = active.pop(0)
        while excess[u] > 0:
            if not push(u):
                relabel(u)
        if excess[u] > 0:
            active.append(u)
    
    max_flow = excess[sink]

    # Extract nodes in the maximum flow path
    max_flow_path = []
    s = sink
    while s != source:
        if s in parent:
            max_flow_path.append(s)
            s = parent[s]
        else:
            break
    max_flow_path.append(source)
    max_flow_path.reverse()

    return max_flow, max_flow_path
