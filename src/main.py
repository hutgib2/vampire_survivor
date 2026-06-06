# /// script
# dependencies = [
#   "pytmx",
# ]
# ///

import asyncio
import pygame
from game.homescreen import HomeScreen

async def main():
    print('CREATING HOMESCREEN')
    homescreen = HomeScreen()
    await homescreen.run()
    
asyncio.run(main())