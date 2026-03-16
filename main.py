"""
Maze Solver - Main Entry Point
==============================
A visual maze solver demonstrating BFS, DFS, A*, and Ant Colony Optimization (ACO).

Controls:
    1/2/3/4       - Run BFS/DFS/A*/ACO (fast)
    Shift+1/2/3/4 - Run BFS/DFS/A*/ACO step-by-step
    C - Compare all algorithms
    N - Generate new random maze
    W - Toggle walls on/off
    R - Reset
    Q - Quit

Step-by-step controls:
    SPACE - Next step
    F - Fast forward
    S - Slow auto-play

Usage:
    python main.py
"""

import time
from maze import Maze, generate_random_maze
from algorithms import bfs, dfs, astar, aco
from algorithms_visual import bfs_visual, dfs_visual, astar_visual, aco_visual
from visualizer import MazeVisualizer


class MazeSolverGame:
    """
    Main game controller that orchestrates maze solving visualization.
    """

    def __init__(self):
        """Initialize the game with maze and visualizer."""
        # Create maze environment
        self.maze = Maze()

        # Create visualizer
        self.visualizer = MazeVisualizer(self.maze, "Maze Solver - Algorithm Comparison")

        # Algorithm mapping
        self.algorithms = {
            '1': ('BFS', bfs),
            '2': ('DFS', dfs),
            '3': ('A*', astar),
            '4': ('ACO', aco),
        }

        # Visual (step-by-step) algorithms
        self.visual_algorithms = {
            '1': ('BFS', bfs_visual),
            '2': ('DFS', dfs_visual),
            '3': ('A*', astar_visual),
            '4': ('ACO', aco_visual),
        }

        # Current state
        self.running = True

    def run_algorithm(self, algo_key, animate_exploration=True):
        """
        Run a single algorithm and visualize the result.

        Args:
            algo_key: '1' for BFS, '2' for DFS, '3' for A*, '4' for ACO
            animate_exploration: Whether to animate the exploration process
        """
        if algo_key not in self.algorithms:
            return

        name, algorithm = self.algorithms[algo_key]

        # Update status
        self.visualizer.stats['algorithm'] = name
        self.visualizer.stats['status'] = 'Searching...'
        self.visualizer.update()

        # Get optimal path length from BFS (for comparison)
        # BFS is used as the shortest-path reference for all other algorithms
        if name != 'BFS':
            bfs_result = bfs(self.maze)
            if bfs_result.success:
                self.visualizer.stats['optimal_length'] = len(bfs_result.path) - 1
            else:
                self.visualizer.stats['optimal_length'] = None
        else:
            self.visualizer.stats['optimal_length'] = None  # BFS is always optimal

        # Run the algorithm with timing
        start_time = time.perf_counter()
        result = algorithm(self.maze)
        end_time = time.perf_counter()

        elapsed_ms = (end_time - start_time) * 1000

        # If BFS, set optimal length to its own result
        if name == 'BFS' and result.success:
            self.visualizer.stats['optimal_length'] = len(result.path) - 1

        # Animate exploration if enabled
        # For ACO, explored may be larger/noisier, so keep the same cap
        if animate_exploration and result.explored and len(result.explored) <= 100:
            self.visualizer.stats['status'] = 'Exploring...'
            self.visualizer.animate_exploration(result.explored, delay=0.01)

        # Update visualizer with results
        self.visualizer.set_explored(result.explored)
        self.visualizer.stats['nodes_explored'] = result.nodes_expanded

        if result.success:
            path_len = len(result.path) - 1
            self.visualizer.stats['status'] = f'Found! ({elapsed_ms:.1f}ms)'
            self.visualizer.set_path(result.path)
            self.visualizer.update()

            # Adjust animation speed based on path length
            if path_len <= 20:
                # Normal animation for short paths
                self.visualizer.stats['status'] = 'Drawing path...'
                self.visualizer.animate_path_drawing(result.path, delay=0.03)
                self.visualizer.update()
                time.sleep(0.3)
                self.visualizer.stats['status'] = 'Running solution...'
                self.animate_solution(result.path, step_delay=0.12)
            elif path_len <= 50:
                # Faster animation for medium paths
                self.visualizer.stats['status'] = f'Running solution ({path_len} steps)...'
                self.animate_solution(result.path, step_delay=0.05)
            else:
                # Very long path - show quick preview only
                self.visualizer.stats['status'] = (
                    f'Path found: {path_len} steps (too long for full animation)'
                )
                self.visualizer.update()
                time.sleep(1)
                # Quick animation - just show key points
                step = max(1, path_len // 15)
                quick_path = result.path[::step]
                if not quick_path or quick_path[-1] != result.path[-1]:
                    quick_path.append(result.path[-1])
                self.animate_solution(quick_path, step_delay=0.08)
        else:
            self.visualizer.stats['status'] = 'No path found!'
            self.visualizer.stats['path_length'] = 0

        self.visualizer.update()

    def animate_solution(self, path, step_delay=0.12):
        """
        Animate agent moving along the solution path.

        Args:
            path: List of (row, col) positions
            step_delay: Seconds between each step
        """
        for pos in path:
            # Check for quit/reset events
            event = self.visualizer.handle_events()
            if event == 'q':
                self.running = False
                return
            elif event == 'r':
                self.reset()
                return

            # Update agent position
            self.visualizer.set_agent_position(pos)
            self.visualizer.update()
            time.sleep(step_delay)

        # Final status - pulse the exit
        self.visualizer.stats['status'] = 'Complete!'
        if path:
            final_pos = path[-1]
            self.visualizer.pulse_cell(final_pos[0], final_pos[1], (255, 215, 0))
        self.visualizer.update()

    def reset(self):
        """Reset the game state."""
        self.visualizer.reset()
        self.visualizer.update()

    def generate_new_maze(self):
        """Generate a new random maze."""
        self.visualizer.stats['status'] = 'Generating new maze...'
        self.visualizer.update()

        # Generate new maze
        self.maze = generate_random_maze(rows=10, cols=10, num_exits=3)

        # Recreate visualizer with new maze
        self.visualizer.close()
        self.visualizer = MazeVisualizer(self.maze, "Maze Solver - Algorithm Comparison")

        # Reset state
        self.reset()
        self.visualizer.stats['status'] = 'New maze generated! (Press 1/2/3/4 to solve)'

        print(f"\nNew maze generated!")
        print(f"Start: {self.maze.start}")
        print(f"Exits: {self.maze.exits}")

        self.visualizer.update()

    def run_visual_algorithm(self, algo_key, step_delay=0.3):
        """
        Run algorithm with step-by-step visualization.

        Shows each step: what's popped, what's pushed, queue/stack state,
        or iteration progress for ACO.

        Args:
            algo_key: '1' for BFS, '2' for DFS, '3' for A*, '4' for ACO
            step_delay: Seconds between each step (can be adjusted)
        """
        if algo_key not in self.visual_algorithms:
            return

        name, visual_algo = self.visual_algorithms[algo_key]

        self.reset()
        self.visualizer.stats['algorithm'] = f'{name} (Step-by-Step)'
        self.visualizer.stats['status'] = 'Press SPACE to step, F for fast, R to reset'
        self.visualizer.update()

        print(f"\n{'=' * 60}")
        print(f"STEP-BY-STEP: {name}")
        print(f"{'=' * 60}")
        print("Controls: SPACE=next step, F=fast forward, S=slow auto, R=reset, Q=quit")
        print("-" * 60)

        # Get the generator
        algo_generator = visual_algo(self.maze)

        auto_mode = False
        current_delay = step_delay

        for step in algo_generator:
            # Update visualizer with current step
            self.visualizer.set_algorithm_step(step)
            self.visualizer.set_agent_position(step.current_pos)

            self.visualizer.stats['status'] = f'Step {step.step_num}: {step.action.upper()}'
            self.visualizer.update()

            # Print to console
            print(f"Step {step.step_num}: {step.message}")

            # Keep explored/path synced if available in the step object
            if hasattr(step, 'explored'):
                self.visualizer.set_explored(step.explored)
            if hasattr(step, 'path_so_far') and step.path_so_far:
                self.visualizer.set_path(step.path_so_far)

            # Check if goal found
            if step.is_goal:
                self.visualizer.stats['status'] = f'GOAL FOUND! Path: {len(step.path_so_far) - 1} steps'
                self.visualizer.set_path(step.path_so_far)
                self.visualizer.update()

                print(f"\n*** GOAL REACHED! ***")
                print(f"Final path length: {len(step.path_so_far) - 1} steps")
                print(f"Total nodes explored: {len(step.explored)}")
                time.sleep(1)

                # Animate the final path
                self.visualizer.algo_step = None  # Clear step display
                self.visualizer.stats['status'] = 'Animating solution...'
                self.animate_solution(step.path_so_far, step_delay=0.1)
                return

            if step.action == 'fail':
                self.visualizer.stats['status'] = 'NO PATH FOUND!'
                self.visualizer.update()
                print("\n*** NO PATH EXISTS ***")
                time.sleep(2)
                return

            # Wait for user input or auto-advance
            if auto_mode:
                time.sleep(current_delay)

                # Check for events during auto mode
                event = self.visualizer.handle_events()
                if event == 'q':
                    self.running = False
                    return
                elif event == 'r':
                    self.reset()
                    return
                elif event == ' ':  # Space to pause
                    auto_mode = False
            else:
                # Wait for keypress
                waiting = True
                while waiting:
                    event = self.visualizer.handle_events()
                    if event == 'q':
                        self.running = False
                        return
                    elif event == 'r':
                        self.reset()
                        return
                    elif event == ' ':  # Space - next step
                        waiting = False
                    elif event == 'f':  # F - fast forward (auto mode)
                        auto_mode = True
                        current_delay = 0.1
                        waiting = False
                    elif event == 's':  # S - slow mode
                        auto_mode = True
                        current_delay = 0.5
                        waiting = False

                    self.visualizer.update()
                    time.sleep(0.05)

        # Clear step display at the end
        self.visualizer.algo_step = None
        self.visualizer.update()

    def run(self):
        """Main game loop."""
        print("=" * 60)
        print("MAZE SOLVER - Algorithm Comparison & Visualization")
        print("=" * 60)
        print(f"\nMaze: {self.maze.rows}x{self.maze.cols}")
        print(f"Start: {self.maze.start}")
        print(f"Exits: {self.maze.exits}")
        print("\nControls:")
        print("  1/2/3/4       - Run BFS/DFS/A*/ACO (fast)")
        print("  Shift+1/2/3/4 - Run BFS/DFS/A*/ACO STEP-BY-STEP")
        print("  C - Compare all algorithms")
        print("  N - Generate new random maze")
        print("  W - Toggle walls on/off")
        print("  R - Reset")
        print("  Q - Quit")
        print("\nStep-by-step controls:")
        print("  SPACE - Next step")
        print("  F - Fast forward")
        print("  S - Slow auto-play")
        print("-" * 60)

        self.visualizer.update()

        while self.running:
            event = self.visualizer.handle_events()

            if event == 'q':
                self.running = False

            elif event == 'r':
                self.reset()

            elif event in ('1', '2', '3', '4'):
                self.reset()
                self.run_algorithm(event)

            elif event in ('!', '@', '#', '$'):  # Shift + 1/2/3/4
                key_map = {'!': '1', '@': '2', '#': '3', '$': '4'}
                self.run_visual_algorithm(key_map[event])

            elif event == 'c':
                self.run_comparison()

            elif event == 'n':
                self.generate_new_maze()

            elif event == 'w':
                status = self.visualizer.toggle_walls()
                self.reset()
                self.visualizer.stats['status'] = status
                self.visualizer.update()

            # Keep updating display
            self.visualizer.update()

        self.visualizer.close()
        print("\nGoodbye!")

    def run_comparison(self):
        """
        Run all algorithms and display comparison results visually.
        """
        self.reset()
        self.visualizer.stats['algorithm'] = 'Comparing...'
        self.visualizer.stats['status'] = 'Running all algorithms...'
        self.visualizer.update()

        results = {}
        all_paths = {}
        raw_results = {}

        # First pass: run all algorithms and collect raw results
        for key, (name, algorithm) in self.algorithms.items():
            self.visualizer.stats['status'] = f'Running {name}...'
            self.visualizer.update()

            start_time = time.perf_counter()
            result = algorithm(self.maze)
            elapsed = (time.perf_counter() - start_time) * 1000

            raw_results[name] = {
                'result': result,
                'time_ms': elapsed,
            }
            all_paths[name] = result.path if result.success else []

            time.sleep(0.15)  # Brief pause for visual feedback

        # Find optimal path length (BFS guarantees shortest path)
        optimal_length = None
        if raw_results['BFS']['result'].success:
            optimal_length = len(raw_results['BFS']['result'].path) - 1

        # Second pass: calculate rewards with optimal reference
        for name, data in raw_results.items():
            result = data['result']
            reward = self.calculate_reward(result, optimal_length)

            results[name] = {
                'success': result.success,
                'path_length': len(result.path) - 1 if result.path else 0,
                'nodes_expanded': result.nodes_expanded,
                'time_ms': data['time_ms'],
                'reward': reward,
            }

        # Set comparison results for visualization
        self.visualizer.set_comparison_results(results)
        self.visualizer.stats['algorithm'] = 'All'
        self.visualizer.stats['status'] = 'Comparison complete!'
        self.visualizer.update()

        # Print to console too
        print("\n" + "=" * 82)
        print("ALGORITHM COMPARISON RESULTS")
        print("=" * 82)
        print(f"{'Algorithm':<10} {'Success':<10} {'Path':<8} {'Nodes':<8} {'Time (ms)':<12} {'Reward':<8}")
        print("-" * 82)

        display_order = ['BFS', 'DFS', 'A*', 'ACO']
        for name in display_order:
            data = results.get(name)
            if not data:
                continue
            print(
                f"{name:<10} {str(data['success']):<10} {data['path_length']:<8} "
                f"{data['nodes_expanded']:<8} {data['time_ms']:<12.2f} {data['reward']:<8.0f}"
            )

        print("=" * 82)

        # Animate each algorithm's path sequentially
        algo_colors = {
            'BFS': (100, 180, 255),
            'DFS': (255, 180, 100),
            'A*': (100, 255, 150),
            'ACO': (220, 120, 255),
        }

        for algo_name in display_order:
            path = all_paths.get(algo_name, [])
            if not path:
                continue

            # Skip very long animations
            if len(path) > 30:
                self.visualizer.stats['status'] = f'{algo_name}: {len(path) - 1} steps (skipping animation)'
                self.visualizer.update()
                time.sleep(1)
                continue

            self.visualizer.stats['status'] = f'Showing {algo_name} path...'
            self.visualizer.set_path(path)
            self.visualizer.set_agent_position(self.maze.start)
            self.visualizer.update()
            time.sleep(0.3)

            # Animate agent along path
            for pos in path:
                event = self.visualizer.handle_events()
                if event in ('q', 'r'):
                    if event == 'q':
                        self.running = False
                    return

                self.visualizer.set_agent_position(pos)
                self.visualizer.update()
                time.sleep(0.08)

            time.sleep(0.5)

        # Final state
        self.visualizer.stats['status'] = 'Comparison complete! (Press R to reset)'
        self.visualizer.set_agent_position(self.maze.start)
        self.visualizer.update()

    def calculate_reward(self, result, optimal_path_length=None):
        """
        Calculate reward score for an algorithm result.

        Reward Components:
        1. SUCCESS_BONUS: +100 for finding any path
        2. PATH_EFFICIENCY: Up to +100 for optimal/near-optimal path
        3. EXPLORATION_EFFICIENCY: Up to +50 for minimal node expansion

        Args:
            result: SearchResult object
            optimal_path_length: Known optimal length (for comparison)

        Returns:
            float: Reward score (0-250 range)
        """
        if not result.success:
            return 0

        path_len = len(result.path) - 1
        nodes = result.nodes_expanded

        # 1. Base reward for success
        reward = 100

        # 2. Path efficiency bonus (0-100 points)
        # Optimal path gets 100, longer paths get less
        if optimal_path_length is not None:
            optimal = optimal_path_length
        else:
            optimal = 10  # fallback estimate

        if path_len <= optimal:
            path_bonus = 100
        else:
            # Lose 10 points per extra step
            path_bonus = max(0, 100 - (path_len - optimal) * 10)
        reward += path_bonus

        # 3. Exploration efficiency (0-50 points)
        # Fewer nodes = higher efficiency
        if nodes <= 30:
            explore_bonus = 50
        elif nodes <= 50:
            explore_bonus = 40
        elif nodes <= 100:
            explore_bonus = 25
        elif nodes <= 150:
            explore_bonus = 10
        else:
            explore_bonus = 0
        reward += explore_bonus

        return reward


def main():
    """Entry point."""
    game = MazeSolverGame()
    game.run()


if __name__ == "__main__":
    main()
