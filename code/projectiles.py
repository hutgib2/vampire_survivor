from settings import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, surf, pos, direction, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = pos) 
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 1000
        self.direction = direction
        self.speed = 1200
    
    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()

class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, orientation, groups):
        super().__init__(groups)
        self.angle = orientation.angle_to(pygame.math.Vector2(0, 1))
        self.image = pygame.transform.rotate(surf, self.angle)
        self.rect = self.image.get_frect(center = pos)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 50
        self.direction = pygame.math.Vector2(0,0)
    
    def update(self, dt):
        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()

class Flame(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.image = frames[0]
        self.rect = self.image.get_frect(center = pos)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 1000
        self.frames = frames
        self.frame_index = 0
        self.animation_speed = 15

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]
    
    def update(self, dt):
        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()
        self.animate(dt)

class Orb(pygame.sprite.Sprite):
    def __init__(self, surf, pos, direction, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = pos) 
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 5000
        self.direction = direction
        self.speed = 500
        self.type = 'orb'
    
    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()