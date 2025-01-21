from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        # Load player image
        self.load_images()
        self.state, self.frame_index = 'down', 0
        self.image = self.frames[self.state][self.frame_index]  # Set initial image
        self.rect = self.image.get_rect(center=pos)  # Full sprite rectangle
        self.hitbox_rect = self.rect.inflate(-60, -90)  # Create a smaller hitbox inside the rect

        # Movement attributes
        self.direction = pygame.math.Vector2()  # Initialize direction
        self.speed = 500  # Set speed
        self.collision_sprites = collision_sprites

    def load_images(self):
        # Load player images
        self.frames = {'up': [], 'down': [], 'left': [], 'right': []}

        for state in self.frames.keys():
            for folder_path, sub_folders, file_names in walk(join('..', 'images', 'player', state)):
                if file_names:
                    for file_name in sorted(file_names, key=lambda name: int(name.split('.')[0])):
                        full_path = join(folder_path, file_name)
                        surf = pygame.image.load(full_path).convert_alpha()
                        self.frames[state].append(surf)

    def input(self):
        # Handle player input (e.g., keyboard)
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
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

    def animate(self, dt):
        # Get state based on direction
        if self.direction.x != 0:
            self.state = 'right' if self.direction.x > 0 else 'left'
        elif self.direction.y != 0:
            self.state = 'down' if self.direction.y > 0 else 'up'

        # Animate
        if self.direction.magnitude() != 0:  # Only animate if the player is moving
            self.frame_index += 5 * dt  # Increment frame index
            if self.frame_index >= len(self.frames[self.state]):  # Loop animation
                self.frame_index = 0
            self.image = self.frames[self.state][int(self.frame_index)]  # Update image

    def update(self, dt):
        # Update player state
        self.input()
        self.move(dt)
        self.animate(dt)