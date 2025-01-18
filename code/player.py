from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        # Load player image
        self.image = pygame.image.load(join('..', 'images', 'player', 'down', '0.png')).convert_alpha()
        self.rect = self.image.get_rect(center=pos)  # Full sprite rectangle
        self.hitbox_rect = self.rect.inflate(-60, -90)  # Create a smaller hitbox inside the rect

        # Movement attributes
        self.direction = pygame.math.Vector2()  # Initialize direction
        self.speed = 500  # Set speed
        self.collision_sprites = collision_sprites

    def input(self):
        # Handle player input (e.g., keyboard)
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction

    def move(self, dt):
        # Move the player based on direction and speed
        self.hitbox_rect.x += self.direction.x * self.speed * dt  # Move hitbox horizontally
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt  # Move hitbox vertically
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center  # Sync the rect with the hitbox

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if self.hitbox_rect.colliderect(sprite.rect):  # Check collision with hitbox
                if direction == 'horizontal':
                    if self.direction.x > 0:  # Moving right
                        self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0:  # Moving left
                        self.hitbox_rect.left = sprite.rect.right
                if direction == 'vertical':
                    if self.direction.y > 0:  # Moving down
                        self.hitbox_rect.bottom = sprite.rect.top
                    if self.direction.y < 0:  # Moving up
                        self.hitbox_rect.top = sprite.rect.bottom

    def update(self, dt):
        # Update player state
        self.input()
        self.move(dt)
        