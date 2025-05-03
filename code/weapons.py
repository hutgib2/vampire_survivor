from settings import *
from math import atan2, degrees
from projectiles import Bullet, Laser

class Gun(pygame.sprite.Sprite):
    def __init__(self, surf, player, groups, game):
        super().__init__(groups)
        self.player = player
        self.distance = 120
        self.game = game
        self.player_direction = pygame.Vector2(1, -1)
        self.gun_surf = surf
        self.image = self.gun_surf
        self.rect = self.image.get_frect(center = self.player.rect.center + self.player_direction * self.distance)
        self.can_shoot = True
        self.shoot_time = 0
        self.cooldown = 250
    
    def get_direction(self):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        if mouse_pos - player_pos != 0:
            self.player_direction = (mouse_pos - player_pos).normalize()
        else:
            self.player_direction = 0
    
    def rotate(self):
        angle = degrees(atan2(self.player_direction.x, self.player_direction.y)) - 90
        if self.player_direction.x > 0:
            self.image = pygame.transform.rotozoom(self.gun_surf, angle, 1)
        else:
            self.image = pygame.transform.rotozoom(self.gun_surf, abs(angle), 1)
            self.image = pygame.transform.flip(self.image, False, True)

    def shoot(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            self.game.shoot_sound.play()
            pos = self.rect.center + self.player_direction * 50
            Bullet(self.game.bullet_surf, pos, self.player_direction, (self.game.all_sprites, self.game.bullet_sprites))
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()
    
    def shoot_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.cooldown:
                self.can_shoot = True
    
    def bullet_collision(self):
        collision_sprites = pygame.sprite.groupcollide(self.game.bullet_sprites, self.game.enemy_sprites, True, False, pygame.sprite.collide_mask)
        for bullet, enemies in collision_sprites.items():
            for enemy in enemies:
                if enemy.type != 'orb':
                    self.game.impact_sound.play()
                    if enemy.type != 'boss':
                        enemy.destroy(False)
                        self.game.kill_count += 1
                        break
                    else:
                        enemy.lives -= 1
                        if enemy.lives <= 0:
                            enemy.destroy(False)
                            self.game.kill_count += 1

    def update(self, _):
        self.get_direction()
        self.rotate()
        self.rect.center = self.player.rect.center + (self.player_direction + pygame.Vector2(0, -0.2)) * self.distance
        self.shoot_timer()
        self.shoot()
        self.bullet_collision()

class PiercingGun(Gun):
    def bullet_collision(self):
        collision_sprites = pygame.sprite.groupcollide(self.game.bullet_sprites, self.game.enemy_sprites, False, False, pygame.sprite.collide_mask)
        for bullet, enemies in collision_sprites.items():
            for enemy in enemies:
                self.game.impact_sound.play()
                enemy.destroy(False)
                self.game.kill_count += 1
                break

class Shotgun(Gun):        
    def shoot(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            self.game.shoot_sound.play()
            pos = self.rect.center + self.player_direction * 64
            Bullet(self.game.bullet_surf, pos, self.player_direction, (self.game.all_sprites, self.game.bullet_sprites))
            Bullet(self.game.bullet_surf, pos, self.player_direction.rotate(45), (self.game.all_sprites, self.game.bullet_sprites))
            Bullet(self.game.bullet_surf, pos, self.player_direction.rotate(-45), (self.game.all_sprites, self.game.bullet_sprites))
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

class Sideshotgun(Gun):
    def shoot(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            self.game.shoot_sound.play()
            pos = self.rect.center + self.player_direction * 64
            Bullet(self.game.bullet_surf, pos, self.player_direction, (self.game.all_sprites, self.game.bullet_sprites))
            Bullet(self.game.bullet_surf, pos, self.player_direction.rotate(90), (self.game.all_sprites, self.game.bullet_sprites))
            Bullet(self.game.bullet_surf, pos, self.player_direction.rotate(-90), (self.game.all_sprites, self.game.bullet_sprites))
            Bullet(self.game.bullet_surf, pos, self.player_direction.rotate(180), (self.game.all_sprites, self.game.bullet_sprites))
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

class Machinegun(Gun):
    def __init__(self, surf, player, groups, game):
        super().__init__(surf, player, groups, game)
        self.cooldown = 125

class Lasergun(Gun):
    def bullet_collision(self):
        collision_sprites = pygame.sprite.groupcollide(self.game.bullet_sprites, self.game.enemy_sprites, False, False, pygame.sprite.collide_mask)
        for bullet, enemies in collision_sprites.items():
            for enemy in enemies:
                self.game.impact_sound.play()
                if type(enemy) == Enemy:
                    enemy.destroy(False)
                if type(bullet) == Bullet:
                    bullet.kill()
                    Laser(self.game.laser_surf, enemy.rect.center, bullet.direction, (self.game.all_sprites, self.game.bullet_sprites))
                self.game.kill_count += 1
                break

class Knife(Gun):
    def __init__(self, surf, player, groups, game):
        super().__init__(surf, player, groups, game)
        self.distance = 150

    def knife_collision(self):
        collision_sprites = pygame.sprite.spritecollide(self, self.game.enemy_sprites, False, pygame.sprite.collide_mask)
        for enemy in collision_sprites:
            if enemy.death_time == 0:
                self.game.impact_sound.play()
                enemy.destroy(False)
                self.game.kill_count += 1

    def update(self, _):
        self.get_direction()
        self.rotate()
        self.rect.center = self.player.rect.center + (self.player_direction + pygame.Vector2(0, -0.33)) * self.distance
        self.knife_collision()