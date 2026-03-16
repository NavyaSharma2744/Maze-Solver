"""
algorithms.py
=============
Search algorithm implementations for the Maze Solver project.

Includes:
- BFS
- DFS
- A*
- Ant Colony Optimization (ACO)

Expected by main.py:
    from algorithms import bfs, dfs, astar, aco

This file is written to be fairly tolerant of different Maze class designs.
It tries these, in order:
1. maze.get_neighbors(pos)
2. maze.get_valid_neighbors(pos)
3. maze.neighbors(pos)
4. derive neighbors from common maze fields like walls/grid

Expected Maze fields/methods (at least some of these):
- maze.start -> (row, col)
- maze.exits -> list/set of exit cells
- maze.rows, maze.cols
- maze.walls OR maze.grid (optional fallback)
"""

from __future__ import annotations

import heapq
import math
import random
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


Position = Tuple[int, int]


@dataclass
class SearchResult:
    success: bool
    path: List[Position]
    explored: List[Position]
    nodes_expanded: int
    metadata: dict = field(default_factory=dict)


# ---------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------
def _is_goal(pos: Position, maze) -> bool:
    return pos in set(maze.exits)


def _heuristic(pos: Position, exits) -> int:
    """Manhattan distance to nearest exit."""
    return min(abs(pos[0] - er) + abs(pos[1] - ec) for er, ec in exits)


def _reconstruct_path(parent: Dict[Position, Optional[Position]], goal: Position) -> List[Position]:
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = parent.get(current)
    path.reverse()
    return path


def _in_bounds(maze, r: int, c: int) -> bool:
    return 0 <= r < maze.rows and 0 <= c < maze.cols


def _is_blocked_fallback(maze, pos: Position) -> bool:
    """
    Best-effort fallback wall check for common Maze designs.
    Adjust this if your maze.py uses a different representation.
    """
    r, c = pos

    # Case 1: maze.walls is a set of blocked cells
    if hasattr(maze, "walls"):
        walls = maze.walls
        if isinstance(walls, set):
            return pos in walls

    # Case 2: maze.grid with 1 = wall, 0 = free
    if hasattr(maze, "grid"):
        grid = maze.grid
        try:
            return grid[r][c] == 1
        except Exception:
            pass

    # Case 3: maze.maze with 1 = wall
    if hasattr(maze, "maze"):
        grid = maze.maze
        try:
            return grid[r][c] == 1
        except Exception:
            pass

    return False


def _get_neighbors(maze, pos: Position) -> List[Position]:
    """
    Tries multiple Maze APIs before falling back to manual 4-direction moves.
    """
    for method_name in ("get_neighbors", "get_valid_neighbors", "neighbors"):
        if hasattr(maze, method_name):
            method = getattr(maze, method_name)
            try:
                neighbors = method(pos)
                if neighbors is not None:
                    return list(neighbors)
            except TypeError:
                pass

    r, c = pos
    candidates = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
    valid = []

    for nr, nc in candidates:
        if not _in_bounds(maze, nr, nc):
            continue
        if _is_blocked_fallback(maze, (nr, nc)):
            continue
        valid.append((nr, nc))

    return valid


# ---------------------------------------------------------------------
# BFS
# ---------------------------------------------------------------------
def bfs(maze) -> SearchResult:
    start = maze.start
    exits = set(maze.exits)

    queue = deque([start])
    visited: Set[Position] = {start}
    parent: Dict[Position, Optional[Position]] = {start: None}
    explored: List[Position] = []
    nodes_expanded = 0

    while queue:
        current = queue.popleft()
        explored.append(current)
        nodes_expanded += 1

        if current in exits:
            return SearchResult(
                success=True,
                path=_reconstruct_path(parent, current),
                explored=explored,
                nodes_expanded=nodes_expanded,
            )

        for neighbor in _get_neighbors(maze, current):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)

    return SearchResult(
        success=False,
        path=[],
        explored=explored,
        nodes_expanded=nodes_expanded,
    )


# ---------------------------------------------------------------------
# DFS
# ---------------------------------------------------------------------
def dfs(maze) -> SearchResult:
    start = maze.start
    exits = set(maze.exits)

    stack = [start]
    visited: Set[Position] = {start}
    parent: Dict[Position, Optional[Position]] = {start: None}
    explored: List[Position] = []
    nodes_expanded = 0

    while stack:
        current = stack.pop()
        explored.append(current)
        nodes_expanded += 1

        if current in exits:
            return SearchResult(
                success=True,
                path=_reconstruct_path(parent, current),
                explored=explored,
                nodes_expanded=nodes_expanded,
            )

        neighbors = list(_get_neighbors(maze, current))
        neighbors.reverse()  # keeps traversal visually stable in many layouts

        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                stack.append(neighbor)

    return SearchResult(
        success=False,
        path=[],
        explored=explored,
        nodes_expanded=nodes_expanded,
    )


# ---------------------------------------------------------------------
# A*
# ---------------------------------------------------------------------
def astar(maze) -> SearchResult:
    start = maze.start
    exits = set(maze.exits)

    open_heap = []
    heapq.heappush(open_heap, (_heuristic(start, exits), 0, start))

    parent: Dict[Position, Optional[Position]] = {start: None}
    g_score: Dict[Position, int] = {start: 0}
    visited: Set[Position] = set()
    explored: List[Position] = []
    nodes_expanded = 0

    while open_heap:
        _, current_g, current = heapq.heappop(open_heap)

        if current in visited:
            continue

        visited.add(current)
        explored.append(current)
        nodes_expanded += 1

        if current in exits:
            return SearchResult(
                success=True,
                path=_reconstruct_path(parent, current),
                explored=explored,
                nodes_expanded=nodes_expanded,
            )

        for neighbor in _get_neighbors(maze, current):
            tentative_g = current_g + 1

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                parent[neighbor] = current
                f_score = tentative_g + _heuristic(neighbor, exits)
                heapq.heappush(open_heap, (f_score, tentative_g, neighbor))

    return SearchResult(
        success=False,
        path=[],
        explored=explored,
        nodes_expanded=nodes_expanded,
    )


# ---------------------------------------------------------------------
# ACO helpers
# ---------------------------------------------------------------------
def _path_length(path: List[Position]) -> int:
    return max(0, len(path) - 1)


def _weighted_choice(candidates, weights):
    total = sum(weights)
    if total <= 0:
        return random.choice(candidates)

    pick = random.uniform(0, total)
    running = 0.0
    for candidate, weight in zip(candidates, weights):
        running += weight
        if pick <= running:
            return candidate
    return candidates[-1]


def _build_ant_path(
    maze,
    pheromone: Dict[Tuple[Position, Position], float],
    alpha: float,
    beta: float,
    max_steps: int,
):
    """
    One ant performs a probabilistic walk from start to any exit.
    Returns:
        path, explored_cells, success
    """
    start = maze.start
    exits = set(maze.exits)

    current = start
    path = [current]
    explored = [current]
    visited_in_path = {current}

    for _ in range(max_steps):
        if current in exits:
            return path, explored, True

        neighbors = _get_neighbors(maze, current)

        if not neighbors:
            return path, explored, False

        # Prefer unvisited neighbors first; if none, allow revisits
        candidates = [n for n in neighbors if n not in visited_in_path]
        if not candidates:
            candidates = neighbors

        weights = []
        for nxt in candidates:
            edge = (current, nxt)
            tau = pheromone.get(edge, 1.0)

            # Heuristic = inverse of distance to nearest exit
            dist = _heuristic(nxt, exits)
            eta = 1.0 / (dist + 1)

            score = (tau ** alpha) * (eta ** beta)
            weights.append(score)

        next_cell = _weighted_choice(candidates, weights)

        current = next_cell
        path.append(current)
        explored.append(current)
        visited_in_path.add(current)

        if current in exits:
            return path, explored, True

    return path, explored, False


def _deposit_pheromone(
    pheromone: Dict[Tuple[Position, Position], float],
    path: List[Position],
    amount: float,
):
    if len(path) < 2:
        return

    for i in range(len(path) - 1):
        a = path[i]
        b = path[i + 1]
        pheromone[(a, b)] = pheromone.get((a, b), 1.0) + amount
        pheromone[(b, a)] = pheromone.get((b, a), 1.0) + amount


# ---------------------------------------------------------------------
# ACO
# ---------------------------------------------------------------------
def aco(
    maze,
    num_ants: int = 20,
    num_iterations: int = 35,
    alpha: float = 1.0,
    beta: float = 3.0,
    evaporation_rate: float = 0.25,
    q: float = 100.0,
    max_steps_multiplier: int = 4,
) -> SearchResult:
    """
    Ant Colony Optimization for maze solving.

    Notes:
    - ACO is probabilistic, so results may vary across runs.
    - BFS remains your shortest-path reference for comparison.
    """
    start = maze.start
    exits = set(maze.exits)

    if start in exits:
        return SearchResult(
            success=True,
            path=[start],
            explored=[start],
            nodes_expanded=1,
            metadata={"iterations": 0, "ants": 0},
        )

    all_cells = [
        (r, c)
        for r in range(maze.rows)
        for c in range(maze.cols)
        if not _is_blocked_fallback(maze, (r, c))
    ]

    # Initialize pheromone on visible transitions
    pheromone: Dict[Tuple[Position, Position], float] = {}
    for cell in all_cells:
        for nbr in _get_neighbors(maze, cell):
            pheromone[(cell, nbr)] = 1.0

    max_steps = max(maze.rows * maze.cols * max_steps_multiplier, 20)

    global_explored: List[Position] = []
    global_explored_seen: Set[Position] = set()
    nodes_expanded = 0

    best_path: List[Position] = []
    best_len = math.inf

    for _ in range(num_iterations):
        iteration_successes = []

        for _ant in range(num_ants):
            ant_path, ant_explored, success = _build_ant_path(
                maze=maze,
                pheromone=pheromone,
                alpha=alpha,
                beta=beta,
                max_steps=max_steps,
            )

            nodes_expanded += len(ant_explored)

            for cell in ant_explored:
                if cell not in global_explored_seen:
                    global_explored_seen.add(cell)
                    global_explored.append(cell)

            if success:
                length = _path_length(ant_path)
                iteration_successes.append((ant_path, length))

                if length < best_len:
                    best_len = length
                    best_path = ant_path[:]

        # Evaporation
        for edge in list(pheromone.keys()):
            pheromone[edge] *= (1.0 - evaporation_rate)
            if pheromone[edge] < 0.01:
                pheromone[edge] = 0.01

        # Deposit pheromone for successful ants
        for ant_path, length in iteration_successes:
            deposit = q / max(1, length)
            _deposit_pheromone(pheromone, ant_path, deposit)

    success = len(best_path) > 0 and best_path[-1] in exits

    return SearchResult(
        success=success,
        path=best_path if success else [],
        explored=global_explored,
        nodes_expanded=nodes_expanded,
        metadata={
            "iterations": num_iterations,
            "ants": num_ants,
            "best_length": best_len if success else None,
        },
    )
