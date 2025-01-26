import pygame
from settings import *

class GameOverMenu:
    def __init__(self, game):
        self.game = game
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 50)
        self.buttons = []
        self.selected_button = 0
        self.menu_active = True

        # Button setup
        self.buttons.append(self.create_button("Retry", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.buttons.append(self.create_button("Quit", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100))

    def create_button(self, text, x, y):
        # Create a button with text and a rectangle
        button_text = self.small_font.render(text, True, (255, 255, 255))
        button_rect = button_text.get_rect(center=(x, y))
        return {'text': text, 'text_surf': button_text, 'rect': button_rect, 'hovered': False}

    def draw(self):
        # Draw a semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Dark semi-transparent background
        self.display_surface.blit(overlay, (0, 0))

        # Draw game over text
        game_over_text = self.font.render("Game Over", True, (255, 255, 255))
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
        self.display_surface.blit(game_over_text, game_over_rect)

        # Draw buttons
        for button in self.buttons:
            color = (200, 200, 200) if button['hovered'] else (255, 255, 255)  # Hover effect
            button_text = self.small_font.render(button['text'], True, color)
            button_rect = button_text.get_rect(center=button['rect'].center)
            self.display_surface.blit(button_text, button_rect)

            # Draw a border around the button
            border_rect = button_rect.inflate(20, 10)  # Make the border slightly larger than the text
            pygame.draw.rect(self.display_surface, color, border_rect, 2)

    def handle_input(self):
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button['hovered'] = button['rect'].collidepoint(mouse_pos)  # Check if mouse is over the button

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.buttons[0]['rect'].collidepoint(mouse_pos):  # Retry button
                    self.game.reset_game()
                    self.menu_active = False
                elif self.buttons[1]['rect'].collidepoint(mouse_pos):  # Quit button
                    pygame.quit()
                    exit()

    def update(self):
        self.handle_input()
        self.draw()