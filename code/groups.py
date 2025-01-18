from settings import *

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def draw(self, surface):
        for sprite in self:
            surface.blit(sprite.image, sprite.rect)
            