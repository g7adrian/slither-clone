import pygame
import math

# Background Constants
GRID_COLOR = (40, 40, 40) # Dark grey
GRID_SPACING = 100 # Increased base spacing for visibility when zoomed out
LINE_THICKNESS = 1 # Base thickness

def draw_background(surface, snake_head_pos, screen_center, screen_width, screen_height, zoom):
    """Draws grid relative to snake head, scaled by zoom."""
    surface.fill((20, 20, 20))

    screen_grid_spacing = GRID_SPACING * zoom
    screen_line_thickness = max(1, int(LINE_THICKNESS * zoom))

    if screen_grid_spacing < 5:
        return

    # Visible world coordinates range, centered around snake head
    view_width_world = screen_width / zoom
    view_height_world = screen_height / zoom
    world_view_left = snake_head_pos.x - view_width_world / 2
    world_view_top = snake_head_pos.y - view_height_world / 2

    # Find the starting grid lines in world coordinates
    start_x = math.floor(world_view_left / GRID_SPACING) * GRID_SPACING
    start_y = math.floor(world_view_top / GRID_SPACING) * GRID_SPACING

    # Calculate number of lines needed
    num_lines_x = math.ceil(view_width_world / GRID_SPACING) + 1
    num_lines_y = math.ceil(view_height_world / GRID_SPACING) + 1

    # Draw vertical lines
    for i in range(num_lines_x):
        world_x = start_x + i * GRID_SPACING
        # World pos -> Camera Space (relative to head)
        camera_space_x = world_x - snake_head_pos.x
        # Camera Space -> View Space (apply zoom)
        view_space_x = camera_space_x * zoom
        # View Space -> Screen Space (center on screen)
        screen_x = int(view_space_x + screen_center.x)
        pygame.draw.line(surface, GRID_COLOR, (screen_x, 0), (screen_x, screen_height), screen_line_thickness)

    # Draw horizontal lines
    for i in range(num_lines_y):
        world_y = start_y + i * GRID_SPACING
        # World pos -> Camera Space (relative to head)
        camera_space_y = world_y - snake_head_pos.y
        # Camera Space -> View Space (apply zoom)
        view_space_y = camera_space_y * zoom
        # View Space -> Screen Space (center on screen)
        screen_y = int(view_space_y + screen_center.y)
        pygame.draw.line(surface, GRID_COLOR, (0, screen_y), (screen_width, screen_y), screen_line_thickness) 