import unittest
from collections import deque
import sys
import types

try:
    import pygame  # noqa: F401
except ModuleNotFoundError:
    # Logic tests do not call rendering methods; a lightweight stub is enough.
    sys.modules["pygame"] = types.ModuleType("pygame")

from maze import Maze
from player import Player


# Direction deltas shared by both maze and movement tests.
DIRECTIONS = {
    "top": (-1, 0, "bottom"),
    "right": (0, 1, "left"),
    "bottom": (1, 0, "top"),
    "left": (0, -1, "right"),
}


class TestMazeCoreLogic(unittest.TestCase):
    # Core invariants: structure, connectivity, and wall consistency.
    def test_maze_dimensions_and_exit(self):
        maze = Maze(10, 20, 800, 720)
        self.assertEqual(maze.rows, 10)
        self.assertEqual(maze.cols, 20)
        self.assertEqual(len(maze.grid), 10)
        self.assertEqual(len(maze.grid[0]), 20)
        self.assertEqual(maze.exit_row, 9)
        self.assertEqual(maze.exit_col, 19)

    def test_cell_bounds_cover_full_play_area(self):
        maze = Maze(7, 11, 800, 720)

        x0, y0, _, _ = maze.get_cell_bounds(0, 0)
        _, _, x1_last, y1_last = maze.get_cell_bounds(maze.rows - 1, maze.cols - 1)
        self.assertEqual((x0, y0), (0, 0))
        self.assertEqual((x1_last, y1_last), (maze.width, maze.height))

        for c in range(maze.cols - 1):
            _, _, right_edge, _ = maze.get_cell_bounds(0, c)
            next_left, _, _, _ = maze.get_cell_bounds(0, c + 1)
            self.assertEqual(right_edge, next_left)

        for r in range(maze.rows - 1):
            _, _, _, bottom_edge = maze.get_cell_bounds(r, 0)
            _, next_top, _, _ = maze.get_cell_bounds(r + 1, 0)
            self.assertEqual(bottom_edge, next_top)

    def test_neighbor_walls_are_consistent(self):
        maze = Maze(12, 12, 800, 720)
        for r in range(maze.rows):
            for c in range(maze.cols):
                cell = maze.grid[r][c]
                for direction, (dr, dc, opposite) in DIRECTIONS.items():
                    nr = r + dr
                    nc = c + dc
                    if 0 <= nr < maze.rows and 0 <= nc < maze.cols:
                        neighbor = maze.grid[nr][nc]
                        self.assertEqual(cell.walls[direction], neighbor.walls[opposite])

    def test_start_can_reach_exit(self):
        maze = Maze(20, 20, 800, 720)

        start = (0, 0)
        target = (maze.exit_row, maze.exit_col)
        queue = deque([start])
        visited = {start}

        while queue:
            row, col = queue.popleft()
            if (row, col) == target:
                break

            for direction, (dr, dc, _) in DIRECTIONS.items():
                nr = row + dr
                nc = col + dc
                if 0 <= nr < maze.rows and 0 <= nc < maze.cols and maze.can_move(row, col, direction):
                    nxt = (nr, nc)
                    if nxt not in visited:
                        visited.add(nxt)
                        queue.append(nxt)

        self.assertIn(target, visited)


class TestPlayerCoreLogic(unittest.TestCase):
    # Player movement should only follow open maze paths.
    def test_player_cannot_move_through_walls(self):
        maze = Maze(2, 2, 100, 100)
        for row in maze.grid:
            for cell in row:
                cell.walls = {"top": True, "right": True, "bottom": True, "left": True}

        player = Player(0, 0)
        player.move("right", maze)
        self.assertEqual((player.row, player.col), (0, 0))
        self.assertEqual(player.trail, [(0, 0)])

    def test_player_moves_when_path_is_open(self):
        maze = Maze(2, 2, 100, 100)
        for row in maze.grid:
            for cell in row:
                cell.walls = {"top": True, "right": True, "bottom": True, "left": True}

        maze.grid[0][0].walls["right"] = False
        maze.grid[0][1].walls["left"] = False

        player = Player(0, 0)
        player.move("right", maze)
        self.assertEqual((player.row, player.col), (0, 1))
        self.assertEqual(player.trail[-1], (0, 1))


if __name__ == "__main__":
    unittest.main()
