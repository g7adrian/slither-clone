import pygame
import math
from movement_controller import MovementController, PlayerController, AIController

# Snake Constants
SNAKE_COLOR = (0, 255, 0) # Bright Green
SNAKE_ALT_COLOR = (0, 200, 0) # Darker Green
AI_SNAKE_COLOR = (0, 100, 255) # Bright Blue
AI_SNAKE_ALT_COLOR = (0, 70, 180) # Darker Blue
BASE_RADIUS = 0.5 # Used for drawing size and initial radius calc
INITIAL_WEIGHT = 1
GROWTH_EXPONENT = 0.2 # Controls radius growth

class Snake:
    # Constants as class attributes
    BASE_RADIUS = BASE_RADIUS
    INITIAL_WEIGHT = INITIAL_WEIGHT
    GROWTH_EXPONENT = GROWTH_EXPONENT

    def __init__(self, x, y, controller_class=PlayerController):
        self.head_pos = pygame.Vector2(x, y)
        self.weight = Snake.INITIAL_WEIGHT
        self.radius, self.length = self.__class__._calculate_size(self.weight)
        # Body starts as just the head position repeated for the initial length
        self.body = [self.head_pos.copy() for _ in range(self.length)]
        self.direction = pygame.Vector2(1, 0)
        # Initialize the movement controller
        self.controller = controller_class(self)
        # Track if AI controlled for color
        self.is_ai_controlled = isinstance(self.controller, AIController)

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
        
        # Choose color based on control mode
        main_color = AI_SNAKE_COLOR if self.is_ai_controlled else SNAKE_COLOR
        alt_color = AI_SNAKE_ALT_COLOR if self.is_ai_controlled else SNAKE_ALT_COLOR
        
        # Draw based on actual segment positions in self.body
        for i, segment_world_pos in enumerate(reversed(self.body)):
            color = main_color if i % 2 == 0 else alt_color
            camera_space_pos = segment_world_pos - self.head_pos
            view_space_pos = camera_space_pos * zoom
            screen_pos = view_space_pos + screen_center
            pygame.draw.circle(surface, color, (int(screen_pos.x), int(screen_pos.y)), screen_radius)

    def start_boost(self):
        """Delegate to controller."""
        self.controller.start_boost()

    def stop_boost(self):
        """Delegate to controller."""
        self.controller.stop_boost()

    def move(self, screen_center):
        """Delegate movement to the controller."""
        self.controller.move(screen_center)

    def grow(self, amount=1):
        """Increases weight and recalculates target length/radius."""
        self.weight += amount
        # Update radius and target length (self.length)
        self.radius, self.length = self.__class__._calculate_size(self.weight)
        # The move method will handle preserving segments based on new self.length 

    def toggle_controller(self):
        """Switch between player and AI controller."""
        from movement_controller import PlayerController, AIController
        
        if isinstance(self.controller, PlayerController):
            # Switch to AI controller
            self.controller = AIController(self)
            self.is_ai_controlled = True
        else:
            # Switch to player controller
            self.controller = PlayerController(self)
            self.is_ai_controlled = False
        return self.is_ai_controlled
    
    def handle_mouse_down(self, button):
        """Delegate to controller."""
        self.controller.handle_mouse_down(button)

    def handle_mouse_up(self, button):
        """Delegate to controller."""
        self.controller.handle_mouse_up(button) 