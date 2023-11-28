import pygame
from settings import *
from support import FolderImportProxy
from random import randint, choice
from sprites import Generic

class Sky:
    '''Class for the sky.'''
    def __init__(self):
        '''Initializes the sky.'''
        self.display_surface = pygame.display.get_surface()
        self.full_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.start_color = [255, 255, 255]
        self.end_color = (38, 101, 189)
        
    def display(self, dt):
        '''Displays the sky.'''
        for index, value in enumerate(self.end_color):
            if self.start_color[index] > value:
                self.start_color[index] -= dt
                
            if self.start_color[index] < value:
                self.start_color[index] += 2*dt
                
        self.full_surf.fill(self.start_color)
        self.display_surface.blit(self.full_surf, (0,0), special_flags = pygame.BLEND_RGBA_MULT)

class Drop(Generic):
    '''Class for rain drops.'''
    def __init__(self, surf, pos, moving, groups, z):
        '''Initializes the rain drops.'''
        super().__init__(pos, surf, groups, z)
        self.lifetime = randint(400, 500)
        self.start_time = pygame.time.get_ticks()
        
        self.moving = moving
        if self.moving:
            self.pos = pygame.math.Vector2(self.rect.topleft)
            self.direction = pygame.math.Vector2(-2,4)
            self.speed = randint(200,250)
            
    def update(self,dt):
        '''Updates the rain drops.'''
        if self.moving:
            self.pos += self.direction * self.speed * dt
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))
            
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()

class Rain:
    '''Class for the rain.'''
    def __init__(self, all_sprites):
        '''Initializes the rain.'''
        self.loader_proxy = FolderImportProxy()
        self.all_sprites = all_sprites  
        self.rain_drops = self.loader_proxy.import_folder('graphics/rain/drops/')
        self.rain_floor = self.loader_proxy.import_folder('graphics/rain/floor/')
        self.floor_w, self.floor_h = pygame.image.load('graphics/world/ground.png').get_size()
        
    def create_floor(self):
        '''Creates the rain floor.'''
        Drop(surf = choice(self.rain_floor), 
             pos = (randint(0,self.floor_w),randint(0,self.floor_h)), 
             moving = False, 
             groups = self.all_sprites,
             z = LAYERS['rain floor'])
        
    def create_drops(self):
        '''Creates the rain drops.'''
        Drop(surf = choice(self.rain_drops), 
             pos = (randint(0,self.floor_w),randint(0,self.floor_h)), 
             moving = True, 
             groups = self.all_sprites,
             z = LAYERS['rain drops'])
    
    def update(self):
        '''Updates the rain.'''
        self.create_floor()
        self.create_drops()