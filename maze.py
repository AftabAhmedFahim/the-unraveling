import random
import math
import pygame


class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.visited = False
        self.walls = {
            "top": True,
            "right": True,
            "bottom": True,
            "left": True
        }


class Maze:
    def __init__(self, rows, cols, width, height):
        self.rows = rows
        self.cols = cols
        self.width = width
        self.height = height
        self.cell_width = width / cols
        self.cell_height = height / rows
        # Compatibility scalar used by a few callers and style calculations.
        self.cell_size = int(min(self.cell_width, self.cell_height))

        self.grid = self.create_grid()
        self.generate_maze()

        self.exit_row = self.rows - 1
        self.exit_col = self.cols - 1

    def create_grid(self):
        return [[Cell(r, c) for c in range(self.cols)] for r in range(self.rows)]

    def get_unvisited_neighbors(self, cell):
        neighbors = []
        r = cell.row
        c = cell.col

        # (dr, dc, wall_from_current, matching_wall_on_neighbor)
        directions = [
            (-1, 0, "top", "bottom"),
            (0, 1, "right", "left"),
            (1, 0, "bottom", "top"),
            (0, -1, "left", "right")
        ]

        for dr, dc, wall, opposite_wall in directions:
            nr = r + dr
            nc = c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                neighbor = self.grid[nr][nc]
                if not neighbor.visited:
                    neighbors.append((neighbor, wall, opposite_wall))

        return neighbors

    def generate_maze(self):
        # Generate a perfect maze using DFS + backtracking.
        stack = []
        current = self.grid[0][0]
        current.visited = True

        while True:
            neighbors = self.get_unvisited_neighbors(current)

            if neighbors:
                next_cell, wall, opposite_wall = random.choice(neighbors)

                # Carve a bidirectional passage between current and chosen neighbor.
                current.walls[wall] = False
                next_cell.walls[opposite_wall] = False

                stack.append(current)
                current = next_cell
                current.visited = True
            elif stack:
                current = stack.pop()
            else:
                break

    def get_cell_bounds(self, row, col, y_offset=0):
        # Convert a logical cell index into pixel bounds (x0, y0, x1, y1).
        x0 = int(round(col * self.cell_width))
        x1 = int(round((col + 1) * self.cell_width))
        y0 = int(round(row * self.cell_height)) + y_offset
        y1 = int(round((row + 1) * self.cell_height)) + y_offset
        return x0, y0, x1, y1

    def draw(self, screen, y_offset=0):
        wall_color = (28, 44, 80)
        wall_highlight = (120, 152, 212)
        wall_width = max(2, int(min(self.cell_width, self.cell_height) // 14))

        for row in self.grid:
            for cell in row:
                x0, y0, x1, y1 = self.get_cell_bounds(cell.row, cell.col, y_offset)

                if cell.walls["top"]:
                    pygame.draw.line(screen, wall_highlight, (x0, y0 + 1), (x1, y0 + 1), wall_width)
                    pygame.draw.line(screen, wall_color, (x0, y0), (x1, y0), wall_width)
                if cell.walls["right"]:
                    pygame.draw.line(screen, wall_highlight, (x1, y0 + 1), (x1, y1 + 1), wall_width)
                    pygame.draw.line(screen, wall_color, (x1, y0), (x1, y1), wall_width)
                if cell.walls["bottom"]:
                    pygame.draw.line(screen, wall_highlight, (x0, y1 + 1), (x1, y1 + 1), wall_width)
                    pygame.draw.line(screen, wall_color, (x0, y1), (x1, y1), wall_width)
                if cell.walls["left"]:
                    pygame.draw.line(screen, wall_highlight, (x0 + 1, y0), (x0 + 1, y1), wall_width)
                    pygame.draw.line(screen, wall_color, (x0, y0), (x0, y1), wall_width)

    def draw_floor(self, screen, y_offset=0):
        tile_a = (236, 246, 255)
        tile_b = (226, 239, 252)
        for row in self.grid:
            for cell in row:
                x0, y0, x1, y1 = self.get_cell_bounds(cell.row, cell.col, y_offset)
                tile_color = tile_a if (cell.row + cell.col) % 2 == 0 else tile_b
                pygame.draw.rect(screen, tile_color, (x0, y0, x1 - x0, y1 - y0))

    def draw_exit(self, screen, color, y_offset=0, pulse=0.0):
        x0, y0, x1, y1 = self.get_cell_bounds(self.exit_row, self.exit_col, y_offset)
        cell_w = x1 - x0
        cell_h = y1 - y0
        base = min(cell_w, cell_h)
        padding = max(4, base // 4)
        x = x0 + padding
        y = y0 + padding
        rect_w = max(6, cell_w - 2 * padding)
        rect_h = max(6, cell_h - 2 * padding)
        cx = x + rect_w // 2
        cy = y + rect_h // 2

        glow_radius = min(rect_w, rect_h) // 2 + max(8, base // 3) + int(4 * math.sin(pulse * 5.0))
        glow_surface = pygame.Surface((glow_radius * 2 + 6, glow_radius * 2 + 6), pygame.SRCALPHA)
        glow_center = (glow_surface.get_width() // 2, glow_surface.get_height() // 2)

        pygame.draw.circle(glow_surface, (90, 230, 140, 60), glow_center, glow_radius)
        pygame.draw.circle(glow_surface, (130, 255, 170, 85), glow_center, max(6, glow_radius - 6))
        screen.blit(glow_surface, (cx - glow_center[0], cy - glow_center[1]))

        pygame.draw.rect(screen, color, (x, y, rect_w, rect_h))
        pygame.draw.rect(screen, (245, 255, 247), (x, y, rect_w, rect_h), 2)

    def can_move(self, row, col, direction):
        return not self.grid[row][col].walls[direction]
