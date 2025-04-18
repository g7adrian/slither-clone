import pygame
import math

# Snake Constants
SNAKE_COLOR = (0, 255, 0) # Bright Green
SNAKE_ALT_COLOR = (0, 200, 0) # Darker Green
BASE_RADIUS = 0.5 # Used for drawing size and initial radius calc
INITIAL_WEIGHT = 1
GROWTH_EXPONENT = 0.2 # Controls radius growth
SNAKE_SPEED = 1
BOOST_SPEED = 2
ROTATION_SPEED = 50
ANGLE_TOLERANCE = 0.5

class Snake:
    # Constants as class attributes
    BASE_RADIUS = BASE_RADIUS
    INITIAL_WEIGHT = INITIAL_WEIGHT
    GROWTH_EXPONENT = GROWTH_EXPONENT

    def __init__(self, x, y):
        self.head_pos = pygame.Vector2(x, y)
        self.weight = Snake.INITIAL_WEIGHT
        self.radius, self.length = self.__class__._calculate_size(self.weight)
        # Body starts as just the head position repeated for the initial length
        self.body = [self.head_pos.copy() for _ in range(self.length)]
        self.direction = pygame.Vector2(1, 0)
        self.boosting = False

    @classmethod
    def _calculate_size(cls, weight):
        """Calculates radius first based on weight, then floored length."""
        effective_weight = max(1, weight)
        new_radius = cls.BASE_RADIUS * (effective_weight / cls.INITIAL_WEIGHT) ** cls.GROWTH_EXPONENT
        new_radius = max(1e-9, new_radius)
        segment_area = math.pi * new_radius**2
        if segment_area <= 0:
            new_length = 1
        else:
            required_length = max(1, math.floor(effective_weight / segment_area))
            new_length = required_length
        return new_radius, new_length # Return integer length

    def draw(self, surface, screen_center, zoom):
        # Use world radius * zoom for drawing to reflect zoom changes
        screen_radius = int(self.radius * zoom)
        if screen_radius < 1: screen_radius = 1
        # Draw based on actual segment positions in self.body
        for i, segment_world_pos in enumerate(reversed(self.body)):
            color = SNAKE_COLOR if i % 2 == 0 else SNAKE_ALT_COLOR
            camera_space_pos = segment_world_pos - self.head_pos
            view_space_pos = camera_space_pos * zoom
            screen_pos = view_space_pos + screen_center
            pygame.draw.circle(surface, color, (int(screen_pos.x), int(screen_pos.y)), screen_radius)

    def start_boost(self):
        self.boosting = True

    def stop_boost(self):
        self.boosting = False

    def move(self, screen_center):
        # --- Rotation Logic ---
        mouse_pos = pygame.mouse.get_pos()
        target_direction = pygame.Vector2(mouse_pos) - screen_center
        if target_direction.length_squared() > 0:
            target_direction.normalize_ip()
            angle_magnitude = abs(self.direction.angle_to(target_direction))
            if angle_magnitude > ANGLE_TOLERANCE:
                cross_product = self.direction.cross(target_direction)
                rotation_delta = min(angle_magnitude, ROTATION_SPEED)
                if cross_product != 0:
                    rotation_amount = math.copysign(rotation_delta, cross_product)
                    self.direction = self.direction.rotate(rotation_amount)

        # --- Classic Snake Movement --- 
        # Calculate speed
        current_speed = BOOST_SPEED if self.boosting else SNAKE_SPEED
        # Calculate new head position
        new_head_pos = self.head_pos + self.direction * current_speed

        # Update head position reference
        self.head_pos = new_head_pos

        # Insert new head position at the front of the body list
        self.body.insert(0, self.head_pos.copy())

        # Remove tail segment if body is longer than target length
        # self.length is the target integer length calculated by _calculate_size
        target_segments = self.length
        while len(self.body) > target_segments:
            self.body.pop()

    def grow(self, amount=1):
        """Increases weight and recalculates target length/radius."""
        self.weight += amount
        # Update radius and target length (self.length)
        self.radius, self.length = self.__class__._calculate_size(self.weight)
        # The move method will handle preserving segments based on new self.length 