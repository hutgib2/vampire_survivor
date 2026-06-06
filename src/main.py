import pygame
from game.homescreen import HomeScreen
import asyncio

async def main():
    homescreen = HomeScreen()
    await homescreen.run()
    
asyncio.run(main())