from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        # Load player image
        self.image = pygame.image.load(join('..', 'images', 'player', 'down', '0.png')).convert_alpha()
        self.rect = self.image.get_rect(center=pos)  # Use get_rect instead of get_frect

        # Movement attributes
        self.direction = pygame.math.Vector2()  # Initialize direction
        self.speed = 500  # Set speed

    def input(self):
        # Handle player input (e.g., keyboard)
        key = pygame.key.get_pressed()
        self.direction.x = int(key[pygame.K_RIGHT]) - int(key[pygame.K_LEFT])
        self.direction.y = int(key[pygame.K_DOWN]) - int(key[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction

    def move(self, dt):
        # Move the player based on direction and speed
        self.rect.center += self.direction * self.speed * dt

    def update(self, dt):
        # Update player state
        self.input()
        self.move(dt)