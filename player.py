from typing import Any
import pygame
from settings import *
from support import *
from timer import Timer

class Player(pygame.sprite.Sprite):
    def __init__(self, position, group) -> None:
        super().__init__(group)

        self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0

        self.image = self.animations[self.status][self.frame_index]
        
        self.rect = self.image.get_rect(center = position)
        self.z = LAYERS['main']
        
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200

        self.tools = ['hoe', 'axe', 'water']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]

        self.timers = {
            'tool_use': Timer(350, self.use_tool),
            'tool_switch': Timer(200),
            'seed_use': Timer(350, self.use_seed),
            'seed_switch': Timer(200),
        }

        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

    def use_tool(self):
        #print(self.selected_tool)
        pass

    def use_seed(self):
        pass

    def import_assets(self):
        self.animations = {'up': [],'down': [],'left': [],'right': [],
						   'right_idle':[],'left_idle':[],'up_idle':[],'down_idle':[],
						   'right_hoe':[],'left_hoe':[],'up_hoe':[],'down_hoe':[],
						   'right_axe':[],'left_axe':[],'up_axe':[],'down_axe':[],
						   'right_water':[],'left_water':[],'up_water':[],'down_water':[]}
        for animation in self.animations.keys():
            path = './NEW_ASSETS/player/graphics/character/' + animation
            self.animations[animation] = import_folder(path)

    def animate(self, dt):
        self.frame_index += dt * 4
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0
        self.image = self.animations[self.status][int(self.frame_index)]


    def input(self):
        pressed = pygame.key.get_pressed()

        if not self.timers['tool_use'].active:
            if pressed[pygame.K_w]:
                self.direction.y = -1
                self.status = 'up'
            elif pressed[pygame.K_s]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0

            if pressed[pygame.K_a]:
                self.direction.x = -1
                self.status = 'left'
            elif pressed[pygame.K_d]:
                self.direction.x = 1
                self.status = 'right'
            else:
                self.direction.x = 0

        if pressed[pygame.K_SPACE]:
            self.timers['tool_use'].activate()
            self.direction = pygame.math.Vector2()
            self.frame_index = 0

        if pressed[pygame.K_q] and not self.timers['tool_switch'].active:
            self.timers['tool_switch'].activate()
            self.tool_index += 1
            if self.tool_index >= len(self.tools):
                self.tool_index = 0
            self.selected_tool = self.tools[self.tool_index]

        if pressed[pygame.K_LCTRL]:
            self.timers['seed_use'].activate()
            self.direction = pygame.math.Vector2()
            self.frame_index = 0

        if pressed[pygame.K_e] and not self.timers['seed_switch'].active:
            self.timers['seed_switch'].activate()
            self.seed_index += 1
            if self.seed_index >= len(self.seeds):
                self.seed_index = 0
            self.selected_seed = self.seeds[self.seed_index]
            print(self.selected_seed)

    def get_status(self):
        if self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_idle'
        
        if self.timers['tool_use'].active:
            self.status = self.status.split('_')[0] + '_' + self.selected_tool

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def move(self, dt):
        if self.direction.magnitude() > 0:  
            self.direction = self.direction.normalize()

        self.pos.x += self.direction.x * self.speed * dt
        self.rect.centerx = self.pos.x

        self.pos.y += self.direction.y * self.speed * dt
        self.rect.centery = self.pos.y
        

    def update(self, dt):
        self.input()
        self.get_status()
        self.update_timers()
        self.move(dt)
        self.animate(dt)