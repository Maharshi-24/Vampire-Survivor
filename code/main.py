from genericpath import exists, isdir
from os import listdir
from settings import *
from player import Player
from sprites import *
from pytmx.util_pygame import load_pygame
from groups import AllSprites
from random import randint, choice
import math

class Game:
    def __init__(self):
        # Setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Survivor Shooter')
        self.clock = pygame.time.Clock()
        self.running = True

        # Groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # Timers
        self.can_shoot = True
        self.shoot_time = 0

        # Enemy timer
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, ENEMY_SPAWN_INTERVAL)
        self.spawn_positions = []

        # Player health
        self.player_health = MAX_HEALTH
        self.health_bar_shake_timer = 0
        self.damage_flash_timer = 0
        self.low_health_pulse_alpha = 0

        # Audio
        self.shoot_sound = pygame.mixer.Sound(AUDIO_PATHS['shoot'])
        self.shoot_sound.set_volume(AUDIO_VOLUME)
        self.impact_sound = pygame.mixer.Sound(AUDIO_PATHS['impact'])
        self.impact_sound.set_volume(IMPACT_VOLUME)
        self.music = pygame.mixer.Sound(AUDIO_PATHS['music'])
        self.music.set_volume(MUSIC_VOLUME)
        self.music.play(-1)

        # Setup
        self.load_images()
        self.setup()

    def load_images(self):
        # Load bullet image
        self.bullet_surf = pygame.image.load(IMAGE_PATHS['bullet']).convert_alpha()
        scale_factor = 0.6
        self.bullet_surf = pygame.transform.scale(self.bullet_surf, (int(self.bullet_surf.get_width() * scale_factor), int(self.bullet_surf.get_height() * scale_factor)))

        # Load enemy frames
        self.enemy_frames = {}
        enemies_folder = IMAGE_PATHS['enemies']
        if not exists(enemies_folder):
            raise FileNotFoundError(f"Enemies folder not found: {enemies_folder}")

        for enemy_type in listdir(enemies_folder):
            enemy_path = join(enemies_folder, enemy_type)
            if isdir(enemy_path):
                self.enemy_frames[enemy_type] = []
                for file_name in sorted(listdir(enemy_path), key=lambda name: int(name.split('.')[0])):
                    full_path = join(enemy_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[enemy_type].append(surf)

    def setup(self):
        map = load_pygame(MAP_PATHS['world'])

        for x, y, image in map.get_layer_by_name('Ground').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)

        for obj in map.get_layer_by_name('Objects'):
            CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))

        for obj in map.get_layer_by_name('Collisions'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)

        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites)
                self.gun = Gun(self.player, self.all_sprites)
            else:
                self.spawn_positions.append((obj.x, obj.y))

    def input(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            self.shoot_sound.play()
            # Get the mouse position
            mouse_pos = pygame.mouse.get_pos()
            # Calculate the direction vector from the gun to the mouse
            direction = pygame.Vector2(mouse_pos[0] - WINDOW_WIDTH / 2, mouse_pos[1] - WINDOW_HEIGHT / 2).normalize()

            # Calculate the bullet's starting position at the tip of the gun
            gun_tip_offset = 40  # Adjust this value based on the gun's length
            bullet_start_pos = self.gun.rect.center + direction * gun_tip_offset

            # Spawn the bullet at the tip of the gun with the calculated direction
            Bullet(self.bullet_surf, bullet_start_pos, direction, [self.all_sprites, self.bullet_sprites])
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

    def gun_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= GUN_COOLDOWN:  # Use GUN_COOLDOWN from settings
                self.can_shoot = True

    def bullet_collision(self):
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                # Check collision with collision sprites (e.g., walls, objects)
                collision_sprites = pygame.sprite.spritecollide(bullet, self.collision_sprites, False, pygame.sprite.collide_mask)
                if collision_sprites:
                    self.impact_sound.play()
                    for sprite in collision_sprites:
                        if hasattr(sprite, 'destroy'):  # Check if the sprite has a destroy method
                            sprite.destroy()
                    bullet.kill()

                # Check collision with enemy sprites
                enemy_collisions = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if enemy_collisions:
                    self.impact_sound.play()
                    for enemy in enemy_collisions:
                        if hasattr(enemy, 'destroy'):  # Check if the enemy has a destroy method
                            enemy.destroy()
                    bullet.kill()

    def player_collision(self):
        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask):
            if self.player.take_damage():  # If damage is taken
                self.take_damage()  # Reduce health

    def draw_health_bar(self):
        # Calculate health bar width based on current health
        health_width = (self.player_health / MAX_HEALTH) * HEALTH_BAR_WIDTH

        # Draw health bar background
        pygame.draw.rect(self.display_surface, HEALTH_BAR_BG_COLOR, (*HEALTH_BAR_POS, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT))

        # Draw health bar foreground (current health) with gradient
        health_surface = pygame.Surface((health_width, HEALTH_BAR_HEIGHT))
        health_surface.fill(HEALTH_BAR_COLOR)
        self.display_surface.blit(health_surface, HEALTH_BAR_POS)

        # Draw health bar border
        border_rect = pygame.Rect(*HEALTH_BAR_POS, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT)
        pygame.draw.rect(self.display_surface, HEALTH_BAR_BORDER_COLOR, border_rect, HEALTH_BAR_BORDER_WIDTH)

        # Shake effect when hit
        if self.health_bar_shake_timer > 0:
            shake_offset = randint(-5, 5)
            self.display_surface.blit(self.display_surface, (shake_offset, 0))
            self.health_bar_shake_timer -= 1

    def draw_low_health_overlay(self):
        if self.player_health <= LOW_HEALTH_THRESHOLD:
            # Calculate the alpha value for the overlay using a sine wave
            self.low_health_pulse_alpha += LOW_HEALTH_OVERLAY_SPEED
            pulse_alpha = int((1 + math.sin(self.low_health_pulse_alpha)) * 127.5 + 127.5)
            
            # Clamp pulse_alpha to the valid range [0, 255]
            pulse_alpha = max(0, min(255, pulse_alpha))
            
            # Create a translucent red overlay
            overlay_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay_surface.fill((255, 0, 0, pulse_alpha))
            self.display_surface.blit(overlay_surface, (0, 0))

    def take_damage(self):
        if self.player_health > 0:
            self.player_health -= 1  # Reduce health by 1 hit
            self.health_bar_shake_timer = HEALTH_BAR_SHAKE_DURATION  # Start shake effect
            self.damage_flash_timer = DAMAGE_FLASH_DURATION  # Start damage flash effect

            # Check if player is dead
            if self.player_health <= 0:
                self.running = False  # End the game

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000

            # Event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == self.enemy_event:
                    Enemy(choice(self.spawn_positions), choice(list(self.enemy_frames.values())), (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites),

            # Update
            self.gun_timer()
            self.input()
            self.all_sprites.update(dt)
            self.bullet_collision()
            self.player_collision()

            # Draw
            self.display_surface.fill('black')
            self.all_sprites.draw(self.player.rect.center)
            self.draw_health_bar()  # Draw the health bar
            pygame.display.update()

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()