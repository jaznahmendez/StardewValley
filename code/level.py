import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import ObjectFactory
from pytmx.util_pygame import load_pygame
from support import FolderImportProxy
from transition import Transition
from soil import SoilLayer
from sky import Rain, Sky
from random import randint
from menu import Menu
import os
import pickle

class Memento:
    '''Memento class for storing game state'''
    def __init__(self, player_state, raining, soil_state):
        '''Initializes the memento'''
        self.player_state = player_state
        self.raining = raining
        self.soil_state = soil_state

    def get_state(self):
        '''Returns the state stored in the memento'''
        return self.player_state, self.raining, self.soil_state

class Level:
    '''Level class for managing game elements'''
    def __init__(self) -> None:
        '''Initializes the level'''
        self.loader_proxy = FolderImportProxy()
        self.init_pos = (0,0)
        
        self.display_surface = pygame.display.get_surface()

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
        
        self.reset_button = pygame.Rect(50, 50, 100, 50)
        self.reset_button_color = (255, 0, 0)
        
        try:
            with open('game_status.pkl', 'rb') as f:
                saved_state = pickle.load(f)
                self.restore_from_memento(saved_state)
        except FileNotFoundError:
            print('error')
            self.reset_game()
            
    def save_to_memento(self):
        '''Saves the current state of the game'''
        player_state = self.player.get_state()
        soil_state = self.soil_layer.get_state()
        return Memento(player_state, self.raining, soil_state)

    def restore_from_memento(self, memento):
        '''Restores the game state from a memento'''
        player_state, raining, soil_state = memento.get_state()
        self.player.set_state(player_state)
        self.raining = raining
        self.soil_layer.set_state(soil_state)
        
    def setup(self):
        '''Sets up the game elements'''
        tmx_data = load_pygame('data/map.tmx')

        for layer in ['HouseFloor', 'HouseFurnitureBottom']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                ObjectFactory.create_object("Generic", (x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])

        for layer in ['HouseWalls', 'HouseFurnitureTop']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                ObjectFactory.create_object("Generic", (x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['main'])

            for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
                ObjectFactory.create_object("Generic", (x * TILE_SIZE, y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprites], LAYERS['main'])

        water_frames = self.loader_proxy.import_folder('graphics/water')
        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            ObjectFactory.create_object("Water", (x * TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites)

        for obj in tmx_data.get_layer_by_name('Decoration'):
            ObjectFactory.create_object("CandySunflower", (obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])

        for obj in tmx_data.get_layer_by_name('Trees'):
            ObjectFactory.create_object("Tree", pos = (obj.x, obj.y), 
                 surf = obj.image, 
                 groups = [self.all_sprites, self.collision_sprites, self.tree_sprites], 
                 name = obj.name,
                 player_add = self.player_add)

        for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
            ObjectFactory.create_object("Generic", (x * TILE_SIZE, y * TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), self.collision_sprites, LAYERS['main'])

        ObjectFactory.create_object("Generic", (0, 0), pygame.image.load('graphics/world/ground.png').convert_alpha(), self.all_sprites, LAYERS['ground'])
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
                ObjectFactory.create_object("Interaction", (obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)
                
            if obj.name == 'Trader':
                ObjectFactory.create_object("Interaction", (obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)
          
    def player_add(self, item,):
        '''Adds an item to the player's inventory'''
        self.success.play()
        self.player.item_inventory[item] += 1
    
    def toggle_shop(self):
        '''Toggles the shop menu'''
        self.shop_active = not self.shop_active
        
    def reset_game(self):
        '''Resets the game'''
        self.soil_layer.update_reset()
        self.soil_layer.remove_water()
        self.player.reset_player(self.init_pos)    
        self.raining = randint(0,10) > 5
        self.soil_layer.raining = self.raining
        
        if self.raining:
            self.soil_layer.water_all()
        
        self.sky.start_color = [255, 255, 255]
        
        try:
            os.remove('game_status.pkl')
        except FileNotFoundError:
            pass
    
    def reset(self):
        '''Resets the game'''
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
        '''Checks if the player is colliding with a plant and harvests it if it is'''
        if self.soil_layer.plant_sprites:
            for plant in self.soil_layer.plant_sprites.sprites():
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    self.player_add(plant.plant_type)
                    plant.kill()
                    ObjectFactory.create_object("Particle", 
                        pos = plant.rect.topleft,
                        surf = plant.image,
                        groups = self.all_sprites,
                        z = LAYERS['main']
                    )
                    self.soil_layer.grid[plant.rect.centery // TILE_SIZE][plant.rect.centerx // TILE_SIZE].remove('P')
    
    def save_game(self):
        '''Saves the game state to a file'''
        current_state = self.save_to_memento()
        with open('game_status.pkl', 'wb') as f:
            pickle.dump(current_state, f)
            
    def update_game_elements(self, dt):
        '''Updates the game elements'''
        self.all_sprites.update(dt)
        if self.raining:
            self.rain.update()
        self.player.update(dt)
        
    def draw_game_elements(self):
        '''Draws the game elements'''
        self.all_sprites.custom_draw(self.player)
        self.overlay.display()
        
    def run(self, dt):
        '''Runs the game loop'''
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)
        
        if self.shop_active:
            self.menu.update()
        else:
            self.all_sprites.update(dt)
            self.plant_collision()
            pygame.draw.rect(self.display_surface, self.reset_button_color, self.reset_button)
            font = pygame.font.Font(None, 36)
            text = font.render('Reset', True, (255, 255, 255))
            text_rect = text.get_rect(center=self.reset_button.center)
            self.display_surface.blit(text, text_rect)
            
        self.overlay.display()
        if self.raining and not self.shop_active:
            self.rain.update()
            pygame.draw.rect(self.display_surface, self.reset_button_color, self.reset_button)
            font = pygame.font.Font(None, 36)
            text = font.render('Reset', True, (255, 255, 255))
            text_rect = text.get_rect(center=self.reset_button.center)
            self.display_surface.blit(text, text_rect)
        
        self.sky.display(dt)
        
        if self.player.sleep:
            self.transition.play()
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.reset_button.collidepoint(event.pos):
                    self.reset_game()
                    self.update_game_elements(dt)
                    self.draw_game_elements() 
        
        pygame.display.flip()

class CameraGroup(pygame.sprite.Group):
    '''CameraGroup class for managing sprites'''
    def __init__(self) -> None:
        '''Initializes the CameraGroup'''
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        '''Draws the sprites in the group'''
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)