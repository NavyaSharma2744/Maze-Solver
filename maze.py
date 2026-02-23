"""
Maze Environment Module
=======================
This module defines the maze grid and basic components.

Key Concepts:
- The maze is a 2D grid (list of lists)
- Each cell has a type: EMPTY, WALL, START, EXIT
- Coordinates are (row, col) where (0,0) is top-left
"""

import random
from collections import deque

# Cell type constants - makes code readable
EMPTY = 0   # Agent can walk here
WALL = 1    # Blocked cell
START = 2   # Starting position (only one)
EXIT = 3    # Exit positions (can be multiple)


class Maze:
    """
    Represents the maze grid environment.

    The maze uses a coordinate system where:
    - Row 0 is the top
    - Column 0 is the left
    - Position (r, c) means row r, column c
    """

    def __init__(self, grid=None):
        """
        Initialize maze with a grid.

        Args:
            grid: 2D list of cell types. If None, creates default 10x10 maze.
        """
        if grid is None:
            self.grid = self._create_default_maze()
        else:
            self.grid = grid

        self.rows = len(self.grid)
        self.cols = len(self.grid[0])

        # Find special positions
        self.start = self._find_start()
        self.exits = self._find_exits()

    def _create_default_maze(self):
        """
        Creates a 10x10 maze with walls, one start, and three exits.

        Legend:
        0 = Empty (walkable)
        1 = Wall (blocked)
        2 = Start
        3 = Exit
        """
        # Design a maze with interesting paths
        maze = [
            [2, 0, 0, 1, 0, 0, 0, 0, 0, 3],  # Row 0: Start at (0,0), Exit at (0,9)
            [0, 1, 0, 1, 0, 1, 1, 1, 0, 0],  # Row 1
            [0, 1, 0, 0, 0, 0, 0, 1, 0, 1],  # Row 2
            [0, 0, 0, 1, 1, 1, 0, 0, 0, 1],  # Row 3
            [1, 1, 0, 0, 0, 1, 0, 1, 0, 0],  # Row 4
            [0, 0, 0, 1, 0, 0, 0, 1, 1, 0],  # Row 5
            [0, 1, 1, 1, 0, 1, 0, 0, 0, 0],  # Row 6
            [0, 0, 0, 0, 0, 1, 1, 1, 1, 0],  # Row 7
            [1, 1, 1, 1, 0, 0, 0, 0, 0, 0],  # Row 8
            [3, 0, 0, 0, 0, 1, 1, 1, 0, 3],  # Row 9: Exits at (9,0) and (9,9)
        ]
        return maze

    def _find_start(self):
        """Find the starting position in the maze."""
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == START:
                    return (r, c)
        raise ValueError("No start position found in maze!")

    def _find_exits(self):
        """Find all exit positions in the maze."""
        exits = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == EXIT:
                    exits.append((r, c))
        if not exits:
            raise ValueError("No exits found in maze!")
        return exits

    def is_valid_position(self, row, col):
        """
        Check if a position is valid (within bounds and not a wall).

        Args:
            row: Row index
            col: Column index

        Returns:
            bool: True if agent can be at this position
        """
        # Check bounds
        if row < 0 or row >= self.rows:
            return False
        if col < 0 or col >= self.cols:
            return False
        # Check if not a wall
        return self.grid[row][col] != WALL

    def is_exit(self, row, col):
        """Check if position is an exit."""
        return (row, col) in self.exits

    def get_neighbors(self, row, col):
        """
        Get all valid neighboring positions (for movement).

        Actions: Up, Down, Left, Right

        Args:
            row, col: Current position

        Returns:
            list: List of (row, col) tuples for valid moves
        """
        # Define movement directions: (delta_row, delta_col)
        directions = [
            (-1, 0),  # Up
            (1, 0),   # Down
            (0, -1),  # Left
            (0, 1),   # Right
        ]

        neighbors = []
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc

            if self.is_valid_position(new_row, new_col):
                neighbors.append((new_row, new_col))

        return neighbors

    def display(self, agent_pos=None, enemy_pos=None, path=None):
        """
        Display the maze in terminal.

        Args:
            agent_pos: (row, col) of agent, shown as 'A'
            enemy_pos: (row, col) of enemy, shown as 'X'
            path: List of positions to highlight with '.'
        """
        # Symbols for display
        symbols = {
            EMPTY: '·',   # Empty cell
            WALL: '█',    # Wall
            START: 'S',   # Start
            EXIT: 'E',    # Exit
        }

        print("\n" + "─" * (self.cols * 2 + 1))

        for r in range(self.rows):
            row_str = "│"
            for c in range(self.cols):
                # Priority: Agent > Enemy > Path > Cell type
                if agent_pos and (r, c) == agent_pos:
                    row_str += "A "
                elif enemy_pos and (r, c) == enemy_pos:
                    row_str += "X "
                elif path and (r, c) in path:
                    row_str += "* "
                else:
                    row_str += symbols[self.grid[r][c]] + " "
            print(row_str + "│")

        print("─" * (self.cols * 2 + 1))
        print(f"Legend: S=Start, E=Exit, █=Wall, ·=Empty, A=Agent, X=Enemy, *=Path\n")


# =============================================================================
# RANDOM MAZE GENERATION
# =============================================================================

def generate_random_maze(rows=10, cols=10, num_exits=3, seed=None):
    """
    Generate a random solvable maze using recursive backtracking.

    Args:
        rows: Number of rows
        cols: Number of columns
        num_exits: Number of exits to place
        seed: Random seed for reproducibility (None for random)

    Returns:
        Maze object with randomly generated grid
    """
    if seed is not None:
        random.seed(seed)

    # Initialize grid with all walls
    grid = [[WALL for _ in range(cols)] for _ in range(rows)]

    # Use recursive backtracking to carve passages
    def carve(r, c):
        grid[r][c] = EMPTY
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        random.shuffle(directions)

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == WALL:
                # Carve passage between cells
                grid[r + dr // 2][c + dc // 2] = EMPTY
                carve(nr, nc)

    # Start carving from (0, 0)
    carve(0, 0)

    # Add some random passages to make it less maze-like and more open
    for _ in range(int(rows * cols * 0.15)):
        r = random.randint(1, rows - 2)
        c = random.randint(1, cols - 2)
        if grid[r][c] == WALL:
            # Check if opening this wall connects passages
            neighbors = sum(1 for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                           if 0 <= r + dr < rows and 0 <= c + dc < cols
                           and grid[r + dr][c + dc] == EMPTY)
            if neighbors >= 2:
                grid[r][c] = EMPTY

    # Place start at top-left corner
    grid[0][0] = START

    # Candidate exit positions (corners and edges)
    candidates = [
        (0, cols - 1),           # Top-right
        (rows - 1, 0),           # Bottom-left
        (rows - 1, cols - 1),    # Bottom-right
        (rows // 2, cols - 1),   # Middle-right
        (rows - 1, cols // 2),   # Bottom-middle
    ]

    # Ensure exit positions are reachable (clear walls if needed)
    for pos in candidates:
        r, c = pos
        if grid[r][c] == WALL:
            grid[r][c] = EMPTY
            # Also clear adjacent cell if it's a wall
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == WALL:
                    grid[nr][nc] = EMPTY
                    break

    # Place exits
    random.shuffle(candidates)
    for i in range(min(num_exits, len(candidates))):
        r, c = candidates[i]
        grid[r][c] = EXIT

    # Create maze and verify solvability
    maze = Maze(grid)

    def is_solvable(m):
        """Check if maze has path from start to any exit."""
        visited = set()
        queue = deque([m.start])
        visited.add(m.start)

        while queue:
            pos = queue.popleft()
            if pos in m.exits:
                return True
            for neighbor in m.get_neighbors(*pos):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return False

    # If not solvable, clear more walls until it is
    attempts = 0
    while not is_solvable(maze) and attempts < 20:
        # Clear random walls
        for _ in range(5):
            r = random.randint(1, rows - 2)
            c = random.randint(1, cols - 2)
            if grid[r][c] == WALL:
                grid[r][c] = EMPTY
        maze = Maze(grid)
        attempts += 1

    return maze


# =============================================================================
# TEST CODE
# =============================================================================

if __name__ == "__main__":
    print("Creating default maze...")
    maze = Maze()

    print(f"Maze size: {maze.rows} x {maze.cols}")
    print(f"Start position: {maze.start}")
    print(f"Exit positions: {maze.exits}")

    maze.display()

    # Test neighbor finding
    print(f"Neighbors of start {maze.start}: {maze.get_neighbors(*maze.start)}")

    # Test random maze generation
    print("\n" + "=" * 50)
    print("Testing random maze generation...")
    print("=" * 50)

    for i in range(3):
        random_maze = generate_random_maze(rows=10, cols=10, num_exits=3)
        print(f"\nRandom Maze {i+1}:")
        print(f"Start: {random_maze.start}")
        print(f"Exits: {random_maze.exits}")
        random_maze.display()
