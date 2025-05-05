from settings import *
from projectiles import Orb
class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, framedata, player, collision_sprites, game):
        super().__init__(game.all_sprites, game.enemy_sprites)
        self.game = game
        self.player = player
        self.type = framedata[0]
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
        if self.player.aura != None and (player_pos - enemy_pos).length() <= 300:
            self.hitbox_rect.x += self.direction.x * self.speed * dt / 2
        else:
            self.hitbox_rect.x += self.direction.x * self.speed * dt
        if self.type != 'bat':
            self.collisions('horizontal')
        if self.player.aura != None and (player_pos - enemy_pos).length() <= 300:
            self.hitbox_rect.y += self.direction.y * self.speed * dt / 2
        else:
            self.hitbox_rect.y += self.direction.y * self.speed * dt
        if self.type != 'bat':
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
        self.game.enemy_sprites.remove(self)
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

class Boss(pygame.sprite.Sprite):
    def __init__(self, pos, surf, player, game):
        super().__init__(game.all_sprites, game.enemy_sprites)
        self.game = game
        self.lives = 25
        self.player = player
        self.image = surf
        self.type = 'boss'
        self.animation_speed = 6
        self.position_offset = [0, 1, 0, -1]
        self.frame_index = 0
        self.can_shoot = True
        self.shoot_time = 0
        self.orb_cooldown = 1000
        self.rect = self.image.get_frect(center = pos)
        self.direction = pygame.Vector2()
        self.speed = 150
        self.death_time = 0
        self.death_duration = 400

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        self.rect.centery += self.position_offset[int(self.frame_index) % len(self.position_offset)]       

    def move(self, dt):
        player_pos = pygame.Vector2(self.player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        self.direction = (player_pos - enemy_pos).normalize()
        self.rect.center += self.direction * self.speed * dt
    
    def set_mask_to_red(self):
       for x in range(self.image.get_width()):
           for y in range(self.image.get_height()):
               color = self.image.get_at((x, y))
               if color == (255, 255, 255):
                    self.image.set_at((x, y), (175, 0, 0))

    def shoot(self):
        if self.can_shoot:
            self.game.shoot_sound.play()
            Orb(self.game.orb_surf, self.rect.center, (pygame.math.Vector2(self.player.rect.center) - (pygame.math.Vector2(self.rect.center))).normalize(), (self.game.all_sprites, self.game.enemy_sprites))
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()
    
    def shoot_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.orb_cooldown:
                self.can_shoot = True

    def destroy(self, hit_player):
        self.game.enemy_sprites.remove(self)
        self.death_time = pygame.time.get_ticks()
        self.image = pygame.mask.from_surface(self.image).to_surface()
        self.image.set_colorkey('black')
        if hit_player:
            self.set_mask_to_red()

    def death_timer(self):
        if pygame.time.get_ticks() - self.death_time >= self.death_duration:
            self.kill()

    def update(self, dt):
        if self.death_time == 0:
            self.shoot()
            self.shoot_timer()
            self.move(dt)
            self.animate(dt)
        else:
            self.death_timer()