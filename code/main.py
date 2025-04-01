from genericpath import exists, isdir
from os import listdir
from settings import *
from player import Player
from sprites import *
from pytmx.util_pygame import load_pygame
from groups import AllSprites
from random import randint, choice
import math
from game_over import GameOverMenu
from player_stats import PlayerStats
from powerups import PowerUpManager
from menu import Menu

class Game:
    def __init__(self):
        # Setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Vampire Survivor')
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.paused = False
        
        # Game state
        self.current_state = 'menu'  # menu, playing, paused, game_over
        
        # Groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.powerup_sprites = pygame.sprite.Group()
        
        # Game systems
        self.player_stats = PlayerStats()
        self.powerup_manager = PowerUpManager([self.all_sprites, self.powerup_sprites])
        self.menu = Menu(self)
        self.menu.create_main_menu()  # Initialize the main menu
        
        # Timers
        self.can_shoot = True
        self.shoot_time = 0
        self.game_start_time = 0
        
        # Enemy timer
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, ENEMY_SPAWN_INTERVAL)
        self.spawn_positions = []
        
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
        
    def start_game(self):
        self.current_state = 'playing'
        self.game_start_time = pygame.time.get_ticks()
        self.reset_game()
        
    def resume_game(self):
        self.current_state = 'playing'
        self.paused = False
        
    def reset_game(self):
        self.game_over = False
        self.all_sprites.empty()
        self.collision_sprites.empty()
        self.bullet_sprites.empty()
        self.enemy_sprites.empty()
        self.powerup_sprites.empty()
        self.player_stats = PlayerStats()
        self.setup()
        
    def show_main_menu(self):
        self.current_state = 'menu'
        self.menu.create_main_menu()
        
    def show_options(self):
        # TODO: Implement options menu
        pass
        
    def quit_game(self):
        self.running = False
        
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
                
    def load_images(self):
        # Load bullet image
        self.bullet_surf = pygame.image.load(IMAGE_PATHS['bullet']).convert_alpha()
        scale_factor = 0.6
        self.bullet_surf = pygame.transform.scale(self.bullet_surf, 
            (int(self.bullet_surf.get_width() * scale_factor), 
             int(self.bullet_surf.get_height() * scale_factor)))
        
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
                    
    def input(self):
        # Get all events first before processing
        events = pygame.event.get()
        
        # Process events for menu if in menu state
        if self.current_state in ['menu', 'paused', 'game_over']:
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.menu.handle_event(event)
        else:  # Playing state
            if self.current_state == 'playing':
                if pygame.mouse.get_pressed()[0] and self.can_shoot:
                    self.shoot_sound.play()
                    mouse_pos = pygame.mouse.get_pos()
                    direction = pygame.Vector2(mouse_pos[0] - WINDOW_WIDTH / 2, mouse_pos[1] - WINDOW_HEIGHT / 2).normalize()
                    
                    gun_tip_offset = 40
                    bullet_start_pos = self.gun.rect.center + direction * gun_tip_offset
                    
                    Bullet(self.bullet_surf, bullet_start_pos, direction, [self.all_sprites, self.bullet_sprites])
                    self.can_shoot = False
                    self.shoot_time = pygame.time.get_ticks()
            
            # Process other events for gameplay
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.current_state == 'playing':
                            self.current_state = 'paused'
                            self.menu.create_pause_menu()
                        elif self.current_state == 'paused':
                            self.resume_game()
                elif event.type == self.enemy_event and self.current_state == 'playing':
                    Enemy(choice(self.spawn_positions), choice(list(self.enemy_frames.values())), 
                        (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites)
                
    def update(self, dt):
        if self.current_state == 'playing':
            self.gun_timer()
            self.all_sprites.update(dt)
            self.bullet_collision()
            self.player_collision()
            self.powerup_manager.update(dt)
            self.player_stats.update_powerups()
            
            # Update game time
            self.player_stats.time_survived = (pygame.time.get_ticks() - self.game_start_time) / 1000
            
    def bullet_collision(self):
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                # Check collision with collision sprites
                collision_sprites = pygame.sprite.spritecollide(bullet, self.collision_sprites, False, pygame.sprite.collide_mask)
                if collision_sprites:
                    self.impact_sound.play()
                    for sprite in collision_sprites:
                        if hasattr(sprite, 'destroy'):
                            sprite.destroy()
                    bullet.kill()
                    
                # Check collision with enemy sprites
                enemy_collisions = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if enemy_collisions:
                    self.impact_sound.play()
                    for enemy in enemy_collisions:
                        if hasattr(enemy, 'destroy'):
                            enemy.destroy()
                            self.player_stats.kills += 1
                            self.powerup_manager.spawn_powerup(enemy.rect.center)
                            if self.player_stats.kills == 1:
                                self.player_stats.unlock_achievement('first_blood')
                            if self.player_stats.kills >= 100:
                                self.player_stats.unlock_achievement('marksman')
                    bullet.kill()
                    
                # Check collision with power-ups
                powerup_collisions = pygame.sprite.spritecollide(bullet, self.powerup_sprites, False)
                if powerup_collisions:
                    for powerup in powerup_collisions:
                        powerup.apply_effect(self.player_stats)
                        powerup.kill()
                        
    def player_collision(self):
        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask):
            if self.player.take_damage():
                self.take_damage()
                
    def take_damage(self):
        if self.player_stats.health > 0:
            self.player_stats.health -= 1
            self.health_bar_shake_timer = HEALTH_BAR_SHAKE_DURATION
            self.damage_flash_timer = DAMAGE_FLASH_DURATION
            
            if self.player_stats.health <= 0:
                self.game_over = True
                self.current_state = 'game_over'
                self.menu.create_game_over_menu(self.player_stats)
                
    def draw(self):
        # Always fill the background with black
        self.display_surface.fill('black')
        
        if self.current_state == 'playing':
            self.all_sprites.draw(self.player.rect.center)
            self.draw_health_bar()
            self.draw_low_health_overlay()
            self.player_stats.draw(self.display_surface)
        elif self.current_state in ['menu', 'paused', 'game_over']:
            # Draw a semi-transparent background for menu
            if self.current_state == 'paused':
                # If paused, show game in background
                self.all_sprites.draw(self.player.rect.center)
                # Add a dark overlay
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                overlay.set_alpha(150)
                overlay.fill((0, 0, 0))
                self.display_surface.blit(overlay, (0, 0))
            
            # Draw the menu
            self.menu.draw(self.display_surface)
            
        pygame.display.update()
        
    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000
            
            self.input()
            self.update(dt)
            self.draw()
            
        pygame.quit()
        
    def draw_health_bar(self):
        # Calculate health bar width based on current health
        health_width = (self.player_stats.health / self.player_stats.max_health) * HEALTH_BAR_WIDTH
        
        # Draw health bar background
        pygame.draw.rect(self.display_surface, HEALTH_BAR_BG_COLOR, 
                        (*HEALTH_BAR_POS, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT))
        
        # Draw health bar foreground (current health)
        health_surface = pygame.Surface((health_width, HEALTH_BAR_HEIGHT))
        health_surface.fill(HEALTH_BAR_COLOR)
        self.display_surface.blit(health_surface, HEALTH_BAR_POS)
        
        # Draw health bar border
        border_rect = pygame.Rect(*HEALTH_BAR_POS, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT)
        pygame.draw.rect(self.display_surface, HEALTH_BAR_BORDER_COLOR, 
                        border_rect, HEALTH_BAR_BORDER_WIDTH)
        
        # Shake effect when hit
        if hasattr(self, 'health_bar_shake_timer') and self.health_bar_shake_timer > 0:
            shake_offset = randint(-5, 5)
            self.display_surface.blit(self.display_surface, (shake_offset, 0))
            self.health_bar_shake_timer -= 1
            
    def draw_low_health_overlay(self):
        if self.player_stats.health <= LOW_HEALTH_THRESHOLD:
            # Calculate the alpha value for the overlay using a sine wave
            if not hasattr(self, 'low_health_pulse_alpha'):
                self.low_health_pulse_alpha = 0
            self.low_health_pulse_alpha += LOW_HEALTH_OVERLAY_SPEED
            pulse_alpha = int((1 + math.sin(self.low_health_pulse_alpha)) * 127.5 + 127.5)
            
            # Clamp pulse_alpha to the valid range [0, 255]
            pulse_alpha = max(0, min(255, pulse_alpha))
            
            # Reduce the alpha value to make the overlay more translucent
            pulse_alpha = int(pulse_alpha * 0.5)
            
            # Create a translucent red overlay
            overlay_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay_surface.fill((255, 0, 0, pulse_alpha))
            self.display_surface.blit(overlay_surface, (0, 0))
        
    def gun_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= GUN_COOLDOWN:
                self.can_shoot = True
                
if __name__ == '__main__':
    game = Game()
    game.run()