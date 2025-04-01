import pygame
from settings import *
from random import random, choice
import math

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, pos, powerup_type, groups):
        super().__init__(groups)
        self.powerup_type = powerup_type
        self.image = pygame.Surface((30, 30))
        self.image.fill(self.get_color())
        self.rect = self.image.get_rect(center=pos)
        self.float_y = self.rect.y
        self.float_speed = 0.5
        self.float_offset = 0
        
    def get_color(self):
        colors = {
            'speed': (255, 165, 0),    # Orange
            'damage': (255, 0, 0),     # Red
            'health': (0, 255, 0),     # Green
            'shield': (0, 255, 255),   # Cyan
            'rapid_fire': (255, 255, 0) # Yellow
        }
        return colors.get(self.powerup_type, (255, 255, 255))
    
    def apply_effect(self, player_stats):
        effects = {
            'speed': lambda: setattr(player_stats, 'speed', player_stats.speed * 1.5),
            'damage': lambda: setattr(player_stats, 'damage', player_stats.damage * 1.5),
            'health': lambda: setattr(player_stats, 'health', min(player_stats.health + 5, player_stats.max_health)),
            'shield': lambda: player_stats.add_powerup('shield', POWERUP_DURATION),
            'rapid_fire': lambda: player_stats.add_powerup('rapid_fire', POWERUP_DURATION)
        }
        effects[self.powerup_type]()
    
    def update(self, dt):
        # Floating animation
        self.float_offset += self.float_speed * dt
        self.float_y = self.rect.y + math.sin(self.float_offset) * 5
        self.rect.y = self.float_y

class PowerUpManager:
    def __init__(self, groups):
        self.groups = groups
        self.powerup_types = ['speed', 'damage', 'health', 'shield', 'rapid_fire']
    
    def spawn_powerup(self, pos):
        if random() < POWERUP_SPAWN_CHANCE:
            powerup_type = choice(self.powerup_types)
            PowerUp(pos, powerup_type, self.groups)
    
    def update(self, dt):
        for sprite in self.groups[0]:
            if isinstance(sprite, PowerUp):
                sprite.update(dt) 