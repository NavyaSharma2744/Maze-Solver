"""
Pygame Visualizer Module
========================
This module provides a graphical interface for the maze using pygame.

Key Features:
- Colorful grid display
- Animation support for path visualization
- Enemy movement animation
"""

import pygame
import time
import math

# Colors (RGB)
COLORS = {
    'background': (30, 30, 40),      # Dark background
    'empty': (60, 60, 80),           # Empty cells
    'wall': (20, 20, 30),            # Walls
    'start': (50, 205, 50),          # Green for start
    'exit': (255, 215, 0),           # Gold for exits
    'agent': (0, 150, 255),          # Blue for agent
    'enemy': (255, 60, 60),          # Red for enemy
    'path': (100, 200, 100),         # Light green for path
    'explored': (80, 80, 120),       # Explored cells
    'exploring': (150, 100, 200),    # Currently exploring (purple)
    'frontier': (255, 200, 100),     # Orange for frontier/queue cells
    'current': (255, 100, 255),      # Magenta for current cell
    'grid_line': (40, 40, 55),       # Grid lines
    'text': (255, 255, 255),         # White text
    'bfs_path': (100, 180, 255),     # Light blue for BFS
    'dfs_path': (255, 180, 100),     # Orange for DFS
    'astar_path': (100, 255, 150),   # Light green for A*
}

# Cell size in pixels
CELL_SIZE = 60
MARGIN = 2  # Gap between cells


class MazeVisualizer:
    """
    Pygame-based visualizer for the maze.

    Creates a window showing:
    - The maze grid with walls and paths
    - Start (green) and Exit (gold) positions
    - Agent (blue circle) and Enemy (red circle)
    - Path visualization during algorithm execution
    """

    def __init__(self, maze, title="Maze Solver"):
        """
        Initialize the visualizer.

        Args:
            maze: Maze object to visualize
            title: Window title
        """
        # Initialize pygame
        pygame.init()
        pygame.font.init()

        self.maze = maze

        # Calculate window size
        self.width = maze.cols * CELL_SIZE + 220  # Extra space for info panel
        self.height = maze.rows * CELL_SIZE + 210  # Extra space for title and comparison panel

        # Create window
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(title)

        # Fonts for text
        self.title_font = pygame.font.SysFont('arial', 28)
        self.info_font = pygame.font.SysFont('arial', 18)
        self.small_font = pygame.font.SysFont('arial', 14)

        # Animation state
        self.agent_pos = maze.start
        self.enemy_pos = None
        self.path = []
        self.explored = set()

        # Stats
        self.stats = {
            'algorithm': 'None',
            'path_length': 0,
            'nodes_explored': 0,
            'status': 'Ready',
            'optimal_length': None,  # For showing path quality
        }

        # Comparison results (for comparison mode)
        self.comparison_results = None

        # Algorithm visualization state
        self.algo_step = None  # Current AlgorithmStep object
        self.frontier_cells = []  # Cells in queue/stack
        self.current_cell = None  # Cell being processed

        # Wall toggle - store original grid
        self.original_grid = [row[:] for row in maze.grid]
        self.walls_removed = False

        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()

    def get_cell_rect(self, row, col):
        """Get the pygame Rect for a cell at (row, col)."""
        x = col * CELL_SIZE + MARGIN
        y = row * CELL_SIZE + 50 + MARGIN  # 50px offset for title
        return pygame.Rect(x, y, CELL_SIZE - 2*MARGIN, CELL_SIZE - 2*MARGIN)

    def draw_cell(self, row, col, color, border_radius=5):
        """Draw a single cell with rounded corners."""
        rect = self.get_cell_rect(row, col)
        pygame.draw.rect(self.screen, color, rect, border_radius=border_radius)

    def draw_circle_in_cell(self, row, col, color, radius_ratio=0.35):
        """Draw a circle centered in a cell."""
        rect = self.get_cell_rect(row, col)
        center = rect.center
        radius = int(CELL_SIZE * radius_ratio)
        pygame.draw.circle(self.screen, color, center, radius)
        # Add a slight highlight
        highlight_pos = (center[0] - radius//3, center[1] - radius//3)
        pygame.draw.circle(self.screen, (255, 255, 255), highlight_pos, radius//4)

    def draw_maze(self):
        """Draw the entire maze grid."""
        from maze import WALL, START, EXIT

        for row in range(self.maze.rows):
            for col in range(self.maze.cols):
                cell_type = self.maze.grid[row][col]
                pos = (row, col)

                # Determine cell color (priority: current > frontier > explored > type)
                if self.current_cell and pos == self.current_cell:
                    color = COLORS['current']  # Magenta - currently processing
                elif pos in self.frontier_cells:
                    color = COLORS['frontier']  # Orange - in queue/stack
                elif cell_type == WALL:
                    color = COLORS['wall']
                elif cell_type == START:
                    color = COLORS['start']
                elif cell_type == EXIT:
                    color = COLORS['exit']
                elif pos in self.explored:
                    color = COLORS['explored']
                else:
                    color = COLORS['empty']

                # Draw the cell
                self.draw_cell(row, col, color)

                # Add labels for start and exits
                if cell_type == START:
                    self._draw_cell_label(row, col, "S")
                elif cell_type == EXIT:
                    self._draw_cell_label(row, col, "E")

                # Add frontier indicator
                if pos in self.frontier_cells and cell_type not in (START, EXIT):
                    self._draw_cell_label(row, col, "?")

    def _draw_cell_label(self, row, col, text):
        """Draw a small label in the corner of a cell."""
        rect = self.get_cell_rect(row, col)
        label = self.small_font.render(text, True, (0, 0, 0))
        label_rect = label.get_rect(topleft=(rect.left + 5, rect.top + 5))
        self.screen.blit(label, label_rect)

    def draw_path(self):
        """Draw the solution path."""
        for pos in self.path:
            if pos != self.maze.start and pos not in self.maze.exits:
                self.draw_cell(pos[0], pos[1], COLORS['path'])

    def draw_agent(self):
        """Draw the agent at its current position."""
        if self.agent_pos:
            self.draw_circle_in_cell(self.agent_pos[0], self.agent_pos[1],
                                     COLORS['agent'])

    def draw_enemy(self):
        """Draw the enemy at its current position."""
        if self.enemy_pos:
            self.draw_circle_in_cell(self.enemy_pos[0], self.enemy_pos[1],
                                     COLORS['enemy'], radius_ratio=0.3)

    def draw_title(self):
        """Draw the title at the top."""
        title = self.title_font.render("Maze Solver - Search Algorithms", True, COLORS['text'])
        title_rect = title.get_rect(midtop=(self.maze.cols * CELL_SIZE // 2, 10))
        self.screen.blit(title, title_rect)

    def draw_info_panel(self):
        """Draw the information panel on the right side."""
        # Panel position
        panel_x = self.maze.cols * CELL_SIZE + 20
        panel_y = 60

        # Draw panel background
        panel_rect = pygame.Rect(panel_x - 10, panel_y - 10, 180, 300)
        pygame.draw.rect(self.screen, (40, 40, 55), panel_rect, border_radius=10)

        # Draw stats
        # Build path length display with quality indicator
        path_display = f"Path Length: {self.stats['path_length']}"
        if self.stats.get('optimal_length') and self.stats['path_length'] > 0:
            opt = self.stats['optimal_length']
            if self.stats['path_length'] == opt:
                path_display += " (Optimal)"
            else:
                diff = self.stats['path_length'] - opt
                path_display += f" (+{diff})"

        lines = [
            f"Algorithm: {self.stats['algorithm']}",
            f"Status: {self.stats['status']}",
            "",
            path_display,
            f"Nodes Explored: {self.stats['nodes_explored']}",
            "",
            "Controls:",
            "  1/2/3 - BFS/DFS/A*",
            "  Shift+1/2/3 - Step Mode",
            "  C - Compare | N - New",
            "  W - Walls | R - Reset",
        ]

        for i, line in enumerate(lines):
            text = self.info_font.render(line, True, COLORS['text'])
            self.screen.blit(text, (panel_x, panel_y + i * 25))

        # Legend
        legend_y = panel_y + len(lines) * 25 + 20
        self._draw_legend(panel_x, legend_y)

    def _draw_legend(self, x, y):
        """Draw a color legend."""
        legend_items = [
            (COLORS['start'], "Start"),
            (COLORS['exit'], "Exit"),
            (COLORS['agent'], "Agent"),
            (COLORS['path'], "Path"),
        ]

        for i, (color, label) in enumerate(legend_items):
            # Draw color square
            rect = pygame.Rect(x, y + i * 22, 15, 15)
            pygame.draw.rect(self.screen, color, rect, border_radius=3)
            # Draw label
            text = self.small_font.render(label, True, COLORS['text'])
            self.screen.blit(text, (x + 22, y + i * 22))

    def set_comparison_results(self, results):
        """
        Set comparison results for display.

        Args:
            results: Dict with algorithm names as keys, containing:
                - success: bool
                - path_length: int
                - nodes_expanded: int
                - time_ms: float
                - reward: float (optional)
        """
        self.comparison_results = results

    def set_algorithm_step(self, step):
        """
        Set the current algorithm visualization step.

        Args:
            step: AlgorithmStep object from algorithms_visual.py
        """
        self.algo_step = step
        if step:
            self.current_cell = step.current_pos
            self.frontier_cells = step.frontier if step.frontier else []
            self.explored = step.explored if step.explored else set()
            self.path = step.path_so_far if step.path_so_far else []
            self.stats['nodes_explored'] = len(self.explored)
            self.stats['path_length'] = len(self.path) - 1 if self.path else 0
        else:
            self.current_cell = None
            self.frontier_cells = []

    def draw_algorithm_state(self):
        """Draw the algorithm state panel showing queue/stack contents."""
        if not self.algo_step:
            return

        step = self.algo_step

        # Panel position - below the maze
        panel_x = 20
        panel_y = self.maze.rows * CELL_SIZE + 55

        # Panel dimensions
        panel_width = self.maze.cols * CELL_SIZE - 20
        panel_height = 140

        # Draw panel background
        panel_rect = pygame.Rect(panel_x - 10, panel_y - 5, panel_width, panel_height)
        pygame.draw.rect(self.screen, (35, 35, 50), panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, (80, 80, 120), panel_rect, width=2, border_radius=8)

        # Get algorithm-specific info
        algo = self.stats.get('algorithm', 'BFS')
        if 'BFS' in algo:
            data_struct = 'QUEUE'
            struct_color = (100, 180, 255)
            pop_side = 'FRONT'
            push_side = 'BACK'
        elif 'DFS' in algo:
            data_struct = 'STACK'
            struct_color = (255, 180, 100)
            pop_side = 'TOP'
            push_side = 'TOP'
        else:  # A*
            data_struct = 'PRIORITY QUEUE'
            struct_color = (100, 255, 150)
            pop_side = 'MIN f(n)'
            push_side = 'BY f(n)'

        # Title with step number
        title = f"Step {step.step_num}: {algo} using {data_struct}"
        title_surface = self.info_font.render(title, True, struct_color)
        self.screen.blit(title_surface, (panel_x, panel_y))

        # Action message
        action_colors = {
            'start': (100, 255, 100),
            'pop': (255, 200, 100),
            'push': (100, 200, 255),
            'goal': (255, 215, 0),
            'fail': (255, 100, 100),
        }
        action_color = action_colors.get(step.action, COLORS['text'])
        msg_surface = self.small_font.render(step.message, True, action_color)
        self.screen.blit(msg_surface, (panel_x, panel_y + 25))

        # Current position
        curr_text = f"Current: {step.current_pos}" if step.current_pos else "Current: None"
        curr_surface = self.small_font.render(curr_text, True, COLORS['current'])
        self.screen.blit(curr_surface, (panel_x, panel_y + 45))

        # Data structure visualization
        ds_y = panel_y + 65
        ds_label = f"{data_struct} (pop from {pop_side}, push to {push_side}):"
        ds_surface = self.small_font.render(ds_label, True, (180, 180, 180))
        self.screen.blit(ds_surface, (panel_x, ds_y))

        # Draw queue/stack contents as boxes
        box_y = ds_y + 18
        box_size = 28
        box_margin = 3
        max_boxes = min(12, len(step.frontier) if step.frontier else 0)

        # Draw bracket
        if 'STACK' in data_struct:
            # Vertical stack representation
            bracket_text = "TOP→" if step.frontier else "[empty]"
        else:
            # Horizontal queue representation
            bracket_text = f"[{pop_side}→" if step.frontier else "[empty]"

        bracket_surface = self.small_font.render(bracket_text, True, struct_color)
        self.screen.blit(bracket_surface, (panel_x, box_y + 5))

        start_x = panel_x + 50

        for i in range(max_boxes):
            pos = step.frontier[i] if i < len(step.frontier) else None
            if pos:
                box_rect = pygame.Rect(start_x + i * (box_size + box_margin), box_y,
                                       box_size, box_size)
                # Color first box differently (next to be popped)
                if i == 0:
                    pygame.draw.rect(self.screen, COLORS['current'], box_rect, border_radius=4)
                else:
                    pygame.draw.rect(self.screen, struct_color, box_rect, border_radius=4)
                pygame.draw.rect(self.screen, (255, 255, 255), box_rect, width=1, border_radius=4)

                # Position text
                pos_text = f"{pos[0]},{pos[1]}"
                pos_surface = self.small_font.render(pos_text, True, (0, 0, 0))
                text_rect = pos_surface.get_rect(center=box_rect.center)
                self.screen.blit(pos_surface, text_rect)

        # Show remaining count if more items
        if step.frontier and len(step.frontier) > max_boxes:
            more_text = f"...+{len(step.frontier) - max_boxes} more"
            more_surface = self.small_font.render(more_text, True, (150, 150, 150))
            self.screen.blit(more_surface, (start_x + max_boxes * (box_size + box_margin) + 5, box_y + 5))

        # Statistics
        stats_y = box_y + box_size + 8
        stats_text = f"Explored: {len(step.explored)} | In {data_struct}: {len(step.frontier) if step.frontier else 0} | Path so far: {len(step.path_so_far)-1 if step.path_so_far else 0} steps"
        stats_surface = self.small_font.render(stats_text, True, (150, 150, 150))
        self.screen.blit(stats_surface, (panel_x, stats_y))

        # Legend
        legend_y = stats_y + 18
        legend_items = [
            (COLORS['current'], "Current"),
            (COLORS['frontier'], "In Queue/Stack"),
            (COLORS['explored'], "Explored"),
        ]
        legend_x = panel_x
        for color, label in legend_items:
            pygame.draw.rect(self.screen, color, (legend_x, legend_y, 12, 12), border_radius=2)
            label_surface = self.small_font.render(label, True, (150, 150, 150))
            self.screen.blit(label_surface, (legend_x + 16, legend_y - 2))
            legend_x += 100

    def draw_comparison_panel(self):
        """Draw comparison results as a detailed visual dashboard."""
        if not self.comparison_results:
            return

        # Panel position - below the maze
        panel_x = 20
        panel_y = self.maze.rows * CELL_SIZE + 55

        # Draw panel background
        panel_width = self.maze.cols * CELL_SIZE - 20
        panel_height = 130
        panel_rect = pygame.Rect(panel_x - 10, panel_y - 10, panel_width, panel_height)
        pygame.draw.rect(self.screen, (35, 35, 50), panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, (60, 60, 80), panel_rect, width=2, border_radius=8)

        # Draw panel title
        title = self.info_font.render("ALGORITHM COMPARISON", True, (255, 215, 0))
        title_rect = title.get_rect(midtop=(panel_x + panel_width // 2 - 10, panel_y - 5))
        self.screen.blit(title, title_rect)

        # Column headers with descriptions
        headers = [
            ("Algorithm", "Search method"),
            ("Path", "Steps to exit"),
            ("Nodes", "States explored"),
            ("Time", "Computation"),
            ("Score", "Performance"),
        ]
        col_widths = [85, 65, 70, 75, 65]
        header_y = panel_y + 25

        # Draw header background
        header_rect = pygame.Rect(panel_x - 5, header_y - 5, sum(col_widths) + 15, 24)
        pygame.draw.rect(self.screen, (50, 50, 70), header_rect, border_radius=4)

        # Draw headers
        x = panel_x
        for i, (header, _) in enumerate(headers):
            text = self.small_font.render(header, True, (180, 180, 200))
            self.screen.blit(text, (x, header_y))
            x += col_widths[i]

        # Algorithm colors and descriptions
        algo_info = {
            'BFS': {'color': (100, 180, 255), 'desc': 'Breadth-First'},
            'DFS': {'color': (255, 180, 100), 'desc': 'Depth-First'},
            'A*': {'color': (100, 255, 150), 'desc': 'Heuristic'},
        }

        # Find best values for highlighting
        successful = {k: v for k, v in self.comparison_results.items() if v['success']}
        if successful:
            best_path = min(v['path_length'] for v in successful.values())
            best_nodes = min(v['nodes_expanded'] for v in successful.values())
            best_time = min(v['time_ms'] for v in successful.values())
            best_reward = max(v.get('reward', 0) for v in successful.values())
        else:
            best_path = best_nodes = best_time = best_reward = 0

        # Draw data rows
        row_y = header_y + 28

        for algo_name in ['BFS', 'DFS', 'A*']:
            if algo_name not in self.comparison_results:
                continue

            data = self.comparison_results[algo_name]
            info = algo_info.get(algo_name, {'color': (150, 150, 150), 'desc': ''})

            # Row background
            row_rect = pygame.Rect(panel_x - 5, row_y - 3, sum(col_widths) + 15, 22)
            row_bg = (*info['color'][:3], 30)  # Semi-transparent
            s = pygame.Surface((row_rect.width, row_rect.height), pygame.SRCALPHA)
            s.fill(row_bg)
            self.screen.blit(s, row_rect.topleft)
            pygame.draw.rect(self.screen, (*info['color'][:3], 100), row_rect, width=1, border_radius=3)

            x = panel_x

            # Algorithm name with color indicator
            pygame.draw.circle(self.screen, info['color'], (x + 5, row_y + 7), 4)
            text = self.small_font.render(algo_name, True, info['color'])
            self.screen.blit(text, (x + 14, row_y))
            x += col_widths[0]

            if data['success']:
                # Path length (highlight if best with star)
                is_best_path = data['path_length'] == best_path
                path_color = (0, 255, 100) if is_best_path else COLORS['text']
                path_str = f"{data['path_length']}" + (" *" if is_best_path else "")
                text = self.small_font.render(path_str, True, path_color)
                self.screen.blit(text, (x, row_y))
                x += col_widths[1]

                # Nodes (highlight if best)
                is_best_nodes = data['nodes_expanded'] == best_nodes
                nodes_color = (0, 255, 100) if is_best_nodes else COLORS['text']
                nodes_str = f"{data['nodes_expanded']}" + (" *" if is_best_nodes else "")
                text = self.small_font.render(nodes_str, True, nodes_color)
                self.screen.blit(text, (x, row_y))
                x += col_widths[2]

                # Time (highlight if best)
                is_best_time = abs(data['time_ms'] - best_time) < 0.01
                time_color = (0, 255, 100) if is_best_time else COLORS['text']
                time_str = f"{data['time_ms']:.2f}ms" + (" *" if is_best_time else "")
                text = self.small_font.render(time_str, True, time_color)
                self.screen.blit(text, (x, row_y))
                x += col_widths[3]

                # Reward/Score (highlight if best)
                reward = data.get('reward', 0)
                is_best_reward = reward == best_reward and reward > 0
                reward_color = (0, 255, 100) if is_best_reward else COLORS['text']
                reward_str = f"{reward:.0f}" + (" *" if is_best_reward else "")
                text = self.small_font.render(reward_str, True, reward_color)
                self.screen.blit(text, (x, row_y))
            else:
                # Failed - show in red
                text = self.small_font.render("FAILED - No path found", True, (255, 80, 80))
                self.screen.blit(text, (x, row_y))

            row_y += 24

        # Draw winner banner
        if successful:
            row_y += 5
            # Find overall winner
            winner = max(successful.items(), key=lambda x: x[1].get('reward', 0))[0]
            winner_info = algo_info.get(winner, {'color': (255, 255, 255)})

            # Winner text with background
            winner_text = f"WINNER: {winner}"
            winner_surface = self.info_font.render(winner_text, True, winner_info['color'])

            # Draw trophy icon (simple)
            trophy_x = panel_x
            pygame.draw.polygon(self.screen, (255, 215, 0), [
                (trophy_x + 5, row_y + 2),
                (trophy_x + 15, row_y + 2),
                (trophy_x + 13, row_y + 10),
                (trophy_x + 7, row_y + 10),
            ])
            pygame.draw.rect(self.screen, (255, 215, 0), (trophy_x + 8, row_y + 10, 4, 4))

            self.screen.blit(winner_surface, (trophy_x + 22, row_y))

            # Show why it won
            reason = []
            winner_data = successful[winner]
            if winner_data['path_length'] == best_path:
                reason.append("shortest path")
            if winner_data['nodes_expanded'] == best_nodes:
                reason.append("most efficient")

            if reason:
                reason_text = f"({', '.join(reason)})"
                reason_surface = self.small_font.render(reason_text, True, (150, 150, 150))
                self.screen.blit(reason_surface, (trophy_x + 120, row_y + 3))

    def update(self):
        """Update the display."""
        # Clear screen
        self.screen.fill(COLORS['background'])

        # Draw all components
        self.draw_title()
        self.draw_maze()
        self.draw_path()
        self.draw_enemy()
        self.draw_agent()
        self.draw_info_panel()

        # Draw algorithm state panel if in step-by-step mode
        if self.algo_step:
            self.draw_algorithm_state()
        # Draw comparison panel if results available
        elif self.comparison_results:
            self.draw_comparison_panel()

        # Update display
        pygame.display.flip()

        # Cap frame rate
        self.clock.tick(60)

    def handle_events(self):
        """
        Handle pygame events.

        Returns:
            str or None: Key pressed ('1', '2', '3', 'r', 'q') or None
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'q'
            elif event.type == pygame.KEYDOWN:
                # Check for shift modifier
                mods = pygame.key.get_mods()
                shift_held = mods & pygame.KMOD_SHIFT

                if event.key == pygame.K_1:
                    return '!' if shift_held else '1'  # Shift+1 for visual mode
                elif event.key == pygame.K_2:
                    return '@' if shift_held else '2'  # Shift+2 for visual mode
                elif event.key == pygame.K_3:
                    return '#' if shift_held else '3'  # Shift+3 for visual mode
                elif event.key == pygame.K_r:
                    return 'r'
                elif event.key == pygame.K_q:
                    return 'q'
                elif event.key == pygame.K_c:
                    return 'c'
                elif event.key == pygame.K_n:
                    return 'n'
                elif event.key == pygame.K_v:
                    return 'v'
                elif event.key == pygame.K_w:
                    return 'w'
                elif event.key == pygame.K_SPACE:
                    return ' '
                elif event.key == pygame.K_f:
                    return 'f'
                elif event.key == pygame.K_s:
                    return 's'
        return None

    def set_agent_position(self, pos):
        """Set the agent's position."""
        self.agent_pos = pos

    def set_enemy_position(self, pos):
        """Set the enemy's position."""
        self.enemy_pos = pos

    def set_path(self, path):
        """Set the solution path to display."""
        self.path = path if path else []
        self.stats['path_length'] = len(self.path) - 1 if self.path else 0

    def add_explored(self, pos):
        """Mark a position as explored."""
        self.explored.add(pos)
        self.stats['nodes_explored'] = len(self.explored)

    def set_explored(self, explored_set):
        """Set all explored positions at once."""
        self.explored = explored_set
        self.stats['nodes_explored'] = len(self.explored)

    def reset(self):
        """Reset the visualization state."""
        self.agent_pos = self.maze.start
        self.enemy_pos = None
        self.path = []
        self.explored = set()
        self.stats = {
            'algorithm': 'None',
            'path_length': 0,
            'nodes_explored': 0,
            'status': 'Ready',
            'optimal_length': None,
        }
        self.comparison_results = None
        self.algo_step = None
        self.frontier_cells = []
        self.current_cell = None

    def toggle_walls(self):
        """Toggle all walls on/off."""
        from maze import WALL, EMPTY, START, EXIT

        if self.walls_removed:
            # Restore original walls
            self.maze.grid = [row[:] for row in self.original_grid]
            self.walls_removed = False
            return "Walls: ON"
        else:
            # Remove all walls (keep start and exits)
            for r in range(self.maze.rows):
                for c in range(self.maze.cols):
                    if self.maze.grid[r][c] == WALL:
                        self.maze.grid[r][c] = EMPTY
            self.walls_removed = True
            return "Walls: OFF"

    def animate_path(self, path, delay=0.1, enemy=None):
        """
        Animate the agent moving along a path with smooth transitions.

        Args:
            path: List of (row, col) positions
            delay: Seconds between each step
            enemy: Enemy object for synchronized movement (optional)
        """
        for t, pos in enumerate(path):
            # Check for quit events
            event = self.handle_events()
            if event == 'q':
                return
            elif event == 'r':
                return

            self.set_agent_position(pos)

            # Update enemy position if provided
            if enemy:
                self.set_enemy_position(enemy.get_position(t))

            self.update()
            time.sleep(delay)

    def animate_exploration(self, explored_positions, delay=0.02):
        """
        Animate the exploration process showing cells being discovered.

        Args:
            explored_positions: Set or list of (row, col) positions
            delay: Seconds between each cell reveal
        """
        explored_list = list(explored_positions)
        current_explored = set()

        for pos in explored_list:
            event = self.handle_events()
            if event in ('q', 'r'):
                return False

            current_explored.add(pos)
            self.explored = current_explored
            self.stats['nodes_explored'] = len(current_explored)
            self.update()
            time.sleep(delay)

        return True

    def animate_path_drawing(self, path, delay=0.05, color=None):
        """
        Animate the path being drawn cell by cell.

        Args:
            path: List of (row, col) positions
            delay: Seconds between each cell
            color: Optional color override for the path
        """
        for i in range(len(path)):
            event = self.handle_events()
            if event in ('q', 'r'):
                return False

            # Draw path up to current position
            self.path = path[:i+1]
            self.update()
            time.sleep(delay)

        return True

    def draw_multiple_paths(self, paths_dict):
        """
        Draw multiple algorithm paths with different colors.

        Args:
            paths_dict: Dict of {algorithm_name: path_list}
        """
        algo_colors = {
            'BFS': COLORS['bfs_path'],
            'DFS': COLORS['dfs_path'],
            'A*': COLORS['astar_path'],
        }

        for algo_name, path in paths_dict.items():
            if not path:
                continue

            color = algo_colors.get(algo_name, COLORS['path'])

            # Draw path with offset for visibility
            offset = {'BFS': -3, 'DFS': 0, 'A*': 3}.get(algo_name, 0)

            for pos in path:
                if pos != self.maze.start and pos not in self.maze.exits:
                    rect = self.get_cell_rect(pos[0], pos[1])
                    # Draw a smaller rectangle with offset
                    path_rect = pygame.Rect(
                        rect.left + 10 + offset,
                        rect.top + 10 + offset,
                        rect.width - 20,
                        rect.height - 20
                    )
                    pygame.draw.rect(self.screen, color, path_rect, border_radius=8)

    def pulse_cell(self, row, col, color, pulses=3, duration=0.3):
        """
        Create a pulsing effect on a cell.

        Args:
            row, col: Cell position
            color: Base color
            pulses: Number of pulse cycles
            duration: Total duration in seconds
        """
        frames = 20
        for pulse in range(pulses):
            for frame in range(frames):
                # Calculate pulse intensity using sine wave
                intensity = (math.sin(frame / frames * math.pi * 2) + 1) / 2

                # Interpolate color
                pulse_color = tuple(
                    int(c + (255 - c) * intensity * 0.5) for c in color[:3]
                )

                self.draw_cell(row, col, pulse_color)
                pygame.display.flip()
                time.sleep(duration / (pulses * frames))

    def close(self):
        """Close the pygame window."""
        pygame.quit()


# Test the visualizer
if __name__ == "__main__":
    from maze import Maze

    # Create maze and visualizer
    maze = Maze()
    viz = MazeVisualizer(maze)

    # Example path for testing
    test_path = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 3), (2, 4)]

    print("Maze Visualizer Test")
    print("Press 1, 2, 3 to select algorithm")
    print("Press R to reset, Q to quit")

    running = True
    while running:
        key = viz.handle_events()

        if key == 'q':
            running = False
        elif key == 'r':
            viz.reset()
        elif key == '1':
            viz.stats['algorithm'] = 'BFS'
            viz.stats['status'] = 'Running...'
            viz.set_path(test_path)
            viz.set_explored({(0, 0), (0, 1), (0, 2), (1, 0), (1, 2)})
            viz.animate_path(test_path, delay=0.2)
            viz.stats['status'] = 'Complete'

        viz.update()

    viz.close()
