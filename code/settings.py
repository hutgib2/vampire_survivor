import pygame 
from os.path import join 
from os import walk

pygame.init()
display_surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

pygame.display.set_caption("Vampire Survivor")
WINDOW_WIDTH, WINDOW_HEIGHT = display_surface.get_size()

TILE_SIZE = 64