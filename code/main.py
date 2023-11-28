from __future__ import annotations
import pygame, sys
from abc import ABC
from enum import Enum

from settings import *
from level import Level

class Game: 
    '''Main game class.'''
    def __init__(self) -> None:
        '''Initialize the game.'''
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Candy Valley')
        self.clock = pygame.time.Clock()
        self.level = Level()

    def run(self):
        '''Main game loop.'''
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.level.save_game()
                    pygame.quit()
                    sys.exit()
            
            dt = self.clock.tick() / 1000
            self.level.run(dt)          
            

if __name__ == '__main__':
    game = Game()
    game.run()