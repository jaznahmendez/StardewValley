from typing import Any
import pygame
from settings import *
from support import *
from timer import Timer
#TO DOs
#CREATE TOOL AND SEED ENUM FOR CLASS USE
class Player(pygame.sprite.Sprite):
    def __init__(self, position, group, collision_sprites, tree_sprites, interaction, soil_layer) -> None:
        super().__init__(group)

        self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0

        self.image = self.animations[self.status][self.frame_index]
        
        self.rect = self.image.get_rect(center = position)
        self.z = LAYERS['main']
        self.hitbox = self.rect.copy().inflate(-126, -70)
        
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200

        self.collision_sprites = collision_sprites

        self.tools = ['hoe', 'axe', 'water']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]

        self.timers = {
            'tool_use': Timer(600, self.use_tool),
            'tool_switch': Timer(200),
            'seed_use': Timer(350, self.use_seed),
            'seed_switch': Timer(200),
        }

        self.seeds = ['candy_tomato1', 'candy_tomato2']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]
        
        self.item_inventory = {
            'wood': 0,
            'apple': 0,
            'corn': 0,
            'tomato': 0
        }
        
        self.tree_sprites = tree_sprites
        self.interaction = interaction
        self.sleep = False
        self.soil_layer = soil_layer

    def use_tool(self):
        if self.selected_tool == 'hoe':
            self.soil_layer.get_hit(self.target_pos)
            
        if self.selected_tool == 'axe':
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()
                
        if self.selected_tool == 'water':
            self.soil_layer.water(self.target_pos)
        
    def get_target_pos(self):
        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]
        
    def use_seed(self):
        self.soil_layer.plant_seed(self.target_pos, self.selected_seed)

    def import_assets(self):
        self.animations = {'up': [],'down': [],'left': [],'right': [],
						   'right_idle':[],'left_idle':[],'up_idle':[],'down_idle':[],
						   'right_hoe':[],'left_hoe':[],'up_hoe':[],'down_hoe':[],
						   'right_axe':[],'left_axe':[],'up_axe':[],'down_axe':[],
						   'right_water':[],'left_water':[],'up_water':[],'down_water':[]}
        for animation in self.animations.keys():
            path = 'graphics/character/' + animation
            self.animations[animation] = import_folder(path)

    def animate(self, dt):
        self.frame_index += dt * 4
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0
        self.image = self.animations[self.status][int(self.frame_index)]

    def input(self):
        pressed = pygame.key.get_pressed()

        if not self.timers['tool_use'].active and not self.sleep:
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
        
        if pressed[pygame.K_RETURN]:
            collided_interaction_sprite = pygame.sprite.spritecollide(self, self.interaction, False)
            if collided_interaction_sprite:
                if collided_interaction_sprite[0].name == 'Trader':
                    pass
                else:
                    self.status = 'left_idle'
                    self.sleep = True

    def get_status(self):
        if self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_idle'
        
        if self.timers['tool_use'].active:
            self.status = self.status.split('_')[0] + '_' + self.selected_tool

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        if self.direction.x > 0:
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0:
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx
                    if direction == 'vertical':
                        if self.direction.y > 0:
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0:
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery

    def move(self, dt):
        if self.direction.magnitude() > 0:  
            self.direction = self.direction.normalize()

        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')

        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')     

    def update(self, dt):
        self.input()
        self.get_status()
        self.update_timers()
        self.get_target_pos()
        self.move(dt)
        self.animate(dt)