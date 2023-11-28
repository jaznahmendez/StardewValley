import pygame
from settings import *
from timer import Timer

class Menu:
    '''Base class for all menus.'''
    def __init__(self, player, toggle_menu):
        '''Initialize the menu.'''
        self.player = player
        self.toggle_menu = toggle_menu
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font('font/LycheeSoda.ttf', 25)

        self.width = 400
        self.space = 10
        self.padding = 8
        
        self.options = list(self.player.item_inventory.keys()) + list(self.player.seed_inventory.keys())
        self.sell_border = len(self.player.item_inventory) - 1
        self.setup()
        
        self.index = 0
        self.timer = Timer(250)
    
    def display_money(self):
        '''Displays the player's money.'''
        text_surf = self.font.render(f'${self.player.money}', False, 'Black')
        text_rect = text_surf.get_rect(midbottom = (SCREEN_WIDTH / 2, SCREEN_HEIGHT - 25))
        
        pygame.draw.rect(self.display_surface, 'White', text_rect.inflate(10,10),0,8)
        self.display_surface.blit(text_surf, text_rect)
    
    def setup(self):
        '''Sets up the menu.'''
        self.text_surfs = []
        self.total_height = 0
        for item in self.options:
            text_surf = self.font.render(item, False, 'Black')
            self.text_surfs.append(text_surf)
            self.total_height += text_surf.get_height() + (self.padding * 2)
        
        self.total_height += (len(self.text_surfs)-1) * self.space
        self.menu_top = SCREEN_HEIGHT / 2 - self.total_height / 2
        self.main_rect = pygame.Rect(SCREEN_WIDTH/2 - self.width / 2,self.menu_top, self.width, self.total_height)
        
        self.buy_text = self.font.render('buy', False, 'Black')
        self.sell_text = self.font.render('sell', False, 'Black')
            
    def input(self):
        '''Handles menu input.'''
        keys = pygame.key.get_pressed()
        self.timer.update()
        
        if keys[pygame.K_ESCAPE]:
            self.toggle_menu()
        
        if not self.timer.active:
            if keys[pygame.K_UP]:
                self.index -= 1
                self.timer.activate()
                
            if keys[pygame.K_DOWN]:
                self.index += 1
                self.timer.activate()
            
            if keys[pygame.K_SPACE]:
                self.timer.activate()
                current_item = self.options[self.index]
                
                if self.index <= self.sell_border:
                    if self.player.item_inventory[current_item] > 0:
                        self.player.item_inventory[current_item] -= 1
                        self.player.money += SALE_PRICES[current_item]
                else:
                     seed_price = PURCHASE_PRICES[current_item]
                     if self.player.money >= seed_price:
                         self.player.seed_inventory[current_item] += 1
                         self.player.money -= PURCHASE_PRICES[current_item]
                         
                        
        if self.index < 0:
            self.index = len(self.options) - 1
        if self.index > len(self.options) - 1:
            self.index = 0
    
    def show_entry(self, text_surf, amount, top, selected):
        '''Displays a menu entry.'''
        bg_rect = pygame.Rect(self.main_rect.left, top, self.width, text_surf.get_height() + (self.padding * 2))
        pygame.draw.rect(self.display_surface, 'White', bg_rect, 0,8)
        
        text_rect = text_surf.get_rect(midleft = (self.main_rect.left  + 20, bg_rect.centery))
        self.display_surface.blit(text_surf,text_rect)
        
        amount_surf = self.font.render(str(amount),False, 'Black')
        amount_rect = amount_surf.get_rect(midright = (self.main_rect.right - 20, bg_rect.centery))
        self.display_surface.blit(amount_surf, amount_rect)
        
        if selected:
            pygame.draw.rect(self.display_surface, 'black', bg_rect, 4,4)
            if self.index <= self.sell_border: #sell
                pos_rect = self.sell_text.get_rect(midleft = (self.main_rect.left+240, bg_rect.centery))
                self.display_surface.blit(self.sell_text,pos_rect)
            else: # buy
                pos_rect = self.buy_text.get_rect(midleft = (self.main_rect.left+240, bg_rect.centery))
                self.display_surface.blit(self.buy_text,pos_rect)
                
    def update(self):
        '''Updates the menu.'''
        self.input()
        self.display_money()
        for text_index, text_surf in enumerate(self.text_surfs):
            top = self.main_rect.top + text_index * (text_surf.get_height() + (self.padding * 2) + self.space)
            amount_list = list(self.player.item_inventory.values()) + list(self.player.seed_inventory.values())
            amount = amount_list[text_index]
            self.show_entry(text_surf, amount, top, self.index == text_index)