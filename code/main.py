from __future__ import annotations
import pygame, sys
from abc import ABC
from enum import Enum

from settings import *
from level import Level

#MEMENTO - missing soil logic

class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Candy Valley')
        self.clock = pygame.time.Clock()
        self.level = Level()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.level.save_game()
                    pygame.quit()
                    sys.exit()

            dt = self.clock.tick() / 1000
            self.level.run(dt)          
            pygame.display.update()

if __name__ == '__main__':
    game = Game()
    game.run()