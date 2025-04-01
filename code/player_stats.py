import pygame
from settings import *

class PlayerStats:
    def __init__(self):
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = BASE_XP_REQUIREMENT
        
        # Base stats
        self.health = BASE_PLAYER_HEALTH
        self.max_health = BASE_PLAYER_HEALTH
        self.damage = BASE_PLAYER_DAMAGE
        self.speed = BASE_PLAYER_SPEED
        
        # Active power-ups
        self.active_powerups = {}
        
        # Achievement tracking
        self.achievements = {key: False for key in ACHIEVEMENTS.keys()}
        self.kills = 0
        self.time_survived = 0
        
        # UI elements
        self.font = pygame.font.Font(None, 36)
        self.xp_bar_rect = pygame.Rect(50, 90, 400, 20)
        
    def add_xp(self, amount):
        self.xp += amount
        while self.xp >= self.xp_to_next_level and self.level < MAX_LEVEL:
            self.level_up()
    
    def level_up(self):
        self.level += 1
        self.xp -= self.xp_to_next_level
        self.xp_to_next_level = int(BASE_XP_REQUIREMENT * (XP_SCALING_FACTOR ** (self.level - 1)))
        
        # Increase stats
        self.max_health += HEALTH_GROWTH
        self.health = self.max_health
        self.damage += DAMAGE_GROWTH
        self.speed += SPEED_GROWTH
        
        # Check for level-based achievements
        if self.level >= 10:
            self.unlock_achievement('speed_demon')
    
    def add_powerup(self, powerup_type, duration):
        self.active_powerups[powerup_type] = {
            'duration': duration,
            'start_time': pygame.time.get_ticks()
        }
    
    def update_powerups(self):
        current_time = pygame.time.get_ticks()
        expired_powerups = []
        
        for powerup_type, data in self.active_powerups.items():
            if current_time - data['start_time'] >= data['duration']:
                expired_powerups.append(powerup_type)
        
        for powerup_type in expired_powerups:
            del self.active_powerups[powerup_type]
    
    def unlock_achievement(self, achievement_id):
        if not self.achievements[achievement_id]:
            self.achievements[achievement_id] = True
            self.add_xp(ACHIEVEMENTS[achievement_id]['xp_reward'])
    
    def draw(self, surface):
        # Draw XP bar
        pygame.draw.rect(surface, (50, 50, 50), self.xp_bar_rect)
        xp_progress = self.xp / self.xp_to_next_level
        xp_width = int(self.xp_bar_rect.width * xp_progress)
        pygame.draw.rect(surface, UI_COLORS['xp_bar'], 
                        (self.xp_bar_rect.x, self.xp_bar_rect.y, xp_width, self.xp_bar_rect.height))
        
        # Draw level text
        level_text = f"Level {self.level}"
        level_surf = self.font.render(level_text, True, UI_COLORS['level_text'])
        surface.blit(level_surf, (self.xp_bar_rect.right + 10, self.xp_bar_rect.y))
        
        # Draw active power-ups
        y_offset = 120
        for powerup_type in self.active_powerups:
            remaining_time = int((self.active_powerups[powerup_type]['duration'] - 
                (pygame.time.get_ticks() - self.active_powerups[powerup_type]['start_time'])) / 1000)
            powerup_text = f"{powerup_type.title()}: {remaining_time}s"
            powerup_surf = self.font.render(powerup_text, True, UI_COLORS['powerup_active'])
            surface.blit(powerup_surf, (50, y_offset))
            y_offset += 30 