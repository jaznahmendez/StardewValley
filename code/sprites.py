from random import randint, choice
from timer import Timer
import pygame
from settings import *

class ObjectFactory:
    '''Factory class for creating objects'''
    @staticmethod
    def create_object(type, *args, **kwargs):
        '''Create an object of type'''
        if type == "Generic":
            return Generic(*args, **kwargs)
        elif type == "Interaction":
            return Interaction(*args, **kwargs)
        elif type == "Water":
            return Water(*args, **kwargs)
        elif type == "CandySunflower":
            return CandySunflower(*args, **kwargs)
        elif type == "Particle":
            return Particle(*args, **kwargs)
        elif type == "Tree":
            return Tree(*args, **kwargs)
        else:
            raise ValueError(f"Unknown type: {type}")
        
class Generic(pygame.sprite.Sprite):
    '''Generic sprite class'''
    def __init__(self, pos, surf, groups, z = LAYERS['main']):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = z
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)
        
class Interaction(Generic):
    '''Generic sprite class for objects that can be interacted with'''
    def __init__(self, pos, size, groups, name):
        surf = pygame.Surface(size)
        super().__init__(pos, surf, groups)
        self.name = name
        
class Water(Generic):
    '''Water sprite class'''
    def __init__(self, pos, frames, groups) -> None:
        self.frames = frames
        self.frame_index = 0
        super().__init__(pos, self.frames[self.frame_index], groups, LAYERS['water'])

    def animate(self, dt):
        '''Animate the water'''
        self.frame_index += dt * 5
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self, dt):
        '''Update the water animation'''
        self.animate(dt)

class CandySunflower(Generic):
    ''''Candy Sunflower sprite class'''
    def __init__(self, pos, surf, groups) -> None:
        super().__init__(pos, surf, groups)
        self.hitbox = self.rect.copy().inflate(-20, -self.rect.height * 0.9)

class Particle(Generic):
    '''Particle sprite class'''
    def __init__(self, pos, surf, groups, z, duration = 200):
        super().__init__(pos, surf, groups, z = LAYERS['main'])
        self.start_time = pygame.time.get_ticks()
        self.duration = duration
        
        mask_surf = pygame.mask.from_surface(self.image)
        new_surf = mask_surf.to_surface()
        new_surf.set_colorkey((0, 0, 0))
        self.image = new_surf
        
    def update(self,dt):
        '''Update the particle animation'''
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.duration:
            self.kill()

class Tree(Generic):
    '''Tree sprite class'''
    def __init__(self, pos, surf, groups, name,player_add) -> None:
        super().__init__(pos, surf, groups)
        
        self.health = 5
        self.alive = True
        #{"small" if name == "Small" else "large"}
        self.stump_surf = pygame.image.load(f'graphics/stumps/small.png').convert_alpha()
        
        self.apple_surf = pygame.image.load('graphics/fruit/candy_apple.png')
        self.apple_pos = APPLE_POS[name]
        self.apple_sprites = pygame.sprite.Group()
        if self.health > 0:
            self.create_fruit()
        
        self.player_add = player_add
        
        self.axe_sound = pygame.mixer.Sound('audio/axe.mp3')
        
    def damage(self):
        '''Damage the tree'''
        self.health -= 1
        self.axe_sound.play()
        
        if len(self.apple_sprites.sprites()) > 0:
            random_apple = choice(self.apple_sprites.sprites())
            ObjectFactory.create_object("Particle", pos = random_apple.rect.topleft, 
                     surf = random_apple.image, 
                     groups = self.groups()[0], 
                     z = LAYERS['fruit'])
            self.player_add('candy_apple')
            random_apple.kill()
    
    def check_death(self):
        '''Check if the tree is dead'''
        if self.health <= 0:
            print('dead')
            ObjectFactory.create_object("Particle", pos = self.rect.topleft, 
                     surf = self.image, 
                     groups = self.groups()[0], 
                     z = LAYERS['fruit'],
                     duration = 500)
            self.image = self.stump_surf
            self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
            self.hitbox = self.rect.copy().inflate(-10, -self.rect.height * 0.6)
            self.alive = False
            self.player_add('wood')
    
    def update(self, dt):
        '''Update the tree'''
        if self.alive:
            self.check_death()
        
    def create_fruit(self):
        '''Create fruit'''
        for pos in self.apple_pos:
            if randint(0,10) < 4:
                x = pos[0] + self.rect.left
                y = pos[1] + self.rect.top
                Generic(pos = (x, y), 
                        surf = self.apple_surf, 
                        groups = [self.apple_sprites, self.groups()[0]],
                        z = LAYERS['fruit'])
               