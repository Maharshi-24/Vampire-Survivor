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
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))  # Fixed typo: 'display' -> 'display_surface'
        pygame.display.set_caption('Survivor Shooter')
        self.clock = pygame.time.Clock()
        self.running = True

        # Groups

        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()

        self.setup()

        # Sprites
        self.player = Player((500, 300), self.all_sprites, self.collision_sprites)


    def setup(self):
        map = load_pygame(join('..', 'data', 'maps', 'world.tmx'))        

        for x,y, image in map.get_layer_by_name('Ground').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)
        
        for obj in map.get_layer_by_name('Objects'):
            CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))

        for obj in map.get_layer_by_name('Collisions'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)



    def run(self):
        while self.running:
            # Delta time
            dt = self.clock.tick(60) / 1000  # Cap frame rate to 60 FPS

            # Event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Update
            self.all_sprites.update(dt)

            # Draw
            self.display_surface.fill('black')  # Clear the screen
            self.all_sprites.draw(self.display_surface)
            pygame.display.update()

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()