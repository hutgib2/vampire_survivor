from settings import *  # import everything from settings.py
from player import Player
from sprites import *
from random import randint, choice
from pytmx.util_pygame import load_pygame
from groups import AllSprites

class Game:
    def __init__(self, display_surface): # Constructor 
        self.display_surface = display_surface
        self.running = True
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(join('..', 'images', 'Oxanium-Bold.ttf'), 40)
        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cooldown = 250
        self.kill_count = 0
        self.high_score = load_high_score()

        # groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.powerup_sprites = pygame.sprite.Group()

        #powerups
        self.powerup_count = 0

        #events
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 300)
        self.powerup_event = pygame.event.custom_type()
        pygame.time.set_timer(self.powerup_event, 10000)
        self.enemy_spawn_positions = []
        self.powerup_spawn_positions = []

        #audio
        self.shoot_sound = pygame.mixer.Sound(join('..', 'audio', 'shoot.wav'))
        self.shoot_sound.set_volume(0.2)
        self.impact_sound = pygame.mixer.Sound(join('..', 'audio', 'new_impact.ogg'))
        self.impact_sound.set_volume(0.3)
        self.music = pygame.mixer.Sound(join('..', 'audio', 'my_first_mashup.wav'))
        self.music.set_volume(0.55)
        self.music.play(loops = 1)
        
        self.load_images()
        self.setup()

    def setup(self):
        map = load_pygame(join('..', 'data', 'maps', 'world.tmx'))
        for x, y, image in map.get_layer_by_name('Ground').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)

        for obj in map.get_layer_by_name('Objects'):
            CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))

        for collision in map.get_layer_by_name('Collisions'):
            CollisionSprite((collision.x, collision.y), pygame.Surface((collision.width, collision.height)), self.collision_sprites)

        for marker in map.get_layer_by_name('Entities'):
            if marker.name == 'Player':
                self.player = Player((marker.x, marker.y), self.all_sprites, self.collision_sprites)
                self.gun = Gun(self.player, self.all_sprites)
            elif marker.name == 'Power up':
                self.powerup_spawn_positions.append((marker.x, marker.y))
            else:
                self.enemy_spawn_positions.append((marker.x, marker.y))
    
    def load_images(self):
        self.life_surf = pygame.transform.scale(pygame.image.load(join('..', 'images', 'life.png')), (75, 75)).convert_alpha()
        
        self.powerup_surface = {'life':self.life_surf}

        self.bullet_surf = pygame.transform.scale(pygame.image.load(join('..', 'images', 'gun', 'bullet.png')), (25, 25)).convert_alpha()
        folders = list(walk(join('..', 'images', 'enemies')))[0][1]
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join('..', 'images', 'enemies', folder)):
                self.enemy_frames[folder] = []
                for file_name in sorted(file_names, key = lambda name: int(name.split('.')[0])):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[folder].append(surf)

    def input(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            self.shoot_sound.play()
            pos = self.gun.rect.center + self.gun.player_direction * 50
            Bullet(self.bullet_surf, pos, self.gun.player_direction, (self.all_sprites, self.bullet_sprites))
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

    def gun_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True
    
    def bullet_collision(self):
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                collision_sprites = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                for enemy in collision_sprites:
                    if enemy.death_time == 0:
                        self.impact_sound.play()
                        enemy.destroy(False)
                        bullet.kill()
                        self.kill_count += 1

    def player_collision(self):
        collision_sprites = pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask)
        for enemy in collision_sprites:
            if enemy.death_time == 0:
                enemy.destroy(True)
                self.impact_sound.play()
                self.player.lives -= 1
                if self.player.lives < 1:
                    if self.kill_count > self.high_score:
                        save_high_score(self.kill_count)
                    return True
        return False
    
    def powerup_collision(self):
        collision_sprites = pygame.sprite.spritecollide(self.player, self.powerup_sprites, True, pygame.sprite.collide_mask)
        for powerup in collision_sprites:
            if self.player.lives < 3:
                self.player.lives += 1

    #def powerup_timer(self):
        #


    def get_spawn_position(self, spawn_positions):
        distance_from_player = 0
        while distance_from_player < 700:
            pos = choice(spawn_positions)
            distance_from_player = pygame.math.Vector2.magnitude(pygame.math.Vector2(pos) - pygame.math.Vector2(self.player.rect.center))
        return pos
    
    def get_powerup_spawn_positions(self, spawn_positions):
        distance_from_powerup = 0
        valid_pos = False
        while not valid_pos:
            pos = choice(spawn_positions)
            valid_pos = True
            if (not self.powerup_sprites):
                break
            for powerup in powerup_sprites:
                distance_from_powerup = pygame.math.Vector2.magnitude(pygame.math.Vector2(pos) - pygame.math.Vector2(powerup.rect.center))
                if distance_from_powerup < 100:
                    valid_pos = False
        return pos

    def display_score(self):
        self.text_surf = self.font.render(str(self.kill_count), True, 'gray25')
        self.text_rect = self.text_surf.get_frect(topleft = (300, 25))
        self.display_surface.blit(self.text_surf, self.text_rect)
        pygame.draw.rect(self.display_surface, 'gray25', self.text_rect.inflate(20, 10).move(0, -6), 5, 10)

    def display_lives(self):
        for i in range(self.player.lives):
            self.life_rect = self.life_surf.get_frect(topleft = (10 + (i*85), 10))
            self.display_surface.blit(self.life_surf, self.life_rect)
        

    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == self.enemy_event:
                    Enemy(self.get_spawn_position(self.enemy_spawn_positions), choice(list(self.enemy_frames.items())), (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites)
                if event.type == self.powerup_event:
                    Powerup(self.get_powerup_spawn_position(self.powerup_spawn_positions), choice(list(self.powerup_surfaces.items())), (self.all_sprites, self.powerup_sprites), self.player)
            self.gun_timer()
            self.input()
            self.all_sprites.update(dt)
            self.bullet_collision()
            self.powerup_collision()
            if self.player_collision():
                self.music.stop()
                return True
            self.all_sprites.draw(self.player.rect.center)
            self.display_score()
            self.display_lives()
            pygame.display.update()

def load_high_score():
    with open(join('..', 'data', 'high_score.txt'), 'r') as file:
        content = file.read()
        highscore = int(content.split("=")[1])
        
        return highscore

def save_high_score(current_score):
    with open(join('..', 'data', 'high_score.txt'), 'w') as file:
        file.write('highscore=' + str(current_score))

class HomeScreen:
    def __init__(self, display_surface, background):
        self.high_score = load_high_score()
        self.waiting = True
        self.display_surface = display_surface
        self.background = background
        self.font = pygame.font.Font(join('..', 'images', 'Oxanium-Bold.ttf'), 40)

        # Draw homescreen
        self.display_surface.blit(background, (0, 0))
        self.display_high_score()
        pygame.display.update()


    def display_high_score(self):
        self.text_surf = self.font.render('high score = ' +str(self.high_score), True, 'gray25')
        self.text_rect = self.text_surf.get_frect(midbottom = (WINDOW_WIDTH / 2 - 180 ,WINDOW_HEIGHT - 180))
        self.display_surface.blit(self.text_surf, self.text_rect)

    def wait(self):
        while self.waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return True
                if event.type == pygame.QUIT:
                    return False

if __name__ == '__main__':
    # loop between creating homescreen and game objects
    # this will reset the games memory each time so we can start clean
    pygame.init()
    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Vampire Survivor")
    home_screen_image = pygame.transform.scale(pygame.image.load(join('..', 'images', 'home_screen.png')), (WINDOW_WIDTH, WINDOW_HEIGHT))
    game_over_screen = pygame.transform.scale(pygame.image.load(join('..', 'images', 'game_over.png')), (WINDOW_WIDTH, WINDOW_HEIGHT))
    homescreen = HomeScreen(display_surface, home_screen_image)
    is_running = homescreen.wait()
    while is_running:
        game = Game(display_surface)
        is_running = game.run()
        if is_running:
            homescreen = HomeScreen(display_surface, game_over_screen)
            is_running = homescreen.wait()
    pygame.quit()