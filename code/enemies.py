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
        if self.player.aura != None and (player_pos - enemy_pos).length() <= self.player.aura.radius:
            self.hitbox_rect.x += self.direction.x * self.speed * dt / 2
        else:
            self.hitbox_rect.x += self.direction.x * self.speed * dt
        if self.type != 'bat':
            self.collisions('horizontal')
        if self.player.aura != None and (player_pos - enemy_pos).length() <= self.player.aura.radius:
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

BOSS_SPEED = 175

class Boss(pygame.sprite.Sprite):
    def __init__(self, pos, player, game):
        super().__init__(game.all_sprites, game.enemy_sprites)
        self.load_images()
        self.game = game
        self.lives = 25
        self.player = player
        self.type = 'boss'
        self.animation_speed = 9
        self.position_offset = [0, 1, 0, -1]
        self.frame_index = 0
        self.state = 'right'
        self.can_shoot = True
        self.shoot_time = 0
        self.orb_cooldown = 500
        self.attack_cooldown = 3000
        self.attack_time = 0
        self.can_attack = False
        self.image = self.walk_frames['down'][0]
        self.rect = self.image.get_frect(center = pos)
        self.direction = pygame.Vector2()
        self.speed = BOSS_SPEED
        self.death_time = 0
        self.death_duration = 400
    
    def load_images(self):
        self.walk_frames = {'left': [], 'right': [], 'up': [], 'down': []}
        for state in self.walk_frames.keys():    # frames.keys() => ('left', 'right', 'up', 'down')
            for folder_path, sub_folders, file_names in walk(join('..', 'images', 'boss', 'walk', state)):
                if file_names:
                    for file_name in sorted(file_names, key= lambda name: int(name.split('.')[0])):
                        full_path = join(folder_path, file_name)
                        surf = pygame.transform.scale(pygame.image.load(full_path), (320, 320)).convert_alpha()
                        self.walk_frames[state].append(surf)

        self.attack_frames = {'left': [], 'right': [], 'up': [], 'down': []}
        for state in self.attack_frames.keys():    # frames.keys() => ('left', 'right', 'up', 'down')
            for folder_path, sub_folders, file_names in walk(join('..', 'images', 'boss', 'attack', state)):
                if file_names:
                    for file_name in sorted(file_names, key= lambda name: int(name.split('.')[0])):
                        full_path = join(folder_path, file_name)
                        surf = pygame.transform.scale(pygame.image.load(full_path), (320, 320)).convert_alpha()
                        self.attack_frames[state].append(surf)

    def loop_frames(self, frames, dt):
        self.statex = 'right' if self.direction.x > 0 else 'left'
        self.statey = 'down' if self.direction.y > 0 else 'up'
        self.state = self.statex if abs(self.direction.x) > abs(self.direction.y) else self.statey
        self.frame_index = self.frame_index + self.animation_speed * dt if self.direction else 0
        self.image = frames[self.state][int(self.frame_index) % len(frames[self.state])] 

    def animate(self, dt):
        if self.can_attack:
            self.speed = 0
            self.loop_frames(self.attack_frames, dt)
        else:
            self.speed = BOSS_SPEED
            self.loop_frames(self.walk_frames, dt)

    def attack_timer(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.attack_time >= self.attack_cooldown:
            self.can_attack = not self.can_attack
            self.attack_time = current_time

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
        if self.can_shoot and self.can_attack:
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
            self.attack_timer()
            self.move(dt)
            self.animate(dt)
        else:
            self.death_timer()