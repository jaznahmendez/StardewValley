from pygame.math import Vector2
# screen
'''Settings for the game.'''
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TILE_SIZE = 64


# overlay positions 
OVERLAY_POSITIONS = {
    '''Positions for the overlay.'''
	'tool' : (40, SCREEN_HEIGHT - 15), 
	'seed': (100, SCREEN_HEIGHT - 5)}

PLAYER_TOOL_OFFSET = {
    '''Offset for the player tool.'''
	'left': Vector2(-50,40),
	'right': Vector2(50,40),
	'up': Vector2(0,-10),
	'down': Vector2(0,50)
}

LAYERS = {
    '''Layers for the game.'''
	'water': 0,
	'ground': 1,
	'soil': 2,
	'soil water': 3,
	'rain floor': 4,
	'house bottom': 5,
	'ground plant': 6,
	'main': 7,
	'house top': 8,
	'fruit': 9,
	'rain drops': 10
}

APPLE_POS = {
    '''Positions for the apples.'''
	'Small': [(18,17), (30,37), (12,50), (30,45), (20,30), (30,10)],
	'Large': [(30,24), (60,65), (50,50), (16,40),(45,50), (42,70)]
}

GROW_SPEED = {
    '''Grow speed for the plants.'''
	'candy_tomato2': 1, #cambiar aquí si queremos que uno crezca más lento
	'candy_tomato1': 1
}

SALE_PRICES = {
    '''Sale prices for the items.'''
	'wood': 4,
	'candy_apple': 2,
	'candy_tomato1': 5,
	'candy_tomato2': 8
}
PURCHASE_PRICES = {
    '''Purchase prices for the items.'''
	'candy_tomato1': 3,
	'candy_tomato2': 5,
}