import pygame
import math
import random

# Movement Constants
SNAKE_SPEED = 1
BOOST_SPEED = 2
ROTATION_SPEED = 50
ANGLE_TOLERANCE = 0.5
MAX_MOUSE_MOVEMENT_SPEED = 100.0  # Maximum pixels per frame the mouse can move

class MovementController:
    """Base class for snake movement controllers."""
    
    def __init__(self, snake):
        """Initialize the controller with a reference to the snake."""
        self.snake = snake
        self.boosting = False
        
        # Track both desired and actual mouse positions
        self.desired_mouse_pos = pygame.Vector2(0, 0)
        self.actual_mouse_pos = pygame.Vector2(0, 0)
        self.max_mouse_movement_speed = MAX_MOUSE_MOVEMENT_SPEED
    
    def start_boost(self):
        """Start boosting the snake."""
        self.boosting = True
    
    def stop_boost(self):
        """Stop boosting the snake."""
        self.boosting = False
    
    def _limit_mouse_movement(self):
        """Limit how quickly the mouse can move between frames."""
        # Calculate vector from actual to desired position
        movement_vector = self.desired_mouse_pos - self.actual_mouse_pos
        movement_distance = movement_vector.length()
        
        # If movement is within limit, set actual to desired
        if movement_distance <= self.max_mouse_movement_speed:
            self.actual_mouse_pos = self.desired_mouse_pos.copy()
        else:
            # Otherwise, limit the movement distance
            movement_vector.scale_to_length(self.max_mouse_movement_speed)
            self.actual_mouse_pos += movement_vector
    
    def move(self, screen_center):
        """Base movement logic for the snake."""
        # Update desired mouse position via implementation-specific method
        self.update_desired_position()
        
        # Apply movement speed limits
        self._limit_mouse_movement()
        
        # Calculate target direction from actual mouse position to screen center
        target_vector = self.actual_mouse_pos - screen_center
        
        # Handle rotation if we have a valid target direction
        if target_vector.length_squared() > 0:
            target_direction = target_vector.copy().normalize()
            self._rotate_to_target(target_direction)
        
        # Calculate current speed based on boost state
        current_speed = BOOST_SPEED if self.boosting else SNAKE_SPEED
        
        # Calculate new head position
        new_head_pos = self.snake.head_pos + self.snake.direction * current_speed
        
        # Update head position reference
        self.snake.head_pos = new_head_pos
        
        # Insert new head position at the front of the body list
        self.snake.body.insert(0, self.snake.head_pos.copy())
        
        # Remove tail segment if body is longer than target length
        target_segments = self.snake.length
        while len(self.snake.body) > target_segments:
            self.snake.body.pop()
    
    def _rotate_to_target(self, target_direction):
        """Rotate the snake's direction towards the target direction."""
        angle_magnitude = abs(self.snake.direction.angle_to(target_direction))
        if angle_magnitude > ANGLE_TOLERANCE:
            cross_product = self.snake.direction.cross(target_direction)
            rotation_delta = min(angle_magnitude, ROTATION_SPEED)
            if cross_product != 0:
                rotation_amount = math.copysign(rotation_delta, cross_product)
                self.snake.direction = self.snake.direction.rotate(rotation_amount)
    
    def update_desired_position(self):
        """
        Update the controller's desired mouse position.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement update_desired_position")


class PlayerController(MovementController):
    """Controller that uses the real mouse for input."""
    
    def __init__(self, snake):
        super().__init__(snake)
        # Initialize with current true mouse position
        mouse_pos = pygame.mouse.get_pos()
        self.desired_mouse_pos = pygame.Vector2(mouse_pos)
        self.actual_mouse_pos = pygame.Vector2(mouse_pos)
        # Track left mouse button state
        self.left_mouse_pressed = False
    
    def update_desired_position(self):
        """Update desired position based on real mouse."""
        # Get the true mouse position
        self.desired_mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        
        # Check for left mouse button state
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0] and not self.left_mouse_pressed:
            self.start_boost()
            self.left_mouse_pressed = True
        elif not mouse_buttons[0] and self.left_mouse_pressed:
            self.stop_boost()
            self.left_mouse_pressed = False


class AIController(MovementController):
    """Controller that uses a virtual mouse for AI-controlled movement."""
    
    def __init__(self, snake):
        super().__init__(snake)
        # Initialize virtual mouse at screen center
        screen = pygame.display.get_surface()
        center_pos = pygame.Vector2(
            screen.get_width() // 2,
            screen.get_height() // 2
        )
        self.desired_mouse_pos = center_pos.copy()
        self.actual_mouse_pos = center_pos.copy()
        
        # AI behavior timers and state
        self.target_change_timer = 0
        self.target_change_interval = random.randint(30, 120)
        self.boost_timer = 0
        self.boost_interval = random.randint(180, 360)
        self.boost_duration = 0
    
    def _set_random_target(self):
        """Set a new random target mouse position on screen."""
        screen = pygame.display.get_surface()
        screen_width, screen_height = screen.get_size()
        
        # Keep targets away from edges
        margin = 100
        x = random.uniform(margin, screen_width - margin)
        y = random.uniform(margin, screen_height - margin)
        
        self.desired_mouse_pos = pygame.Vector2(x, y)
    
    def update_desired_position(self):
        """Update desired position based on AI decisions."""
        # First update AI logic which sets the desired position
        self.update_ai()
    
    def update_ai(self):
        """Update AI decisions including movement target and boost."""
        # Update target change timer
        self.target_change_timer += 1
        if self.target_change_timer >= self.target_change_interval:
            self._set_random_target()
            self.target_change_timer = 0
            self.target_change_interval = random.randint(30, 120)
        
        # Update boost timer
        self.boost_timer += 1
        
        # If boosting, check if boost duration has ended
        if self.boosting:
            self.boost_duration -= 1
            if self.boost_duration <= 0:
                self.stop_boost()
        # Otherwise, consider starting a boost
        elif self.boost_timer >= self.boost_interval:
            # 70% chance to start boosting when timer hits
            if random.random() < 0.7:
                self.start_boost()
                self.boost_duration = random.randint(15, 45)
            
            # Reset boost timer regardless of decision
            self.boost_timer = 0
            self.boost_interval = random.randint(180, 360) 