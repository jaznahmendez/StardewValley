from __future__ import annotations
import pygame, sys
from abc import ABC
from enum import Enum

from settings import *
from level import Level
#NEXT TO DO IS RESTARTING THE DAY
#https://www.youtube.com/watch?v=T4IX36sP_0c
#OTHER TO DOs:
#CHANGE THE TYPE OF STUMP
#RESIZE TREEES
#RESIZE TREES COLLISION SIZES
#RESIZE FLOWERS
#CHANGE GROUND TO CANDYS

class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Stardew Valley Demo')
        self.clock = pygame.time.Clock()
        self.level = Level()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            dt = self.clock.tick() / 1000
            self.level.run(dt)
            pygame.display.update()

if __name__ == '__main__':
    game = Game()
    game.run()