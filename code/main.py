from settings import *
from player import Player
from sprites import *
from pytmx.util_pygame import load_pygame
from groups import AllSprites

from random import randint

class Game:
    def __init__(self):
        # Setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Survivor Shooter')
        self.clock = pygame.time.Clock()
        self.running = True
        self.load_images()

        # Groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()

        self.setup()

        #gun timer
        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cool_down = 100

    def input(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            # Get the mouse position
            mouse_pos = pygame.mouse.get_pos()
            # Calculate the direction vector from the gun to the mouse
            direction = pygame.Vector2(mouse_pos[0] - WINDOW_WIDTH / 2, mouse_pos[1] - WINDOW_HEIGHT / 2).normalize()
            
            # Calculate the bullet's starting position at the tip of the gun
            gun_tip_offset = 60  # Adjust this value based on the gun's length
            bullet_start_pos = self.gun.rect.center + direction * gun_tip_offset
            
            # Spawn the bullet at the tip of the gun with the calculated direction
            Bullet(self.bullet_surf, bullet_start_pos, direction, [self.all_sprites, self.bullet_sprites])
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

    def load_images(self):
        self.bullet_surf = pygame.image.load(join('..', 'images', 'gun', 'bullet.png')).convert_alpha()

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

    def run(self):
        #dt
        while self.running:
            dt = self.clock.tick(60) / 1000

            #event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            #update
            self.gun_timer()
            self.input()
            self.all_sprites.update(dt)

            #draw
            self.display_surface.fill('black')
            self.all_sprites.draw(self.player.rect.center)
            pygame.display.update()

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()  