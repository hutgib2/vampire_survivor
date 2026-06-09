import asyncio
import pygame 
from os.path import join 
from os import walk

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Vampire Survivor")

WINDOW_WIDTH, WINDOW_HEIGHT = screen.get_size()
TILE_SIZE = 64

life_surf = pygame.transform.scale(pygame.image.load(join('assets', 'images', 'powerups', 'life.png')), (75, 75)).convert_alpha()
pierce_surf = pygame.transform.scale(pygame.image.load(join('assets', 'images', 'powerups', 'pierce.png')), (75, 75)).convert_alpha()
machinegun_surf = pygame.transform.scale(pygame.image.load(join('assets', 'images', 'powerups', 'machinegun.png')), (125, 60)).convert_alpha()
lasergun_surf = pygame.transform.scale(pygame.image.load(join('assets', 'images', 'powerups', 'lasergun.png')), (100, 75)).convert_alpha()
lasergun_surf = pygame.transform.flip(lasergun_surf, True, False)
laser_surf = pygame.transform.scale(pygame.image.load(join('assets', 'images', 'powerups', 'laserbeam.png')), (WINDOW_WIDTH, 75)).convert_alpha()
shotgun_surf = pygame.transform.scale(pygame.image.load(join('assets', 'images', 'powerups', 'shotgun.png')), (150, 40)).convert_alpha()
gun_surf = pygame.transform.scale(pygame.image.load(join('assets', 'images', 'gun', 'gun.png')), (100, 54)).convert_alpha()
knife_surf = pygame.transform.scale(pygame.image.load(join('assets', 'images', 'powerups', 'knife.png')), (150, 50)).convert_alpha()
superspeed_surf = pygame.transform.scale(pygame.image.load(join('assets', 'images', 'powerups', 'superspeed.png')), (81, 81)).convert_alpha()
shield_surf = pygame.transform.scale(pygame.image.load(join('assets', 'images', 'powerups', 'shield.png')), (81, 81)).convert_alpha()
slow_surf = pygame.transform.scale(pygame.image.load(join('assets', 'images', 'powerups', 'snail.png')), (96, 96)).convert_alpha()
aura_surf = pygame.transform.scale(pygame.image.load(join('assets', 'images', 'powerups', 'aura.png')), (800, 800)).convert_alpha()
timestop_surf = pygame.transform.scale(pygame.image.load(join('assets', 'images', 'powerups', 'clock.png')), (83, 99)).convert_alpha()
flamegun_surf = pygame.transform.scale(pygame.image.load(join('assets', 'images', 'powerups', 'flamegun.png')), (100, 75)).convert_alpha()
mine_surf = pygame.transform.scale(pygame.image.load(join('assets', 'images', 'powerups', 'mine.png')), (92, 42)).convert_alpha()
bullet_surf = pygame.transform.scale(pygame.image.load(join('assets', 'images', 'gun', 'bullet.png')), (25, 25)).convert_alpha()
orb_surf = pygame.transform.scale(pygame.image.load(join('assets', 'images', 'enemies', 'orb.png')), (52, 52)).convert_alpha()

POWERUP_SURFS = {
					'life':life_surf, 
					'pierce':pierce_surf, 
					'machinegun':machinegun_surf, 
					'laser':lasergun_surf, 
					'shotgun':shotgun_surf, 
					'sideshot':gun_surf, 
					'knife':knife_surf, 
					'superspeed':superspeed_surf,
					'shield':shield_surf,
					'slowaura': slow_surf,
					'timestop': timestop_surf,
					'flamegun': flamegun_surf,
					'mine': mine_surf
				}

enemy_frames = {}
for folder in list(walk(join('assets', 'images', 'enemies')))[0][1]:
	for folder_path, _, file_names in walk(join('assets', 'images', 'enemies', folder)):
		enemy_frames[folder] = []
		for file_name in sorted(file_names, key = lambda name: int(name.split('.')[0])):
			full_path = join(folder_path, file_name)
			surf = pygame.image.load(full_path).convert_alpha()
			enemy_frames[folder].append(surf)

flame_frames = []
for folder_path, _, file_names in walk(join('assets', 'images', 'powerups', 'flame')):
	for file_name in sorted(file_names, key = lambda name: int(name.split('.')[0])):
		full_path = join(folder_path, file_name)
		surf = pygame.transform.scale(pygame.image.load(full_path), (100, 100)).convert_alpha()
		flame_frames.append(surf)

explosion_frames = []
for folder_path, _, file_names in walk(join('assets', 'images', 'powerups', 'explosion')):
	for file_name in sorted(file_names, key = lambda name: int(name.split('.')[0])):
		full_path = join(folder_path, file_name)
		surf = pygame.transform.scale(pygame.image.load(full_path), (100, 100)).convert_alpha()
		explosion_frames.append(surf)

ANIMATIONS = {
	enemy: enemy_frames,
	flame: flame_frames,
	explosion: explosion_frames,
}