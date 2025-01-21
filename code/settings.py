import pygame
from os.path import join
from os import walk
import math

# Window Settings
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
TILE_SIZE = 64

# Health Bar Settings
HEALTH_BAR_WIDTH = 400
HEALTH_BAR_HEIGHT = 30
HEALTH_BAR_POS = (50, 50)  # Position of the health bar
HEALTH_BAR_COLOR = (255, 0, 0)  # Red for health
HEALTH_BAR_BG_COLOR = (50, 50, 50)  # Dark gray for background
HEALTH_BAR_BORDER_COLOR = (255, 255, 255)  # White border
HEALTH_BAR_BORDER_WIDTH = 3  # Border thickness
MAX_HEALTH = 10  # Player can take 10 hits

# Animation Settings
LOW_HEALTH_OVERLAY_SPEED = 0.02  # Speed of the low-health overlay pulse
DAMAGE_FLASH_DURATION = 100  # Duration of the red flash in milliseconds
HEALTH_BAR_SHAKE_DURATION = 100  # Duration of the shake effect in milliseconds
LOW_HEALTH_THRESHOLD = 3  # Health threshold for low health effects
LOW_HEALTH_PULSE_SPEED = 0.02  # Speed of the pulse effect

# Player Settings
PLAYER_SPEED = 500  # Player movement speed

# Invincibility and Blinking Settings
IFRAME_DURATION = 2000  # 2 seconds of invincibility
BLINK_INTERVAL = 200  # Blink every 200 milliseconds

# Gun Settings
GUN_COOLDOWN = 400  # Cooldown between shots in milliseconds
GUN_TIP_OFFSET = 40  # Offset for bullet spawn position
BULLET_SPEED = 1200  # Speed of bullets
BULLET_LIFETIME = 1000  # Lifetime of bullets in milliseconds

# Enemy Settings
ENEMY_SPEED = 100  # Movement speed of enemies
ENEMY_SPAWN_INTERVAL = 500  # Time between enemy spawns in milliseconds
ENEMY_DEATH_DURATION = 500  # Time before enemy disappears after death

# Audio Settings
AUDIO_VOLUME = 0.2  # Default volume for audio
MUSIC_VOLUME = 0.2  # Volume for background music
IMPACT_VOLUME = 0.2  # Volume for impact sound

# File Paths
IMAGE_PATHS = {
    'bullet': join('..', 'images', 'gun', 'bullet.png'),
    'gun': join('..', 'images', 'gun', 'gun.png'),
    'player': {
        'up': join('..', 'images', 'player', 'up'),
        'down': join('..', 'images', 'player', 'down'),
        'left': join('..', 'images', 'player', 'left'),
        'right': join('..', 'images', 'player', 'right'),
    },
    'enemies': join('..', 'images', 'enemies'),
}

AUDIO_PATHS = {
    'shoot': join('..', 'audio', 'shoot.wav'),
    'impact': join('..', 'audio', 'impact.ogg'),
    'music': join('..', 'audio', 'music.wav'),
}

MAP_PATHS = {
    'world': join('..', 'data', 'maps', 'world.tmx'),
}