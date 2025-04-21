from settings import *  # import everything from settings.py
from player import Player
from sprites import *
from random import randint, choice
from pytmx.util_pygame import load_pygame
from groups import AllSprites
from homescreen import *
from enemies import Enemy, Boss

class Game:
    def __init__(self, display_surface): # Constructor 
        self.display_surface = display_surface
        self.running = True
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(join('..', 'images', 'Oxanium-Bold.ttf'), 40)
        self.kill_count = 0
        self.high_score = load_high_score()
        # groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.powerup_sprites = pygame.sprite.Group()
        self.laser_sprites = pygame.sprite.Group()
        self.orb_sprites = pygame.sprite.Group()
        #events
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 300)
        self.powerup_event = pygame.event.custom_type()
        pygame.time.set_timer(self.powerup_event, 15000)
        self.boss_event = pygame.event.custom_type()
        pygame.time.set_timer(self.boss_event, 10000)
        self.enemy_spawn_positions = []
        self.powerup_spawn_positions = []
        #audio
        self.shoot_sound = pygame.mixer.Sound(join('..', 'audio', 'shoot.wav'))
        self.shoot_sound.set_volume(0.2)
        self.impact_sound = pygame.mixer.Sound(join('..', 'audio', 'new_impact.ogg'))
        self.impact_sound.set_volume(0.3)
        self.music = pygame.mixer.Sound(join('..', 'audio', 'my_first_mashup.wav'))
        self.music.set_volume(0.55)
        self.music.play(loops = 0)

    def load_map(self):
        map = load_pygame(join('..', 'data', 'maps', 'world.tmx'))
        for x, y, image in map.get_layer_by_name('Ground').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)
        for obj in map.get_layer_by_name('Objects'):
            CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))
        for collision in map.get_layer_by_name('Collisions'):
            CollisionSprite((collision.x, collision.y), pygame.Surface((collision.width, collision.height)), self.collision_sprites)
        for marker in map.get_layer_by_name('Entities'):
            if marker.name == 'Player':
                self.player = Player((marker.x, marker.y), self.all_sprites, self.collision_sprites, self.gun_surf, self)
            elif marker.name == 'Power up':
                self.powerup_spawn_positions.append((marker.x, marker.y))
            else:
                self.enemy_spawn_positions.append((marker.x, marker.y))
    
    def load_images(self):
        self.life_surf = pygame.transform.scale(pygame.image.load(join('..', 'images', 'powerups', 'life.png')), (75, 75)).convert_alpha()
        self.pierce_surf = pygame.transform.scale(pygame.image.load(join('..', 'images', 'powerups', 'pierce.png')), (75, 75)).convert_alpha()
        self.machinegun_surf = pygame.transform.scale(pygame.image.load(join('..', 'images', 'powerups', 'machinegun.png')), (125, 60)).convert_alpha()
        self.lasergun_surf = pygame.transform.scale(pygame.image.load(join('..', 'images', 'powerups', 'lasergun.png')), (100, 75)).convert_alpha()
        self.lasergun_surf = pygame.transform.flip(self.lasergun_surf, True, False)
        self.laser_surf = pygame.transform.scale(pygame.image.load(join('..', 'images', 'powerups', 'laserbeam.png')), (WINDOW_WIDTH, 75)).convert_alpha()
        self.shotgun_surf = pygame.transform.scale(pygame.image.load(join('..', 'images', 'powerups', 'shotgun.png')), (150, 40)).convert_alpha()
        self.gun_surf = pygame.transform.scale(pygame.image.load(join('..', 'images', 'gun', 'gun.png')), (100, 54)).convert_alpha()
        self.knife_surf = pygame.transform.scale(pygame.image.load(join('..', 'images', 'powerups', 'knife.png')), (150, 50)).convert_alpha()
        self.superspeed_surf = pygame.transform.scale(pygame.image.load(join('..', 'images', 'powerups', 'superspeed.png')), (81, 81)).convert_alpha()
        self.shield_surf = pygame.transform.scale(pygame.image.load(join('..', 'images', 'powerups', 'shield.png')), (81, 81)).convert_alpha()
        self.bullet_surf = pygame.transform.scale(pygame.image.load(join('..', 'images', 'gun', 'bullet.png')), (25, 25)).convert_alpha()
        self.boss_surf = pygame.transform.scale(pygame.image.load(join('..', 'images', 'enemies', 'vampire.png')), (144, 288)).convert_alpha()
        self.orb_surf = pygame.transform.scale(pygame.image.load(join('..', 'images', 'enemies', 'orb.png')), (52, 52)).convert_alpha()
        
        self.powerup_surfaces = {
                                'life':self.life_surf, 
                                'pierce':self.pierce_surf, 
                                'machinegun':self.machinegun_surf, 
                                'laser':self.lasergun_surf, 
                                'shotgun':self.shotgun_surf, 
                                'sideshot':self.gun_surf, 
                                'knife':self.knife_surf, 
                                'superspeed':self.superspeed_surf,
                                'shield':self.shield_surf
                                }
        
        folders = list(walk(join('..', 'images', 'enemies')))[0][1]
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join('..', 'images', 'enemies', folder)):
                self.enemy_frames[folder] = []
                for file_name in sorted(file_names, key = lambda name: int(name.split('.')[0])):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[folder].append(surf)
            
    def load_data(self):
        self.load_images()
        self.load_map()

    def get_spawn_position(self, spawn_positions):
        distance_from_player = 0
        while distance_from_player < 700:
            pos = choice(spawn_positions)
            distance_from_player = pygame.math.Vector2.magnitude(pygame.math.Vector2(pos) - pygame.math.Vector2(self.player.rect.center))
        return pos  
    
    def display_score(self):
        self.text_surf = self.font.render(str(self.kill_count), True, 'gray25')
        self.text_rect = self.text_surf.get_frect(topleft = (300, 25))
        self.display_surface.blit(self.text_surf, self.text_rect)
        pygame.draw.rect(self.display_surface, 'gray25', self.text_rect.inflate(20, 10).move(0, -6), 5, 10)

    def display_lives(self):
        for i in range(self.player.lives):
            self.life_rect = self.life_surf.get_frect(topleft = (10 + (i * 85), 10))
            self.display_surface.blit(self.life_surf, self.life_rect)
        
    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == self.enemy_event:
                    Enemy(self.get_spawn_position(self.enemy_spawn_positions), choice(list(self.enemy_frames.items())), self.player, self.collision_sprites, self)
                if event.type == self.boss_event:
                    Boss(self.get_spawn_position(self.enemy_spawn_positions), self.boss_surf, self.player, self)
                if event.type == self.powerup_event and len(self.powerup_spawn_positions) - 1 > 0:
                    Powerup(self.powerup_spawn_positions.pop(randint(0, len(self.powerup_spawn_positions) - 1)), choice(list(self.powerup_surfaces.items())), (self.all_sprites, self.powerup_sprites), self.player)
            self.all_sprites.update(dt)
            game_over = self.player.enemy_collision()
            if game_over:
                self.music.stop()
                return True
            self.all_sprites.draw(self.player.rect.center)
            self.display_score()
            self.display_lives()
            pygame.display.update()

if __name__ == '__main__':
    pygame.init()
    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Vampire Survivor")
    home_screen_image = pygame.transform.scale(pygame.image.load(join('..', 'images', 'home_screen.png')), (WINDOW_WIDTH, WINDOW_HEIGHT))
    game_over_screen = pygame.transform.scale(pygame.image.load(join('..', 'images', 'game_over.png')), (WINDOW_WIDTH, WINDOW_HEIGHT))
    homescreen = HomeScreen(display_surface, home_screen_image)
    is_running = homescreen.wait()
    while is_running:
        game = Game(display_surface)
        game.load_data()
        is_running = game.run()
        if is_running:
            homescreen = HomeScreen(display_surface, game_over_screen)
            is_running = homescreen.wait()
    pygame.quit()