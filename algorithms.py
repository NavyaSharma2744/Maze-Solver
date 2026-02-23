"""
Search Algorithms: BFS, DFS, A*
"""

from collections import deque
import heapq


class SearchResult:
    def __init__(self, path=None, explored=None, nodes_expanded=0, success=False):
        self.path = path or []
        self.explored = explored or set()
        self.nodes_expanded = nodes_expanded
        self.success = success


def reconstruct_path(came_from, current):
    """Trace back from goal to start using parent pointers."""
    path = []
    while current is not None:
        path.append(current)
        current = came_from.get(current)
    path.reverse()
    return path


def bfs(maze, enemy=None):
    """BFS - Queue (FIFO) - Guarantees shortest path."""
    start = maze.start

    queue = deque([start])
    came_from = {start: None}
    visited = {start}
    explored = set()
    nodes_expanded = 0

    while queue:
        current = queue.popleft()  # FIFO: remove from front
        nodes_expanded += 1
        explored.add(current)

        if maze.is_exit(*current):
            return SearchResult(reconstruct_path(came_from, current), explored, nodes_expanded, True)

        for neighbor in maze.get_neighbors(*current):
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                queue.append(neighbor)  # add to back

    return SearchResult([], explored, nodes_expanded, False)


def dfs(maze, enemy=None):
    """DFS - Stack (LIFO) - Does NOT guarantee shortest path."""
    start = maze.start

    stack = [start]
    came_from = {start: None}
    visited = {start}
    explored = set()
    nodes_expanded = 0

    while stack:
        current = stack.pop()  # LIFO: remove from top
        nodes_expanded += 1
        explored.add(current)

        if maze.is_exit(*current):
            return SearchResult(reconstruct_path(came_from, current), explored, nodes_expanded, True)

        for neighbor in maze.get_neighbors(*current):
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                stack.append(neighbor)  # add to top

    return SearchResult([], explored, nodes_expanded, False)


def manhattan_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def heuristic(maze, pos):
    """Manhattan distance to nearest exit."""
    return min(manhattan_distance(pos, exit_pos) for exit_pos in maze.exits)


def astar(maze, enemy=None):
    """A* - Priority Queue by f=g+h - Optimal and efficient."""
    start = maze.start

    g_score = {start: 0}
    f_score = {start: heuristic(maze, start)}

    counter = 0
    open_set = [(f_score[start], counter, start)]
    open_set_hash = {start}

    came_from = {start: None}
    explored = set()
    nodes_expanded = 0

    while open_set:
        _, _, current = heapq.heappop(open_set)  # pop lowest f
        open_set_hash.discard(current)
        nodes_expanded += 1
        explored.add(current)

        if maze.is_exit(*current):
            return SearchResult(reconstruct_path(came_from, current), explored, nodes_expanded, True)

        for neighbor in maze.get_neighbors(*current):
            tentative_g = g_score[current] + 1

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f = tentative_g + heuristic(maze, neighbor)
                f_score[neighbor] = f

                if neighbor not in open_set_hash:
                    counter += 1
                    heapq.heappush(open_set, (f, counter, neighbor))
                    open_set_hash.add(neighbor)

    return SearchResult([], explored, nodes_expanded, False)


if __name__ == "__main__":
    from maze import Maze

    maze = Maze()
    print(f"Maze: {maze.rows}x{maze.cols}, Start: {maze.start}, Exits: {maze.exits}\n")

    for name, algo in [("BFS", bfs), ("DFS", dfs), ("A*", astar)]:
        result = algo(maze)
        print(f"{name}: path={len(result.path)-1}, nodes={result.nodes_expanded}")
