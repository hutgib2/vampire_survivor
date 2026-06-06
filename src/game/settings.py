import pygame 
from os.path import join 
from os import walk

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WINDOW_WIDTH, WINDOW_HEIGHT = screen.get_size()
TILE_SIZE = 64