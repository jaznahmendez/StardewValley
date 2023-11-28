import pygame

class Timer:
    '''Timer class for handling timed events.'''
    def __init__(self, duration, func = None):
        '''Initialize the timer.'''
        self.duration = duration
        self.func = func
        self.start_time = 0
        self.active = False
    
    def activate(self):
        '''Activate the timer.'''
        self.active = True
        self.start_time = pygame.time.get_ticks()

    def deactivate(self):
        '''Deactivate the timer.'''
        self.active = False
        self.start_time = 0

    def update(self):
        '''Update the timer.'''
        current_time = pygame.time.get_ticks()
        if self.active and current_time - self.start_time >= self.duration:
            if self.func and self.start_time != 0:
                self.func()
            self.deactivate()