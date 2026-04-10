# Maze Solver

A visual maze solver demonstrating **BFS, DFS, A\***, and **Ant Colony Optimization (ACO)** with step-by-step animation and algorithm comparison.

## Demo

https://github.com/user-attachments/assets/62e38997-8fd3-4a8a-8e73-6a390c8cfa8c

## Features

- **Four algorithms**
  - **BFS** (Queue)
  - **DFS** (Stack)
  - **A\*** (Priority Queue)
  - **ACO** (Ant Colony Optimization)
- **Step-by-step visualization**  
  Watch each algorithm explore the maze in real time.
- **Algorithm comparison**  
  Compare path length, nodes explored, execution time, and reward/performance metrics.
- **Random maze generation**  
  Generate new mazes on the fly.
- **Multi-exit support**  
  Mazes can have multiple exits.
- **Wall toggle**  
  Remove or restore walls to observe how each algorithm behaves differently.

## Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install pygame-ce
or
python -m pip install -U pygame-ce

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
| `4` | Run ACO (step-by-step) |
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



