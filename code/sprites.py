from settings import *
from math import atan2, degrees
# ('..', 'images', 'gun', 'bullet.png')
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

class Bullet(pygame.sprite.Sprite):
    def __init__(self, surf, pos, direction, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = pos) 
        self.spawn_time = pygame.time.get_ticks() # it stores the time when the bullet is created
        self.lifetime = 1000
        self.direction = direction
        self.speed = 1200
    
    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        # current_time - spawn_time = time elapsed since bullet was summoned
        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()

class Gun(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        self.player = player
        self.distance = 120
        self.player_direction = pygame.Vector2(1, -1)

        super().__init__(groups)
        self.gun_surf = pygame.transform.scale(pygame.image.load(join('..', 'images', 'gun', 'gun.png')), (100, 70)).convert_alpha()
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

class Powerup(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, player):
        super().__init__(groups)
        self.player = player
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.animation_speed = 6
        self.position_offset = [0, 1, 0, -1]
        self.frame_index = 0

    def update(self, dt):
        self.frame_index += self.animation_speed * dt
        self.rect.centery += self.position_offset[int(self.frame_index) % len(self.position_offset)]
        



class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, framedata, groups, player, collision_sprites):
        super().__init__(groups)
        self.player = player
        self.enemy_type = framedata[0]
        self.frames = framedata[1]
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.animation_speed = 6

        self.rect = self.image.get_frect(center = pos)
        self.hitbox_rect = self.rect.inflate(-20, -40)
        self.collision_sprites = collision_sprites
        self.direction = pygame.Vector2()
        self.speed = 250
        self.death_time = 0
        self.death_duration = 400

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]

    def move(self, dt):
        player_pos = pygame.Vector2(self.player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        self.direction = (player_pos - enemy_pos).normalize()
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        if self.enemy_type != 'bat':
            self.collisions('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        if self.enemy_type != 'bat':
            self.collisions('vertical')
        self.rect.center = self.hitbox_rect.center

    def collisions(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0:
                        self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0:
                        self.hitbox_rect.left = sprite.rect.right
                if direction == 'vertical':
                    if self.direction.y > 0:
                        self.hitbox_rect.bottom = sprite.rect.top
                    if self.direction.y < 0:
                        self.hitbox_rect.top = sprite.rect.bottom
    
    def set_mask_to_red(self):
       for x in range(self.image.get_width()):
           for y in range(self.image.get_height()):
               color = self.image.get_at((x, y))
               if color == (255, 255, 255):
                    self.image.set_at((x, y), (175, 0, 0))

    def destroy(self, hit_player):
        self.death_time = pygame.time.get_ticks()
        self.image = pygame.mask.from_surface(self.frames[0]).to_surface()
        self.image.set_colorkey('black')
        if hit_player:
            self.set_mask_to_red()

    def death_timer(self):
        if pygame.time.get_ticks() - self.death_time >= self.death_duration:
            self.kill()

    def update(self, dt):
        if self.death_time == 0:
            self.move(dt)
            self.animate(dt)
        else:
            self.death_timer()