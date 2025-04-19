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
        self.direction = pygame.Vector2(1, 0)
        self.controller = controller_class(self)
        self.is_ai_controlled = isinstance(self.controller, AIController)

        # NEW: Store head path and desired segment spacing
        self.head_path = [self.head_pos.copy() for _ in range(5)] # Initialize with a few points
        self.segment_spacing = self.radius * 1.5 # Default spacing (e.g., 1.5 times radius)

        # Initialize body based on initial position and spacing
        self.body = [self.head_pos.copy()] * self.length
        self.update_body() # Calculate initial body segment positions

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
        # Adjust spacing based on new radius? Optional.
        # self.segment_spacing = self.radius * 1.5
        # Body length will adjust automatically in update_body

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

    # NEW: Method to update body positions
    def update_body(self):
        """Recalculates body segment positions based on head path and spacing."""
        # Ensure head_path has the current head position
        if not self.head_path or self.head_pos.distance_to(self.head_path[-1]) > 1e-6:
             self.head_path.append(self.head_pos.copy())

        new_body = [self.head_pos.copy()] # First segment is always the head
        current_segment_pos = self.head_pos.copy()
        path_idx = len(self.head_path) - 1
        dist_covered_on_path = 0.0

        # Calculate positions for the remaining segments
        for _ in range(1, self.length):
            target_dist_back = self.segment_spacing # How far back from the previous segment

            # Traverse the path backwards
            while target_dist_back > 0 and path_idx > 0:
                vec_to_prev_point = self.head_path[path_idx - 1] - self.head_path[path_idx]
                dist_between_points = vec_to_prev_point.length()

                if dist_between_points < 1e-6: # Skip zero-length segments in path
                    path_idx -= 1
                    continue

                dist_available_on_segment = dist_between_points - dist_covered_on_path

                if target_dist_back <= dist_available_on_segment:
                    # The next segment position lies on the current path segment
                    fraction = (dist_covered_on_path + target_dist_back) / dist_between_points
                    current_segment_pos = self.head_path[path_idx] + vec_to_prev_point * fraction
                    dist_covered_on_path += target_dist_back # Update how much of the current segment is used
                    target_dist_back = 0 # Found the position
                    break # Exit inner while loop
                else:
                    # Need to consume this entire segment and move to the previous one
                    target_dist_back -= dist_available_on_segment
                    dist_covered_on_path = 0.0 # Reset for the new path segment
                    path_idx -= 1
                    current_segment_pos = self.head_path[path_idx] # Move to the previous path point

            if target_dist_back > 0:
                # Ran out of path, place segment at the oldest point
                current_segment_pos = self.head_path[0].copy()

            new_body.append(current_segment_pos.copy())

        self.body = new_body

        # Prune old head path points (optional optimization)
        # Keep enough path points to cover the snake's length plus buffer
        max_path_length_needed = self.length * self.segment_spacing * 1.5
        current_path_length = 0
        keep_from_index = len(self.head_path) - 1
        while keep_from_index > 0:
            dist = self.head_path[keep_from_index].distance_to(self.head_path[keep_from_index-1])
            if current_path_length + dist > max_path_length_needed:
                break
            current_path_length += dist
            keep_from_index -= 1
        self.head_path = self.head_path[keep_from_index:] 