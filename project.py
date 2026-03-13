import sys
import time
import math
import random
import pygame

from maze import Maze
from player import Player

pygame.init()

# Window settings
WIDTH = 800
HEIGHT = 800
INFO_BAR_HEIGHT = 80
GAME_HEIGHT = HEIGHT - INFO_BAR_HEIGHT

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Unravelling")

# Colors
BG_TOP = (14, 24, 52)
BG_BOTTOM = (6, 10, 24)
TEXT_PRIMARY = (240, 247, 255)
TEXT_MUTED = (183, 206, 236)
ACCENT = (98, 155, 255)
SUCCESS = (56, 210, 124)

TITLE_FONT = pygame.font.SysFont("bahnschrift", 74, bold=True)
BIG_FONT = pygame.font.SysFont("bahnschrift", 62, bold=True)
FONT = pygame.font.SysFont("segoeui", 34, bold=True)
SMALL_FONT = pygame.font.SysFont("segoeui", 24)

CLOCK = pygame.time.Clock()
FPS = 60

# Pre-generated sparkle points keep background animation stable across frames.
SPARK_RNG = random.Random(42)
SPARKS = [
    (
        SPARK_RNG.randint(0, WIDTH),
        SPARK_RNG.randint(0, HEIGHT),
        SPARK_RNG.randint(1, 2),
        SPARK_RNG.random() * math.tau
    )
    for _ in range(90)
]


def quit_game():
    pygame.quit()
    sys.exit()


def draw_text(text, font, color, surface, x, y, center=False, shadow=False):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    if shadow:
        shadow_render = font.render(text, True, (14, 22, 40))
        shadow_rect = shadow_render.get_rect()
        if center:
            shadow_rect.center = (x + 2, y + 2)
        else:
            shadow_rect.topleft = (x + 2, y + 2)
        surface.blit(shadow_render, shadow_rect)
    surface.blit(rendered, rect)


def draw_text_right(text, font, color, surface, right_x, y, shadow=False):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    rect.topright = (right_x, y)
    if shadow:
        shadow_render = font.render(text, True, (14, 22, 40))
        shadow_rect = shadow_render.get_rect()
        shadow_rect.topright = (right_x + 2, y + 2)
        surface.blit(shadow_render, shadow_rect)
    surface.blit(rendered, rect)


def draw_vertical_gradient(surface, top_color, bottom_color, rect=None):
    if rect is None:
        rect = surface.get_rect()
    x, y, w, h = rect
    if h <= 1:
        pygame.draw.rect(surface, top_color, rect)
        return

    for i in range(h):
        blend = i / (h - 1)
        color = (
            int(top_color[0] + (bottom_color[0] - top_color[0]) * blend),
            int(top_color[1] + (bottom_color[1] - top_color[1]) * blend),
            int(top_color[2] + (bottom_color[2] - top_color[2]) * blend)
        )
        pygame.draw.line(surface, color, (x, y + i), (x + w, y + i))


def draw_background(surface, t):
    draw_vertical_gradient(surface, BG_TOP, BG_BOTTOM)
    spark_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for sx, sy, radius, phase in SPARKS:
        alpha = 28 + int(36 * (0.5 + 0.5 * math.sin(t * 1.8 + phase)))
        pygame.draw.circle(spark_surface, (179, 212, 255, alpha), (sx, sy), radius)
    surface.blit(spark_surface, (0, 0))


def draw_panel(surface, rect, fill_rgba, border_color, radius=18):
    shadow = pygame.Surface((rect.width + 8, rect.height + 8), pygame.SRCALPHA)
    pygame.draw.rect(
        shadow,
        (5, 10, 24, 95),
        shadow.get_rect(),
        border_radius=radius + 2
    )
    surface.blit(shadow, (rect.x + 4, rect.y + 5))

    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel, fill_rgba, panel.get_rect(), border_radius=radius)
    pygame.draw.rect(panel, border_color, panel.get_rect(), width=2, border_radius=radius)
    surface.blit(panel, rect.topleft)


def start_screen():
    while True:
        t = pygame.time.get_ticks() / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    return
                if event.key == pygame.K_e:
                    quit_game()

        draw_background(SCREEN, t)
        draw_text("The Unravelling", TITLE_FONT, TEXT_PRIMARY, SCREEN, WIDTH // 2, 185, center=True, shadow=True)

        pulse = 0.5 + 0.5 * math.sin(t * 2.2)
        play_rect = pygame.Rect(WIDTH // 2 - 220, 310, 440, 92)
        exit_rect = pygame.Rect(WIDTH // 2 - 220, 430, 440, 92)

        play_tint = int(244 + 8 * pulse)
        exit_tint = int(238 + 8 * (1 - pulse))
        draw_panel(SCREEN, play_rect, (play_tint, 250, 255, 228), (168, 204, 255), radius=16)
        draw_panel(SCREEN, exit_rect, (exit_tint, 246, 255, 228), (168, 204, 255), radius=16)

        draw_text("Play(P)", FONT, (45, 73, 132), SCREEN, play_rect.centerx, play_rect.centery, center=True)
        draw_text("Exit(E)", FONT, (45, 73, 132), SCREEN, exit_rect.centerx, exit_rect.centery, center=True)

        pygame.display.flip()
        CLOCK.tick(FPS)


def choose_difficulty():
    # Keyboard menu mapping: 1=Easy, 2=Medium, 3=Hard.
    while True:
        t = pygame.time.get_ticks() / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return 10, 10
                elif event.key == pygame.K_2:
                    return 20, 20
                elif event.key == pygame.K_3:
                    return 30, 30

        draw_background(SCREEN, t)

        draw_text("The Unravelling", TITLE_FONT, TEXT_PRIMARY, SCREEN, WIDTH // 2, 130, center=True, shadow=True)
        draw_text("Choose Difficulty", FONT, TEXT_MUTED, SCREEN, WIDTH // 2, 210, center=True, shadow=True)

        menu_rect = pygame.Rect(WIDTH // 2 - 270, 250, 540, 350)
        draw_panel(SCREEN, menu_rect, (244, 250, 255, 220), (190, 217, 255))

        options = [
            ("1", "Easy", "10 x 10"),
            ("2", "Medium", "20 x 20"),
            ("3", "Hard", "30 x 30")
        ]
        for i, (key, label, size) in enumerate(options):
            item_rect = pygame.Rect(menu_rect.x + 35, menu_rect.y + 30 + i * 95, menu_rect.width - 70, 74)
            pulse = 0.5 + 0.5 * math.sin(t * 2.1 + i * 0.9)
            tint = int(240 + 10 * pulse)
            draw_panel(SCREEN, item_rect, (tint, 248, 255, 230), (168, 204, 255), radius=14)
            draw_text(f"{key} - {label}", FONT, (45, 73, 132), SCREEN, item_rect.x + 18, item_rect.y + 17, shadow=False)
            draw_text(f"({size})", SMALL_FONT, (85, 113, 170), SCREEN, item_rect.right - 120, item_rect.y + 24, shadow=False)

        draw_text("Controls: Arrow keys to move", SMALL_FONT, TEXT_MUTED, SCREEN, WIDTH // 2, 652, center=True, shadow=True)
        draw_text("R = Restart, M = Menu", SMALL_FONT, TEXT_MUTED, SCREEN, WIDTH // 2, 685, center=True, shadow=True)

        pygame.display.flip()
        CLOCK.tick(FPS)


def create_new_game(rows, cols):
    # Reset all state for a fresh maze run.
    maze = Maze(rows, cols, WIDTH, GAME_HEIGHT)
    player = Player(0, 0)
    start_time = time.time()
    won = False
    final_time = 0
    return maze, player, start_time, won, final_time


def main():
    start_screen()
    rows, cols = choose_difficulty()
    maze, player, start_time, won, final_time = create_new_game(rows, cols)

    while True:
        t = pygame.time.get_ticks() / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    maze, player, start_time, won, final_time = create_new_game(rows, cols)

                if event.key == pygame.K_m:
                    rows, cols = choose_difficulty()
                    maze, player, start_time, won, final_time = create_new_game(rows, cols)

                if not won:
                    if event.key == pygame.K_UP:
                        player.move("top", maze)
                    elif event.key == pygame.K_RIGHT:
                        player.move("right", maze)
                    elif event.key == pygame.K_DOWN:
                        player.move("bottom", maze)
                    elif event.key == pygame.K_LEFT:
                        player.move("left", maze)

        if not won and player.row == maze.exit_row and player.col == maze.exit_col:
            won = True
            final_time = time.time() - start_time

        draw_background(SCREEN, t)

        # Top info bar
        top_rect = pygame.Rect(12, 10, WIDTH - 24, INFO_BAR_HEIGHT - 18)
        draw_panel(SCREEN, top_rect, (242, 249, 255, 220), (178, 210, 255), radius=16)

        if won:
            timer_text = f"Final Time: {final_time:.2f}s"
        else:
            timer_text = f"Time: {time.time() - start_time:.2f}s"

        draw_text(timer_text, FONT, (36, 67, 126), SCREEN, 28, 22)
        draw_text(f"Size: {rows}x{cols}", FONT, (47, 84, 150), SCREEN, 292, 22)

        # Draw maze and game objects
        maze.draw_floor(SCREEN, INFO_BAR_HEIGHT)
        maze.draw(SCREEN, INFO_BAR_HEIGHT)
        maze.draw_exit(SCREEN, SUCCESS, INFO_BAR_HEIGHT, pulse=t)
        player.draw(SCREEN, maze.cell_width, maze.cell_height, ACCENT, INFO_BAR_HEIGHT)

        # Win overlay
        if won:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((8, 14, 30, 165))
            SCREEN.blit(overlay, (0, 0))

            card_rect = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 - 155, 500, 300)
            draw_panel(SCREEN, card_rect, (244, 250, 255, 232), (166, 202, 255), radius=20)

            win_tint = 200 + int(50 * (0.5 + 0.5 * math.sin(t * 4.0)))
            draw_text("You Win!", BIG_FONT, (win_tint, 76, 76), SCREEN, WIDTH // 2, HEIGHT // 2 - 70, center=True, shadow=True)
            draw_text(f"Time: {final_time:.2f} seconds", FONT, (38, 68, 126), SCREEN, WIDTH // 2, HEIGHT // 2 - 6, center=True)
            draw_text("Restart(R)", SMALL_FONT, (74, 116, 184), SCREEN, card_rect.x + 20, card_rect.bottom - 38)
            draw_text_right("Menu(M)", SMALL_FONT, (74, 116, 184), SCREEN, card_rect.right - 20, card_rect.bottom - 38)

        pygame.display.flip()
        CLOCK.tick(FPS)


if __name__ == "__main__":
    main()
