from settings import *
from math import atan2, degrees

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.ground = True

class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)

class Gun(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        # Player connection
        self.player = player
        self.distance = 100  # Distance from the player
        self.player_direction = pygame.math.Vector2(0, 1)

        # Sprite setup
        super().__init__(groups)
        self.gun_surf = pygame.image.load(IMAGE_PATHS['gun']).convert_alpha()

        # Scale down the gun image
        scale_factor = 0.7  # Adjust this value to make the gun smaller or larger
        self.gun_surf = pygame.transform.scale(self.gun_surf, (int(self.gun_surf.get_width() * scale_factor), int(self.gun_surf.get_height() * scale_factor)))

        self.image = self.gun_surf
        self.rect = self.image.get_rect(center=self.player.rect.center + self.player_direction * self.distance)

    def get_direction(self):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        self.player_direction = (mouse_pos - player_pos).normalize()

    def rotate_gun(self):
        angle = degrees(atan2(self.player_direction.x, self.player_direction.y)) - 90
        if self.player_direction.x > 0:
            self.image = pygame.transform.rotozoom(self.gun_surf, angle, 1)
        else:
            self.image = pygame.transform.rotozoom(self.gun_surf, abs(angle), 1)
            self.image = pygame.transform.flip(self.image, False, True)

    def update(self, dt):
        self.get_direction()
        self.rotate_gun()
        self.rect.center = self.player.rect.center + self.player_direction * self.distance

class Bullet(pygame.sprite.Sprite):
    def __init__(self, surf, pos, direction, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(center=pos)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = BULLET_LIFETIME
        
        self.direction = direction  # Use the direction passed from the input method
        self.speed = BULLET_SPEED

    def update(self, dt):
        self.rect.x += self.direction.x * self.speed * dt
        self.rect.y += self.direction.y * self.speed * dt

        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, player, collision_sprites):
        super().__init__(groups)
        self.player = player

        # Animation frames
        self.frames = frames  # List of frames for the enemy
        self.frame_index = 0  # Current frame index
        self.animation_speed = 6  # Animation speed

        # Set the initial image
        self.image = self.frames[self.frame_index]  # Use the first frame as the initial image
        self.rect = self.image.get_rect(center=pos)  # Set the rect position
        self.hitbox_rect = self.rect.inflate(-20, -40)  # Create a smaller hitbox

        # Movement attributes
        self.direction = pygame.math.Vector2()  # Direction vector
        self.speed = ENEMY_SPEED  # Movement speed
        self.collision_sprites = collision_sprites  # Collision sprites

        # Timer
        self.death_time = 0
        self.death_duration = ENEMY_DEATH_DURATION

    def animate(self, dt):
        # Update the frame index for animation
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0  # Loop the animation

        # Update the current image
        self.image = self.frames[int(self.frame_index)]

    def move(self, dt):
        # Calculate direction towards the player
        player_pos = pygame.Vector2(self.player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        direction = player_pos - enemy_pos

        # Only normalize if the direction vector has a non-zero length
        if direction.length() > 0:
            self.direction = direction.normalize()
        else:
            self.direction = pygame.Vector2(0, 0)  # Stop moving if the player and enemy are at the same position

        # Update the hitbox position
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center  # Sync the rect with the hitbox

    def collision(self, direction):
        # Handle collisions with other sprites
        for sprite in self.collision_sprites:
            if self.hitbox_rect.colliderect(sprite.rect):
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

    def destroy(self):
        # Start a timer
        self.death_time = pygame.time.get_ticks()
        # Change the image
        surf = pygame.mask.from_surface(self.frames[0]).to_surface()
        surf.set_colorkey('black')
        self.image = surf

    def death_timer(self):
        # Check if the timer is over
        if pygame.time.get_ticks() - self.death_time >= self.death_duration:
            self.kill()

    def update(self, dt):
        # Update the enemy's state
        if self.death_time == 0:
            self.move(dt)
            self.animate(dt)
        else:
            self.death_timer()