import os
import pickle
import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, CandySunflower, Tree, Interaction, Particle
from pytmx.util_pygame import load_pygame
from support import *
from transition import Transition
from soil import SoilLayer
from sky import Rain, Sky
from random import randint
from menu import Menu

#HACER QUE SI SE RESETEA EL DÍA, EMPIECE VIENDO PARA ABAJO

class Memento:
    def __init__(self, player_state, raining, soil_state):
        self.player_state = player_state
        self.raining = raining
        self.soil_state = soil_state
        #self.tree_state = tree_state

    def get_state(self):
        return self.player_state, self.raining, self.soil_state

class Level:
    def __init__(self) -> None:
        self.display_surface = pygame.display.get_surface()
        self.init_pos = (0,0)

        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()

        self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)
        self.setup()
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset, self.player)
        
        self.rain = Rain(self.all_sprites)
        self.raining = randint(0,10) > 5
        self.soil_layer.raining = self.raining
        self.sky = Sky()
        
        self.shop_active = False
        self.menu = Menu(self.player, self.toggle_shop)
        
        self.music = pygame.mixer.Sound('audio/blank_space.mp3')
        self.music.set_volume(0.2)
        self.music.play(loops = -1)
        self.success = pygame.mixer.Sound('audio/success.wav')
        self.success.set_volume(0.3)
        
        self.reset_button = pygame.Rect(50, 50, 100, 50)  # Cambia las dimensiones y la posición según tus necesidades
        self.reset_button_color = (255, 0, 0)  # Rojo, por ejemplo
        
        try:
            with open('saved_game_status.pkl', 'rb') as f:
                saved_state = pickle.load(f)
                self.restore_from_memento(saved_state)
        except FileNotFoundError:
            pass
    
    def save_to_memento(self):
        player_state = self.player.get_state()
        soil_state = self.soil_layer.get_state()

        return Memento(player_state, self.raining, soil_state)

    def restore_from_memento(self, memento):
        player_state, raining, soil_state = memento.get_state()
        self.player.set_state(player_state)
        self.raining = raining
        self.soil_layer.set_state(soil_state)
        #for tree, state in zip(self.tree_sprites, tree_state):
        #    tree.set_state(state)  # Y un método set_state en Tree
    
    def reset_game(self):        
        self.player.reset_player(self.init_pos)
        self.soil_layer.reset_soil()
        self.raining = randint(0,10) > 5
        
        try:
            os.remove('saved_game_status.pkl')
        except FileNotFoundError:
            pass
    
    def setup(self):
        tmx_data = load_pygame('data/map.tmx')

        for layer in ['HouseFloor', 'HouseFurnitureBottom']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])

        for layer in ['HouseWalls', 'HouseFurnitureTop']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['main'])

            for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprites], LAYERS['main'])

        water_frames = import_folder('graphics/water')
        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites)

        for obj in tmx_data.get_layer_by_name('Decoration'):
            CandySunflower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])

        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree(pos = (obj.x, obj.y), 
                 surf = obj.image, 
                 groups = [self.all_sprites, self.collision_sprites, self.tree_sprites], 
                 name = obj.name,
                 player_add = self.player_add)

        for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), self.collision_sprites, LAYERS['main'])

        Generic((0, 0), pygame.image.load('graphics/world/ground.png').convert_alpha(), self.all_sprites, LAYERS['ground'])
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.init_pos = (obj.x, obj.y)
                self.player = Player(
                    position = (obj.x, obj.y), 
                    group = self.all_sprites, 
                    collision_sprites = self.collision_sprites,
                    tree_sprites = self.tree_sprites,
                    interaction = self.interaction_sprites,
                    soil_layer = self.soil_layer,
                    toggle_shop = self.toggle_shop)
            
            if obj.name == 'Bed':
                Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)
                
            if obj.name == 'Trader':
                Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)
          
    def player_add(self, item,):
        self.success.play()
        self.player.item_inventory[item] += 1
    
    def toggle_shop(self):
        self.shop_active = not self.shop_active
    
    def reset(self):
        self.soil_layer.update_plants()
        
        self.soil_layer.remove_water()    
        self.raining = randint(0,10) > 5
        self.soil_layer.raining = self.raining
        if self.raining:
            self.soil_layer.water_all()
        
        for tree in self.tree_sprites.sprites():
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            if  tree.alive:
                tree.create_fruit()
                
        self.sky.start_color = [255, 255, 255]
    
    def plant_collision(self):
        if self.soil_layer.plant_sprites:
            for plant in self.soil_layer.plant_sprites.sprites():
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    self.player_add(plant.plant_type)
                    plant.kill()
                    Particle(
                        pos = plant.rect.topleft,
                        surf = plant.image,
                        groups = self.all_sprites,
                        z = LAYERS['main']
                    )
                    self.soil_layer.grid[plant.rect.centery // TILE_SIZE][plant.rect.centerx // TILE_SIZE].remove('P')
    
    def save_game(self):
        current_state = self.save_to_memento()
        with open('saved_game_status.pkl', 'wb') as f:
            pickle.dump(current_state, f)
    
    def run(self, dt):
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)
        
        if self.shop_active:
            self.menu.update()
        else:
            self.all_sprites.update(dt)
            self.plant_collision()
            pygame.draw.rect(self.display_surface, self.reset_button_color, self.reset_button)
            font = pygame.font.Font(None, 36)  # Cambia el tamaño y la fuente según tus necesidades
            text = font.render('Reset', True, (255, 255, 255))  # Texto blanco
            text_rect = text.get_rect(center=self.reset_button.center)
            self.display_surface.blit(text, text_rect)
            
        self.overlay.display()
        if self.raining and not self.shop_active:
            self.rain.update()
            pygame.draw.rect(self.display_surface, self.reset_button_color, self.reset_button)
            font = pygame.font.Font(None, 36)  # Cambia el tamaño y la fuente según tus necesidades
            text = font.render('Reset', True, (255, 255, 255))  # Texto blanco
            text_rect = text.get_rect(center=self.reset_button.center)
            self.display_surface.blit(text, text_rect)
        
        self.sky.display(dt)
        
        if self.player.sleep:
            self.transition.play()
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.reset_button.collidepoint(event.pos):
                    self.reset_game()
        
        #print(self.shop_active)
        #print(self.player.item_inventory)

class CameraGroup(pygame.sprite.Group):
    def __init__(self) -> None:
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)