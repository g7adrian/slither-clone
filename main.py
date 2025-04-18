import pygame
import sys
import math # Import math for area calculation
from snake import Snake # Removed BASE_RADIUS import
from background import draw_background # Import background drawing function
from food import FoodManager, SPAWN_AREA_WIDTH, SPAWN_AREA_HEIGHT # Import FoodManager and boundary constants

# Constants
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
# BACKGROUND_COLOR is now handled by draw_background
FPS = 60 # Frames per second
TEXT_COLOR = (255, 255, 255) # White for text
BOUNDARY_COLOR = (255, 0, 0) # Red for boundary
BOUNDARY_LINE_WIDTH = 3
GAME_OVER_COLOR = (255, 100, 100)
# Target visual radius for the snake when manual zoom is 1.0
TARGET_VISUAL_RADIUS = 10.0
# Zoom control constants - Wider Range
ZOOM_SENSITIVITY = 0.1
MIN_MANUAL_ZOOM = 0.1 # Wider min zoom
MAX_MANUAL_ZOOM = 10.0 # Wider max zoom

# Calculate World Boundary Rect
world_boundary_rect = pygame.Rect(
    -SPAWN_AREA_WIDTH // 2,
    -SPAWN_AREA_HEIGHT // 2,
    SPAWN_AREA_WIDTH,
    SPAWN_AREA_HEIGHT
)

def draw_boundary(surface, boundary_rect, snake_head_pos, screen_center, zoom):
    """Draws the world boundary rectangle transformed to screen coordinates."""
    # Function to transform world point to screen point
    def world_to_screen(world_pos):
        camera_space = world_pos - snake_head_pos
        view_space = camera_space * zoom
        screen_pos = view_space + screen_center
        return screen_pos

    # Get corner points in world coordinates
    top_left = world_to_screen(boundary_rect.topleft)
    top_right = world_to_screen(boundary_rect.topright)
    bottom_left = world_to_screen(boundary_rect.bottomleft)
    bottom_right = world_to_screen(boundary_rect.bottomright)

    # Draw the lines (consider clipping later if needed)
    pygame.draw.line(surface, BOUNDARY_COLOR, top_left, top_right, BOUNDARY_LINE_WIDTH)
    pygame.draw.line(surface, BOUNDARY_COLOR, top_right, bottom_right, BOUNDARY_LINE_WIDTH)
    pygame.draw.line(surface, BOUNDARY_COLOR, bottom_right, bottom_left, BOUNDARY_LINE_WIDTH)
    pygame.draw.line(surface, BOUNDARY_COLOR, bottom_left, top_left, BOUNDARY_LINE_WIDTH)

def main():
    # Initialize Pygame
    pygame.init()

    # Set up the display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Slither Clone")
    clock = pygame.time.Clock() # Create a clock object

    # Center of the screen - useful for camera calculations and drawing
    screen_center = pygame.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    # Font for displaying score/length
    try:
        ui_font = pygame.font.SysFont("Arial", 20) # Slightly smaller font
        game_over_font = pygame.font.SysFont("Arial", 72) # Larger font for game over message
    except pygame.error:
        print("Warning: System font 'Arial' not found, using default font.")
        ui_font = pygame.font.Font(None, 24) # Default font
        game_over_font = pygame.font.Font(None, 80) # Larger default font for game over message

    # Create the player snake at world position (0, 0)
    # Its screen position will be handled by the camera
    player_snake = Snake(0, 0)
    food_manager = FoodManager() # Create the food manager

    manual_zoom_factor = 1.0 # Start at 1.0 manual zoom
    game_state = "playing" # Initial game state
    snake_alive = True

    # Game loop
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Only handle game input if playing
            if game_state == "playing":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # 1 is the left mouse button
                        player_snake.start_boost()
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        player_snake.stop_boost()
                elif event.type == pygame.MOUSEWHEEL: # Handle scroll wheel
                    # Increase/decrease zoom factor
                    manual_zoom_factor += event.y * ZOOM_SENSITIVITY
                    # Clamp zoom factor within limits
                    manual_zoom_factor = max(MIN_MANUAL_ZOOM, min(MAX_MANUAL_ZOOM, manual_zoom_factor))
            # Allow closing window even when game over

        # --- Update Phase ---
        if snake_alive:
            player_snake.move(screen_center)
            food_manager.update(player_snake.head_pos, player_snake.radius) # Update food positions (magnet effect)

            # Check for food collisions
            eaten_food_index = food_manager.check_collision(player_snake.head_pos, player_snake.radius)
            if eaten_food_index is not None:
                eaten_food = food_manager.remove_food(eaten_food_index)
                if eaten_food:
                    player_snake.grow(eaten_food.value)
                # Consider spawning new food here if desired
                # food_manager.spawn_one_food()

            # Check for boundary collisions
            if not world_boundary_rect.collidepoint(player_snake.head_pos.x, player_snake.head_pos.y):
                game_state = "game_over"
                snake_alive = False
                print("GAME OVER - Hit Boundary") # Console message

        # --- Drawing Phase ---
        # Calculate effective zoom to achieve TARGET_VISUAL_RADIUS at manual_zoom=1
        # effective_zoom = (TARGET_VISUAL_RADIUS / world_radius) * manual_zoom
        world_radius = player_snake.radius if player_snake.radius > 1e-9 else 1e-9 # Avoid division by zero
        effective_zoom = (TARGET_VISUAL_RADIUS / world_radius) * manual_zoom_factor

        # Remove camera_offset, pass snake_head_pos to draw functions
        snake_head_pos = player_snake.head_pos

        draw_background(screen, snake_head_pos, screen_center, SCREEN_WIDTH, SCREEN_HEIGHT, effective_zoom)
        draw_boundary(screen, world_boundary_rect, snake_head_pos, screen_center, effective_zoom)

        # Draw food and snake only if snake is alive
        if snake_alive:
            food_manager.draw(screen, snake_head_pos, screen_center, effective_zoom)
            player_snake.draw(screen, screen_center, effective_zoom)

        # Calculate area bounds for display
        segment_area = math.pi * player_snake.radius**2
        lower_bound = math.floor(player_snake.length) * segment_area # Use floor length for bounds
        upper_bound = math.ceil(player_snake.length) * segment_area # Use ceil length for bounds

        # Get food count
        food_count = len(food_manager.foods)

        # Draw UI Text (with area bounds and food count)
        info_text_line1 = f"Weight: {player_snake.weight:.0f} (Radius: {player_snake.radius:.2f}, Length: {player_snake.length:d})"
        info_text_line2 = f"Bounds: [{lower_bound:.1f} - {upper_bound:.1f}] Zoom: {manual_zoom_factor:.2f}"
        info_text_line3 = f"Food Count: {food_count}"

        text_surface1 = ui_font.render(info_text_line1, True, TEXT_COLOR)
        text_rect1 = text_surface1.get_rect()
        text_rect1.topright = (SCREEN_WIDTH - 10, 10)

        text_surface2 = ui_font.render(info_text_line2, True, TEXT_COLOR)
        text_rect2 = text_surface2.get_rect()
        text_rect2.topright = (SCREEN_WIDTH - 10, text_rect1.bottom + 2)

        text_surface3 = ui_font.render(info_text_line3, True, TEXT_COLOR)
        text_rect3 = text_surface3.get_rect()
        text_rect3.topright = (SCREEN_WIDTH - 10, text_rect2.bottom + 2) # Position below line 2

        screen.blit(text_surface1, text_rect1)
        screen.blit(text_surface2, text_rect2)
        screen.blit(text_surface3, text_rect3) # Blit the third line

        # Draw Game Over message if applicable
        if game_state == "game_over":
            game_over_text = "GAME OVER!"
            game_over_surface = game_over_font.render(game_over_text, True, GAME_OVER_COLOR)
            game_over_rect = game_over_surface.get_rect(center=screen_center)
            screen.blit(game_over_surface, game_over_rect)

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

    # Quit Pygame
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main() 