from genericpath import exists, isdir
from os import listdir
from settings import *
from player import Player
from sprites import *
from pytmx.util_pygame import load_pygame
from groups import AllSprites

from random import randint, choice

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

        #gun timer
        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cool_down = 500

        #enemy timer
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 300)
        self.spawn_positions = []
        
        #audio
        self.shoot_sound = pygame.mixer.Sound(join('..', 'audio', 'shoot.wav'))
        self.shoot_sound.set_volume(0.4)
        self.impact_sound = pygame.mixer.Sound(join('..', 'audio', 'impact.ogg'))
        self.impact_sound.set_volume(0.1)
        self.music = pygame.mixer.Sound(join('..', 'audio', 'music.wav'))
        self.music.set_volume(0.1)
        self.music.play(-1)

        #setup 
        self.load_images()
        self.setup()    

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

    def load_images(self):
        self.bullet_surf = pygame.image.load(join('..', 'images', 'gun', 'bullet.png')).convert_alpha()
        # Scale down the bullet image 
        scale_factor = 0.6  # Adjust this value to make the bullet smaller or larger
        self.bullet_surf = pygame.transform.scale(self.bullet_surf, (int(self.bullet_surf.get_width() * scale_factor), int(self.bullet_surf.get_height() * scale_factor)))

        # Load enemy frames
        self.enemy_frames = {}
        enemies_folder = join('..', 'images', 'enemies')
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

        # Debug print to check loaded enemy frames
        print("Loaded enemy frames:", self.enemy_frames)
        


    def gun_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.gun_cool_down:
                self.can_shoot = True

    def setup(self):
        map = load_pygame(join('..', 'data', 'maps', 'world.tmx'))

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
            self.running = False

    def run(self):
        #dt
        while self.running:
            dt = self.clock.tick(60) / 1000

            #event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == self.enemy_event:
                    Enemy(choice(self.spawn_positions), choice(list(self.enemy_frames.values())), (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites),

            #update
            self.gun_timer()
            self.input()
            self.all_sprites.update(dt)
            self.bullet_collision()
            self.player_collision()

            #draw
            self.display_surface.fill('black')
            self.all_sprites.draw(self.player.rect.center)
            pygame.display.update()

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()  