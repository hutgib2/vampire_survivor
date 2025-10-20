from settings import *
from weapons import Gun, PiercingGun, Shotgun, Machinegun, Lasergun, Sideshotgun, Knife, Flamegun
from homescreen import save_high_score
from projectiles import Orb, Mine
from enemies import Boss

PLAYER_SPEED = 350
ANIMATION_SPEED = 6
class Aura(pygame.sprite.Sprite):
    def __init__(self, groups, surf, player):
        super().__init__(groups)
        self.image = surf
        self.image.set_alpha(120)
        self.rect = self.image.get_frect(center = player.rect.center)
        self.player = player
        self.radius = 400
    def update(self, _):
        self.rect.center = self.player.rect.center

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, gun_surf, game):
        super().__init__(groups)
        self.load_images()
        self.image = pygame.image.load(join('..', 'images', 'player', 'down', '0.png')).convert_alpha()
        self.gun_surf = gun_surf
        self.rect = self.image.get_frect(center = pos)
        self.direction = pygame.math.Vector2()
        self.speed = PLAYER_SPEED
        self.animation_speed = ANIMATION_SPEED
        self.collision_sprites = collision_sprites
        self.hitbox_rect = self.rect.inflate(-60, -90)
        self.state, self.frame_index = 'right', 0
        self.lives = 3
        self.game = game
        self.gun = Gun(self.gun_surf, self, self.game.all_sprites, self.game)
        self.powerup_activated = None
        self.powerup_cooldown = 7000
        self.powerup_activation_time = 0
        self.aura = None
        self.minedrop_time = 0
        self.minedrop_cooldown = 500
        self.can_drop_mine = False

    def move(self, dt):
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.object_collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.object_collision('vertical')
        self.rect.center = self.hitbox_rect.center

    def object_collision(self, direction):
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
    
    def load_images(self):
        self.frames = {'left': [], 'right': [], 'up': [], 'down': []}
        for state in self.frames.keys():    # frames.keys() => ('left', 'right', 'up', 'down')
            for folder_path, sub_folders, file_names in walk(join('..', 'images', 'player', state)):
                if file_names:
                    for file_name in sorted(file_names, key= lambda name: int(name.split('.')[0])):
                        full_path = join(folder_path, file_name)
                        surf = pygame.image.load(full_path).convert_alpha()
                        self.frames[state].append(surf)

    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
        if self.direction:
            self.direction = self.direction.normalize()
    
    def animate(self, dt):
        if self.direction.x != 0:
            self.state = 'right' if self.direction.x > 0 else 'left'
        if self.direction.y != 0:
            self.state = 'down' if self.direction.y > 0 else 'up'
        self.frame_index = self.frame_index + self.animation_speed * dt if self.direction else 0
        self.image = self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])]
        if self.powerup_activated == 'shield':
            self.image.set_alpha(130)
        else:
            self.image.set_alpha(255)

    def enemy_collision(self):
        collision_sprites = pygame.sprite.spritecollide(self, self.game.enemy_sprites, False, pygame.sprite.collide_mask)
        for enemy in collision_sprites:
            if self.powerup_activated != 'shield':
                if type(enemy) == Orb:
                    enemy.kill()
                elif type(enemy) == Boss:
                    pass
                else:
                    enemy.destroy(True)
                self.game.impact_sound.play()
                self.lives -= 1
                if self.lives < 1:
                    if self.game.kill_count > self.game.high_score:
                        save_high_score(self.game.kill_count)
                    return True
        return False
    
    def powerup_timer(self):
        if self.powerup_activated != None:
            current_time = pygame.time.get_ticks()
            if current_time - self.powerup_activation_time >= self.powerup_cooldown:
                if self.powerup_activated == 'superspeed':
                    self.speed = PLAYER_SPEED
                    self.animation_speed = ANIMATION_SPEED
                elif self.powerup_activated == 'slowaura':
                    self.aura.kill()
                    self.aura = None
                elif self.powerup_activated == 'timestop':
                    pass
                elif self.powerup_activated == 'mine':
                    pass
                else:
                    self.gun.kill()
                    self.gun = Gun(self.gun_surf, self, self.game.all_sprites, self.game)
                self.powerup_activated = None

    def mine_timer(self):
        if self.powerup_activated == 'mine' and self.can_drop_mine:
            Mine(self.game.mine_surf, self.rect.center, self.game.all_sprites, self.game)
            self.minedrop_time = pygame.time.get_ticks()
            self.can_drop_mine = False
        elif pygame.time.get_ticks() - self.minedrop_time >= self.minedrop_cooldown:
            self.can_drop_mine = True

    def powerup_collision(self):
        powerup_collisions = pygame.sprite.spritecollide(self, self.game.powerup_sprites, True, pygame.sprite.collide_mask)
        for powerup in powerup_collisions:
            self.game.powerup_spawn_positions.append(powerup.rect.center)
            if powerup.type == 'life':
                if self.lives < 3:
                    self.lives += 1
                continue
            self.powerup_activation_time = pygame.time.get_ticks()
            self.powerup_activated = powerup.type
            if powerup.type == 'superspeed':
                self.speed = PLAYER_SPEED * 2
                self.animation_speed = ANIMATION_SPEED * 2
                continue
            if powerup.type == 'shield':
                return
            if powerup.type == 'slowaura':
                if self.aura != None:
                    self.aura.kill()
                self.aura = Aura(self.game.all_sprites, self.game.aura_surf, self)
                return
            if powerup.type == 'timestop':
                continue
            if powerup.type == 'mine':
                self.can_drop_mine = True
                continue
            self.gun.kill()
            if powerup.type == 'pierce':
                self.gun = PiercingGun(self.gun_surf, self, self.game.all_sprites, self.game)
            elif powerup.type == 'machinegun':
                self.gun = Machinegun(self.game.machinegun_surf, self, self.game.all_sprites, self.game)
            elif powerup.type == 'laser':
                self.gun = Lasergun(self.game.lasergun_surf, self, self.game.all_sprites, self.game)
            elif powerup.type == 'shotgun':
                self.gun = Shotgun(self.game.shotgun_surf, self, self.game.all_sprites, self.game)
            elif powerup.type == 'sideshot':
                self.gun = Sideshotgun(self.gun_surf, self, self.game.all_sprites, self.game)
            elif powerup.type == 'knife':
                self.gun = Knife(self.game.knife_surf, self, self.game.all_sprites, self.game)
            elif powerup.type == 'flamegun':
                self.gun = Flamegun(self.game.flamegun_surf, self, self.game.all_sprites, self.game)

    def explosion_collisions(self):
        collision_sprites = pygame.sprite.groupcollide(self.game.explosion_sprites, self.game.enemy_sprites, False, False, pygame.sprite.collide_mask)
        for explosion, enemies in collision_sprites.items():
            for enemy in enemies:
                if type(enemy) == Orb:
                    continue
                self.game.impact_sound.play()
                if type(enemy) == Boss:
                    explosion.kill()
                    enemy.lives -= 1
                    if enemy.lives > 0:
                        continue
                enemy.destroy(False)
                self.game.kill_count += 1

    def update(self, dt):
        self.input()
        self.move(dt)
        self.animate(dt)
        self.powerup_collision()
        self.powerup_timer()
        self.mine_timer()
        self.explosion_collisions()
