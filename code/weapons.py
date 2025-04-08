from settings import *
from math import atan2, degrees

class Gun(pygame.sprite.Sprite):
    def __init__(self, surf, distance, player, groups):
        super().__init__(groups)
        self.player = player
        self.distance = distance
        self.player_direction = pygame.Vector2(1, -1)
        self.gun_surf = surf
        self.image = self.gun_surf
        self.rect = self.image.get_frect(center = self.player.rect.center + self.player_direction * self.distance)
    
    def get_direction(self):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        if mouse_pos - player_pos != 0:
            self.player_direction = (mouse_pos - player_pos).normalize()
        else:
            self.player_direction = 0
    
    def rotate_gun(self):
        angle = degrees(atan2(self.player_direction.x, self.player_direction.y)) - 90
        if self.player_direction.x > 0:
            self.image = pygame.transform.rotozoom(self.gun_surf, angle, 1)
        else:
            self.image = pygame.transform.rotozoom(self.gun_surf, abs(angle), 1)
            self.image = pygame.transform.flip(self.image, False, True)
    
    def update(self, _):
        self.get_direction()
        self.rotate_gun()
        self.rect.center = self.player.rect.center + (self.player_direction + pygame.Vector2(0, -0.2)) * self.distance