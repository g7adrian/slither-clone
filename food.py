import pygame
import random
import math # Added for ceiling in draw
# Import Snake to calculate initial radius
from snake import Snake

# Calculate initial snake radius to set food radius
# We need to access the class method _calculate_size
INITIAL_SNAKE_RADIUS, _ = Snake._calculate_size(Snake.INITIAL_WEIGHT)

# Food Constants
FOOD_COLOR = (255, 192, 203) # Pink
# Set FOOD_RADIUS to match the snake's initial world radius
FOOD_RADIUS = INITIAL_SNAKE_RADIUS
FOOD_VALUE = 1 # Keep value at 1 per piece
# Calculate count based on density (100 per 100x100 grid cell area)
GRID_CELL_AREA = 100 * 100 # Assuming grid spacing is 100 (as in background.py)
TARGET_DENSITY_PER_CELL = 100
SPAWN_AREA_WIDTH = 4000
SPAWN_AREA_HEIGHT = 4000
SPAWN_AREA = SPAWN_AREA_WIDTH * SPAWN_AREA_HEIGHT
NUM_GRID_CELLS = SPAWN_AREA / GRID_CELL_AREA
INITIAL_FOOD_COUNT = int(NUM_GRID_CELLS * TARGET_DENSITY_PER_CELL) # Approx 160,000
MAGNET_SPEED = 2.1
REPLENISH_CHANCE = 0.1 # 10% chance to respawn food when eaten

class Food:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        # Use the calculated FOOD_RADIUS constant
        self.radius = FOOD_RADIUS
        self.color = FOOD_COLOR
        self.value = FOOD_VALUE

class FoodManager:
    def __init__(self):
        self.foods = []
        self.spawn_area_rect = pygame.Rect(
            -SPAWN_AREA_WIDTH // 2,
            -SPAWN_AREA_HEIGHT // 2,
            SPAWN_AREA_WIDTH,
            SPAWN_AREA_HEIGHT
        )
        self.spawn_initial_food()

    def spawn_initial_food(self):
        """Spawns the initial batch of food."""
        for _ in range(INITIAL_FOOD_COUNT):
            self._spawn_one_food()

    def _spawn_one_food(self):
        """Spawns a single food pellet in the defined area."""
        x = random.uniform(self.spawn_area_rect.left, self.spawn_area_rect.right)
        y = random.uniform(self.spawn_area_rect.top, self.spawn_area_rect.bottom)
        self.foods.append(Food(x, y))

    def update(self, snake_head_pos, snake_radius):
        """Moves food towards the snake head if within 2x snake radius."""
        # Calculate squared distance threshold based on 2 * snake_radius
        magnet_distance_threshold_sq = (10 * snake_radius) ** 2

        for food in self.foods:
            direction_to_snake = snake_head_pos - food.pos
            distance_sq = direction_to_snake.length_squared()

            # Check if within the dynamic magnet range
            if 0 < distance_sq < magnet_distance_threshold_sq:
                direction_to_snake.normalize_ip()
                food.pos += direction_to_snake * MAGNET_SPEED

    def check_collision(self, snake_head_pos, snake_radius):
        """Checks if the snake head collides with any food using snake's current radius."""
        # Uses the current FOOD_RADIUS constant
        collision_radius_sq = (snake_radius + FOOD_RADIUS) ** 2
        # Iterate backwards for safe removal during collision check potentially
        for i in range(len(self.foods) - 1, -1, -1):
            food = self.foods[i]
            distance_sq = snake_head_pos.distance_squared_to(food.pos)
            if distance_sq < collision_radius_sq:
                return i
        return None

    def remove_food(self, index):
        """Removes food and potentially replenishes."""
        if 0 <= index < len(self.foods):
            removed_food = self.foods.pop(index)
            # Randomly replenish
            if random.random() < REPLENISH_CHANCE:
                self._spawn_one_food()
            return removed_food
        return None

    def draw(self, surface, snake_head_pos, screen_center, zoom):
        """Draws food relative to snake head, scaled by zoom."""
        # Uses the current FOOD_RADIUS constant
        screen_radius = int(FOOD_RADIUS * zoom)
        if screen_radius < 1: screen_radius = 1

        # Calculate visible world bounds for culling
        view_width_world = surface.get_width() / zoom
        view_height_world = surface.get_height() / zoom
        view_rect_world = pygame.Rect(
            snake_head_pos.x - view_width_world / 2 - FOOD_RADIUS,
            snake_head_pos.y - view_height_world / 2 - FOOD_RADIUS,
            view_width_world + FOOD_RADIUS * 2,
            view_height_world + FOOD_RADIUS * 2
        )

        for food in self.foods:
            # Basic culling (check if food's world position is potentially visible)
            if not view_rect_world.collidepoint(food.pos.x, food.pos.y):
                 continue

            # World pos -> Camera Space (relative to head)
            camera_space_pos = food.pos - snake_head_pos
            # Camera Space -> View Space (apply zoom)
            view_space_pos = camera_space_pos * zoom
            # View Space -> Screen Space (center on screen)
            screen_pos = view_space_pos + screen_center

            pygame.draw.circle(surface, food.color, (int(screen_pos.x), int(screen_pos.y)), screen_radius) 