from settings import *
import pygame

class Game:
    def __init__(self):
        pygame.init()
        self.display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Survivor Shooter')
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):  # Add self as the first parameter
        while self.running:
            #delta time
            dt = self.clock.tick(60) / 1000

            #eventloop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False            

            #update

            #draw
            pygame.display.update()

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()