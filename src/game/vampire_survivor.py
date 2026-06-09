from game.settings import *  # import everything from settings.py
from game.player import Player
from game.sprites import *
from game.groups import AllSprites
from game.enemies import Enemy, Boss
from game.homescreen import *
from game.timer import Timer
from random import randint, choice
from pytmx.util_pygame import load_pygame

class Game:
    def __init__(self): # Constructor 
        self.running = True
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(join('assets', 'images', 'Oxanium-Bold.ttf'), 40)
        self.kill_count = 0
        # self.high_score = load_high_score()

        # groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.powerup_sprites = pygame.sprite.Group()
        self.laser_sprites = pygame.sprite.Group()
        self.orb_sprites = pygame.sprite.Group()
        self.explosion_sprites = pygame.sprite.Group()
        
        #events
        # need to stop enemy event when time_stop powerup activated
        self.enemy_event_timer = Timer(400, lambda:Enemy(self.get_spawn_position(self.enemy_spawn_positions), choice(list(self.enemy_frames.items())), self.player, self.collision_sprites, self), repeat=True, autostart=True)
        self.powerup_event_timer = Timer(15000, lambda:Powerup(self.powerup_spawn_positions.pop(randint(0, len(self.powerup_spawn_positions) - 1)), choice(list(self.powerup_surfaces.items())), (self.all_sprites, self.powerup_sprites), self.player), repeat=True, autostart=True)
        self.boss_event_timer = Timer(60000, lambda:Boss(self.get_spawn_position(self.enemy_spawn_positions), self.player, self), repeat=True, autostart=True)
        self.enemy_spawn_positions = []
        self.powerup_spawn_positions = []
        
        #audio
        self.shoot_sound = pygame.mixer.Sound(join('assets', 'audio', 'shoot.ogg'))
        self.shoot_sound.set_volume(0.2)
        self.impact_sound = pygame.mixer.Sound(join('assets', 'audio', 'new_impact.ogg'))
        self.impact_sound.set_volume(0.3)
        self.music = pygame.mixer.Sound(join('assets', 'audio', 'my_first_mashup.ogg'))
        self.music.set_volume(0.55)
        self.music.play(loops = 0)

        self.load_map()

    def load_map(self):
        map = load_pygame(join('assets', 'data', 'maps', 'world.tmx'))
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

    def get_spawn_position(self, spawn_positions):
        distance_from_player = 0
        while distance_from_player < 700:
            pos = choice(spawn_positions)
            distance_from_player = pygame.math.Vector2.magnitude(pygame.math.Vector2(pos) - pygame.math.Vector2(self.player.rect.center))
        return pos  
    
    def display_score(self):
        self.text_surf = self.font.render(str(self.kill_count), True, 'gray25')
        self.text_rect = self.text_surf.get_frect(topleft = (300, 25))
        screen.blit(self.text_surf, self.text_rect)
        pygame.draw.rect(screen, 'gray25', self.text_rect.inflate(20, 10).move(0, -6), 5, 10)

    def display_lives(self):
        for i in range(self.player.lives):
            self.life_rect = self.life_surf.get_frect(topleft = (10 + (i * 85), 10))
            screen.blit(self.life_surf, self.life_rect)
        
    async def run(self):
        while self.running:
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
            self.all_sprites.update(dt)
            game_over = self.player.enemy_collision()
            if game_over:
                self.music.stop()
                return True
            self.all_sprites.draw(self.player.rect.center)
            self.display_score()
            self.display_lives()
            self.enemy_event_timer.update()
            self.powerup_event_timer.update()
            self.boss_event_timer.update()
            pygame.display.update()