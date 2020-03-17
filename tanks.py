import pygame as pg
import numpy as np
import uuid
import random

pg.font.init()
pg.display.init()
win_count = 0
lose_count = 0
font = pg.font.SysFont('Comic Sans MS', 25)
window_width = 700
window_height = 700
manual_controls = True
grid_x = 13
grid_y = 13
#tank_start_x = (grid_x - 1) / 2
#tank_start_y = (grid_y - 1) / 2
tile_width = window_width / grid_x
tile_height = window_height / grid_y
tanks = []
flags = []
castles = []
tile_img_paths = {'empty': None, 'water': 'img/water.png', 'ground': 'img/ground.png', 'brick': 'img/brick.png',
                'castle': 'img/castle.png'}
tile_durabilities = {'empty': 0, 'water': 0, 'ground': 2, 'brick': 4, 'castle': 1, 'castle_zone': 0}


class Game:

    def __init__(self):
        pg.display.set_caption('tanks or whatever')
        self.gameDisplay = pg.display.set_mode((window_width, window_height))
        self.gameDisplay.fill((250, 250, 250))
        self.running = False
        self.win = False
        self.grid = np.zeros((grid_x, grid_y), dtype=Tile)
        pg.display.flip()

    def win(self):
        return 1

    def lose(self):
        return 1

    def reset(self):
        return 1

class Tile:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.durability = tile_durabilities[self.type]
        self.items = []
        if type == 'empty':
            self.img = pg.Surface((tile_width, tile_height))
        elif type == 'castle_zone':
            self.img = pg.Surface((tile_width, tile_height))
        else:
            self.img = pg.image.load(tile_img_paths[type])

    def destroy(self):
        img = pg.Surface((tile_width, tile_height))
        self.type = 'empty'
        self.img = img

    def get_screen_coords(self):
        return self.x * tile_width, window_height - (self.y + 1) * tile_height

    def show_shot(self, horizontal):
        return
        #coords = self.get_screen_coords()
        #game.gameDisplay.blit()


class Castle(Tile):

    def __init__(self, x, y):
        Tile.__init__(self, x, y, 'castle')
        castles.append(self)

    def destroy(self):
        img = pg.Surface((tile_width, tile_height))
        self.type = 'empty'
        self.img = img
        game.lose()


class Castle_zone(Tile):

    def __init__(self, x, y):
        Tile.__init__(self, x, y, 'castle_zone')

    def deliver_flag(self, flag):
        game.win()


class Tank(object):

    def __init__(self, id, tile, direction):
        self.id = id
        self.original_image = pg.image.load('img/tank.PNG')
        self.img = self.original_image
        self.tile = tile
        self.direction = direction
        self.ammo = []
        self.target = None
        self.has_flag = False
        self.flag = None
        self.get_target()
        tanks.append(self)

    def update_direction(self):
        if np.array_equal(self.direction, [1, 0, 0, 0]):
            self.img = self.original_image
        elif np.array_equal(self.direction, [0, 1, 0, 0]):
            self.img = pg.transform.rotate(self.original_image, 90)
        elif np.array_equal(self.direction, [0, 0, 1, 0]):
            self.img = pg.transform.rotate(self.original_image, 180)
        elif np.array_equal(self.direction, [0, 0, 0, 1]):
            self.img = pg.transform.rotate(self.original_image, -90)

    def get_target(self):
        target = None
        horizontal = True
        trail = []
        if np.array_equal(self.direction, [1, 0, 0, 0]):
            horizontal = not horizontal
            for idx in range(self.tile.y, grid_y):
                tile = game.grid[self.tile.x, idx]
                trail.append(tile)
                if tile.type not in ['empty', 'water']:
                    target = tile
                    break
        elif np.array_equal(self.direction, [0, 0, 0, 1]):
            for idx in range(self.tile.x, grid_x):
                tile = game.grid[idx, self.tile.y]
                trail.append(tile)
                if tile.type not in ['empty', 'water']:
                    target = tile
                    break
        elif np.array_equal(self.direction, [0, 1, 0, 0]):
            for idx in range(self.tile.x, -1, -1):
                tile = game.grid[idx, self.tile.y]
                trail.append(tile)
                if tile.type not in ['empty', 'water']:
                    target = tile
                    break
        elif np.array_equal(self.direction, [0, 0, 1, 0]):
            horizontal = not horizontal
            for idx in range(self.tile.y, -1, -1):
                tile = game.grid[self.tile.x, idx]
                trail.append(tile)
                if tile.type not in ['empty', 'water']:
                    target = tile
                    break
        #if target:
            # target.img = pg.Surface((tile_width, tile_height))
            # target.img.fill([255, 0, 0])
        for tile in trail:
            tile.show_shot(horizontal)
        self.target = target
        update_screen()

    # [up, left, down, right]
    def shoot(self):
        if self.target:
            self.target.durability -= 1
            if self.target.durability == 0:
                self.target.destroy()
                draw_tile(self.target)
                self.get_target()

    def enable_manual_controls(self):
        event = pg.event.wait()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_LEFT:
                self.move([0, 1, 0, 0])
            elif event.key == pg.K_RIGHT:
                self.move([0, 0, 0, 1])
            elif event.key == pg.K_UP:
                self.move([1, 0, 0, 0])
            elif event.key == pg.K_DOWN:
                self.move([0, 0, 1, 0])
            elif event.key == pg.K_SPACE:
                self.shoot()

    #def drop_flag(self):

    def deliver(self):
        if self.tile.type == 'castle_zone' and self.has_flag:
            self.tile.deliver(self.flag)

    # [up, left, down, right]
    def move(self, move):
        new_tile = None
        if np.array_equal(move, [1, 0, 0, 0]) and self.tile.y < grid_y - 1:
            new_tile = game.grid[self.tile.x, self.tile.y + 1]
        elif np.array_equal(move, [0, 0, 0, 1]) and self.tile.x < grid_x - 1:
            new_tile = game.grid[self.tile.x + 1, self.tile.y]
        elif np.array_equal(move, [0, 1, 0, 0]) and self.tile.x > 0:
            new_tile = game.grid[self.tile.x - 1, self.tile.y]
        elif np.array_equal(move, [0, 0, 1, 0]) and self.tile.y > 0:
            new_tile = game.grid[self.tile.x, self.tile.y - 1]
        if new_tile and new_tile.type in ('empty', 'castle_zone'):
            self.tile = new_tile
        self.direction = move
        self.update_direction()
        self.get_target()
        self.pickup(self.tile)
        self.deliver()

    def pickup_flag(self, flag):
        self.has_flag = True
        self.flag = flag
        flag.hide()

    def pickup(self, tile):
        for item in tile.items:
            if isinstance(item, Flag):
                self.pickup_flag(item)

class Pickup(object):
    def __init__(self, tile):
        tile.items.append(self)
        self.tile = tile
        self.picked_up = False
        self.img = None

    def show(self, tile):
        self.tile = tile
        self.picked_up = False

    def hide(self):
        self.picked_up = True


class Flag(Pickup):
    def __init__(self, tile):
        Pickup.__init__(self, tile)
        self.img = pg.image.load('img/flag_white.PNG')
        flags.append(self)

    def show(self, tile):
        Pickup.show(self, tile)
        self.img = pg.image.load('img/flag_white.PNG')

    def hide(self):
        Pickup.hide(self)
        self.img = pg.image.load('img/flag.PNG')


def draw_tank(tank):
    game.gameDisplay.blit(pg.transform.scale(tank.img, (int(tile_width), int(tile_height))), tank.tile.get_screen_coords())
    if tank.has_flag:
        game.gameDisplay.blit(pg.transform.scale(tank.flag.img, (int(tile_width/2), int(tile_height/2))), tank.tile.get_screen_coords())


def draw_flag(flag):
    if not flag.picked_up:
        game.gameDisplay.blit(pg.transform.scale(flag.img, (int(tile_width), int(tile_height))), flag.tile.get_screen_coords())


def init_world():
    for col_idx, col in enumerate(game.grid):
        for row_idx, row in enumerate(col):
            if col_idx in range(0, 2) and row_idx in range(int(grid_y / 2) - 1, int(grid_y / 2) + 2):
                if col_idx == 0 and row_idx == int(grid_y / 2):
                    tile = Castle(row_idx, col_idx)
                else:
                    tile = Castle_zone(row_idx, col_idx)
            else:
                # tile = Tile(row_idx, col_idx, random.choice(['ground', 'brick', 'water', 'empty']))
                tile = Tile(row_idx, col_idx, random.choice(['empty']))
            game.grid[row_idx, col_idx] = tile
    flag = Flag(game.grid[7, 7])
    tank = Tank(1, game.grid[int(grid_x / 2 + 1), 0], [1, 0, 0, 0])
    update_screen()


def draw_world():
    for col in game.grid:
        for tile in col:
            draw_tile(tile)


def draw_tile(tile):
    game.gameDisplay.blit(pg.transform.scale(tile.img, (int(tile_width), int(tile_height))), (tile.get_screen_coords()))
    if tile.durability > 0:
        textsurface = font.render(str(tile.durability), False, (255, 255, 255))
        game.gameDisplay.blit(textsurface, tile.get_screen_coords())


def update_screen():
    # game.gameDisplay.fill((255,255,255))
    draw_world()
    for tank in tanks:
        draw_tank(tank)
    for flag in flags:
        draw_flag(flag)
    pg.display.update()


def run():
    pg.init()
    init_world()
    while game.running:
        if manual_controls:
            for tank in tanks:
                tank.enable_manual_controls()
        update_screen()
        # else: auto
        for event in pg.event.get():
            if event.type == pg.QUIT:
                game.running = False
                pg.quit()


game = Game()
game.running = True
run()
