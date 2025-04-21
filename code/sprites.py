from settings import *
from math import atan2, degrees

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)
        self.ground = True

class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)

class Powerup(pygame.sprite.Sprite):
    def __init__(self, pos, powerup, groups, player):
        super().__init__(groups)
        self.player = player
        self.type = powerup[0]
        self.image = powerup[1]
        self.rect = self.image.get_frect(center = pos)

        self.animation_speed = 6
        self.position_offset = [0, 1, 0, -1]
        self.frame_index = 0

    def update(self, dt):
        self.frame_index += self.animation_speed * dt
        self.rect.centery += self.position_offset[int(self.frame_index) % len(self.position_offset)]        