
# Maze Solver

A visual maze solver demonstrating BFS, DFS, and A* search algorithms with step-by-step animation.

## Demo

https://github.com/user-attachments/assets/3afea3b6-720d-431e-bb30-273b0c20b4b0

## Features

- **Three algorithms**: BFS (Queue), DFS (Stack), A* (Priority Queue)
- **Step-by-step visualization**: Watch the algorithm explore the maze
- **Algorithm comparison**: See path length, nodes explored, time, and reward metrics
- **Random maze generation**: Generate new mazes on the fly
- **Multi-exit support**qqc: Mazes can have multiple exits
- **Wall toggle**: Remove/restore walls to see how algorithms behave

## Setup
clear

```bashcd path/to/your/maze-solver

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install pygame-ce
```

## Running

```bash
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| `1` | Run BFS (step-by-step) |
| `2` | Run DFS (step-by-step) |
| `3` | Run A* (step-by-step) |
| `C` | Compare all algorithms |
| `N` | Generate new random maze |
| `W` | Toggle walls on/off |
| `R` | Reset maze |
| `Q` | Quit |

## Algorithms

- **BFS**: Uses a queue (FIFO). Guarantees shortest path.
- **DFS**: Uses a stack (LIFO). Does NOT guarantee shortest path.
- **A***: Uses a priority queue ordered by f = g + h. Optimal and efficient.

## Project Structure

```
├── main.py              # Entry point
├── maze.py              # Maze grid and generation
├── algorithms.py        # BFS, DFS, A* implementations
├── algorithms_visual.py # Step-by-step versions for animation
└── visualizer.py        # Pygame visualization
```

## Tech Stack

**Python** • **Pygame-ce** • **Queue** • **Stack** • **Priority Queue**

