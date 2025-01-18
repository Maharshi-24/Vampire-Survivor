from settings import *
from player import Player
from sprites import *

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
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()

        # Sprites
        self.player = Player((400, 300), self.all_sprites, self.collision_sprites)
        for i in range(6):
            x, y = randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)
            w, h = randint(60, 100), randint(10, 100)
            CollisionSprite((x, y), (w, h), [self.all_sprites, self.collision_sprites])  # Add to both groups

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