from pathlib import Path
import pygame


class Player:
    def __init__(self, row, col, icon_path="assets/player_icon.png"):
        self.row = row
        self.col = col
        self.trail = [(row, col)]
        self.max_trail_length = 45
        self.icon_original = None
        self.icon_cache = {}
        self._load_icon(icon_path)

    def _load_icon(self, icon_path):
        if not icon_path or not hasattr(pygame, "image"):
            return

        path = Path(icon_path)
        if not path.exists():
            return

        try:
            self.icon_original = pygame.image.load(str(path)).convert_alpha()
        except (pygame.error, OSError):
            # Keep fallback circle rendering if icon loading fails.
            self.icon_original = None

    def _get_scaled_icon(self, icon_size):
        if self.icon_original is None or not hasattr(pygame, "transform"):
            return None

        if icon_size not in self.icon_cache:
            self.icon_cache[icon_size] = pygame.transform.smoothscale(
                self.icon_original, (icon_size, icon_size)
            )
        return self.icon_cache[icon_size]

    def move(self, direction, maze):
        if maze.can_move(self.row, self.col, direction):
            if direction == "top":
                self.row -= 1
            elif direction == "right":
                self.col += 1
            elif direction == "bottom":
                self.row += 1
            elif direction == "left":
                self.col -= 1

            self.trail.append((self.row, self.col))
            if len(self.trail) > self.max_trail_length:
                self.trail.pop(0)

    def draw(self, screen, cell_width, cell_height, color, y_offset=0):
        x = int(round((self.col + 0.5) * cell_width))
        y = int(round((self.row + 0.5) * cell_height)) + y_offset
        base_size = min(cell_width, cell_height)
        radius = max(7, int(base_size // 3))

        # Draw a short fading trail to show recent movement.
        trail_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        trail_radius = max(2, int(base_size // 7))
        trail_total = max(1, len(self.trail) - 1)
        for i, (r, c) in enumerate(self.trail[:-1]):
            tx = int(round((c + 0.5) * cell_width))
            ty = int(round((r + 0.5) * cell_height)) + y_offset
            alpha = int(20 + 85 * ((i + 1) / trail_total))
            pygame.draw.circle(trail_surface, (90, 145, 255, alpha), (tx, ty), trail_radius)
        screen.blit(trail_surface, (0, 0))

        glow_radius = radius + max(6, int(base_size // 5))
        glow_surface = pygame.Surface((glow_radius * 2 + 6, glow_radius * 2 + 6), pygame.SRCALPHA)
        glow_center = (glow_surface.get_width() // 2, glow_surface.get_height() // 2)
        pygame.draw.circle(glow_surface, (70, 155, 255, 60), glow_center, glow_radius)
        pygame.draw.circle(glow_surface, (105, 185, 255, 90), glow_center, max(4, glow_radius - 5))
        screen.blit(glow_surface, (x - glow_center[0], y - glow_center[1]))

        icon_size = max(16, int(base_size * 0.72))
        icon_surface = self._get_scaled_icon(icon_size)

        if icon_surface is not None:
            icon_rect = icon_surface.get_rect(center=(x, y))
            screen.blit(icon_surface, icon_rect)
        else:
            pygame.draw.circle(screen, color, (x, y), radius)
            pygame.draw.circle(screen, (230, 244, 255), (x - radius // 3, y - radius // 3), max(2, radius // 3))
            pygame.draw.circle(screen, (20, 35, 65), (x, y), radius, 2)
