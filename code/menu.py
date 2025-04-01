import pygame
from settings import *

class Button:
    def __init__(self, text, pos, size, color=(50, 50, 50), hover_color=(100, 100, 100)):
        self.text = text
        self.pos = pos
        self.size = size
        self.color = color
        self.hover_color = hover_color
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        self.font = pygame.font.Font(None, 36)
        self.is_hovered = False
        
    def draw(self, surface):
        # Draw a more visible button
        color = self.hover_color if self.is_hovered else self.color
        # Draw button background
        pygame.draw.rect(surface, color, self.rect)
        # Draw button outline
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)
        
        # Draw button text
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class Menu:
    def __init__(self, game):
        self.game = game
        self.buttons = []
        self.font = pygame.font.Font(None, 48)
        
    def create_main_menu(self):
        self.buttons = [
            Button("Start Game", (WINDOW_WIDTH//2 - 100, 300), (200, 50)),
            Button("Options", (WINDOW_WIDTH//2 - 100, 370), (200, 50)),
            Button("Quit", (WINDOW_WIDTH//2 - 100, 440), (200, 50))
        ]
    
    def create_pause_menu(self):
        self.buttons = [
            Button("Resume", (WINDOW_WIDTH//2 - 100, 300), (200, 50)),
            Button("Options", (WINDOW_WIDTH//2 - 100, 370), (200, 50)),
            Button("Quit to Menu", (WINDOW_WIDTH//2 - 100, 440), (200, 50))
        ]
    
    def create_game_over_menu(self, stats):
        self.buttons = [
            Button("Play Again", (WINDOW_WIDTH//2 - 100, 300), (200, 50)),
            Button("Main Menu", (WINDOW_WIDTH//2 - 100, 370), (200, 50)),
            Button("Quit", (WINDOW_WIDTH//2 - 100, 440), (200, 50))
        ]
        self.stats = stats
    
    def draw(self, surface):
        # Draw title
        title = self.font.render("Vampire Survivor", True, (255, 255, 255))
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 200))
        surface.blit(title, title_rect)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(surface)
        
        # Draw game over stats if applicable
        if hasattr(self, 'stats'):
            stats_text = [
                f"Time Survived: {int(self.stats.time_survived)}s",
                f"Kills: {self.stats.kills}",
                f"Level Reached: {self.stats.level}",
                f"Achievements Unlocked: {sum(1 for x in self.stats.achievements.values() if x)}"
            ]
            
            for i, text in enumerate(stats_text):
                stat_surf = self.font.render(text, True, (255, 255, 255))
                stat_rect = stat_surf.get_rect(center=(WINDOW_WIDTH//2, 500 + i * 40))
                surface.blit(stat_surf, stat_rect)
    
    def handle_event(self, event):
        for button in self.buttons:
            if button.handle_event(event):
                if button.text == "Start Game":
                    self.game.start_game()
                elif button.text == "Resume":
                    self.game.resume_game()
                elif button.text == "Play Again":
                    self.game.reset_game()
                elif button.text == "Main Menu":
                    self.game.show_main_menu()
                elif button.text == "Quit":
                    self.game.quit_game()
                elif button.text == "Options":
                    self.game.show_options() 