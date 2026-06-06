import asyncio
import pygame 
from os.path import join 
from os import walk

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Vampire Survivor")

WINDOW_WIDTH, WINDOW_HEIGHT = screen.get_size()
TILE_SIZE = 64