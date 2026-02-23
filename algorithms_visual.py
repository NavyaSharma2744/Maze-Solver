"""
Step-by-step visual versions of search algorithms.
Yields state at each step for animation.
"""

from collections import deque
import heapq


class AlgorithmStep:
    def __init__(self, step_num, current_pos, frontier, explored, path_so_far,
                 action, message, is_goal=False, f_scores=None):
        self.step_num = step_num
        self.current_pos = current_pos
        self.frontier = frontier
        self.explored = explored
        self.path_so_far = path_so_far
        self.action = action
        self.message = message
        self.is_goal = is_goal
        self.f_scores = f_scores


def reconstruct_path(came_from, current):
    path = []
    while current is not None:
        path.append(current)
        current = came_from.get(current)
    path.reverse()
    return path


def bfs_visual(maze):
    """BFS step-by-step. Uses QUEUE (FIFO)."""
    start = maze.start
    queue = deque([start])
    visited = {start}
    came_from = {start: None}
    explored = set()
    step = 0

    yield AlgorithmStep(step, start, list(queue), set(), [start], 'start',
                        f"START: Add {start} to queue")

    while queue:
        step += 1
        current = queue.popleft()
        explored.add(current)
        path = reconstruct_path(came_from, current)

        yield AlgorithmStep(step, current, list(queue), explored.copy(), path, 'pop',
                            f"POP: {current} from FRONT")

        if maze.is_exit(*current):
            yield AlgorithmStep(step, current, list(queue), explored.copy(), path, 'goal',
                                f"GOAL! Path: {len(path)-1} steps", is_goal=True)
            return

        for neighbor in maze.get_neighbors(*current):
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                queue.append(neighbor)
                step += 1
                yield AlgorithmStep(step, current, list(queue), explored.copy(), path, 'push',
                                    f"PUSH: {neighbor} to BACK")


def dfs_visual(maze):
    """DFS step-by-step. Uses STACK (LIFO)."""
    start = maze.start
    stack = [start]
    visited = {start}
    came_from = {start: None}
    explored = set()
    step = 0

    yield AlgorithmStep(step, start, list(stack), set(), [start], 'start',
                        f"START: Add {start} to stack")

    while stack:
        step += 1
        current = stack.pop()
        explored.add(current)
        path = reconstruct_path(came_from, current)

        yield AlgorithmStep(step, current, list(stack), explored.copy(), path, 'pop',
                            f"POP: {current} from TOP")

        if maze.is_exit(*current):
            yield AlgorithmStep(step, current, list(stack), explored.copy(), path, 'goal',
                                f"GOAL! Path: {len(path)-1} steps", is_goal=True)
            return

        for neighbor in maze.get_neighbors(*current):
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                stack.append(neighbor)
                step += 1
                yield AlgorithmStep(step, current, list(stack), explored.copy(), path, 'push',
                                    f"PUSH: {neighbor} to TOP")


def manhattan_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def astar_visual(maze):
    """A* step-by-step. Uses PRIORITY QUEUE by f=g+h."""
    start = maze.start

    def h(pos):
        return min(manhattan_distance(pos, e) for e in maze.exits)

    g_score = {start: 0}
    f_score = {start: h(start)}
    counter = 0
    open_set = [(f_score[start], counter, start)]
    open_set_hash = {start}
    came_from = {start: None}
    explored = set()
    step = 0

    def get_frontier():
        return [item[2] for item in sorted(open_set)]

    yield AlgorithmStep(step, start, get_frontier(), set(), [start], 'start',
                        f"START: Add {start} with f={f_score[start]}")

    while open_set:
        step += 1
        f, _, current = heapq.heappop(open_set)
        open_set_hash.discard(current)
        explored.add(current)
        path = reconstruct_path(came_from, current)
        g = g_score[current]

        yield AlgorithmStep(step, current, get_frontier(), explored.copy(), path, 'pop',
                            f"POP: {current} with f={f} (g={g}, h={f-g})")

        if maze.is_exit(*current):
            yield AlgorithmStep(step, current, get_frontier(), explored.copy(), path, 'goal',
                                f"GOAL! Path: {len(path)-1} steps", is_goal=True)
            return

        for neighbor in maze.get_neighbors(*current):
            tentative_g = g_score[current] + 1

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                new_f = tentative_g + h(neighbor)
                f_score[neighbor] = new_f

                if neighbor not in open_set_hash:
                    counter += 1
                    heapq.heappush(open_set, (new_f, counter, neighbor))
                    open_set_hash.add(neighbor)
                    step += 1
                    yield AlgorithmStep(step, current, get_frontier(), explored.copy(), path, 'push',
                                        f"PUSH: {neighbor} with f={new_f}")


if __name__ == "__main__":
    from maze import Maze
    maze = Maze()

    print("BFS Visual Test:")
    for s in bfs_visual(maze):
        print(f"  Step {s.step_num}: {s.message}")
        if s.is_goal:
            break
