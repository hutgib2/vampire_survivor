from settings import *
from math import atan2, degrees
from sprites import Bullet

class Gun(pygame.sprite.Sprite):
    def __init__(self, surf, distance, player, groups, game):
        super().__init__(groups)
        self.player = player
        self.distance = distance
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
    
    def rotate_gun(self):
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
    
    def timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.cooldown:
                self.can_shoot = True
    
    def update(self, _):
        self.get_direction()
        self.rotate_gun()
        self.rect.center = self.player.rect.center + (self.player_direction + pygame.Vector2(0, -0.2)) * self.distance
        self.timer()
        self.shoot()

            # if self.shotgun_activated:
            #     Bullet(self.bullet_surf, pos, self.gun.player_direction.rotate(45), (self.all_sprites, self.bullet_sprites))
            #     Bullet(self.bullet_surf, pos, self.gun.player_direction.rotate(-45), (self.all_sprites, self.bullet_sprites))
            # if self.sideshot_activated:
            #     Bullet(self.bullet_surf, pos, self.gun.player_direction.rotate(90), (self.all_sprites, self.bullet_sprites))
            #     Bullet(self.bullet_surf, pos, self.gun.player_direction.rotate(-90), (self.all_sprites, self.bullet_sprites))
            #     Bullet(self.bullet_surf, pos, self.gun.player_direction.rotate(180), (self.all_sprites, self.bullet_sprites))