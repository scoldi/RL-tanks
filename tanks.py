import pygame as pg
import numpy as np
import uuid
import random

pg.font.init()
pg.display.init()
font = pg.font.SysFont('Comic Sans MS', 25)
window_width = 700
window_height = 700
manual_controls = True
grid_x = 13
grid_y = 13
tile_width = window_width / grid_x
tile_height = window_height / grid_y
tile_img_paths = {'water': 'img/water.png', 'ground': 'img/ground.png', 'brick': 'img/brick.png'}


class Game:

    def __init__(self):
        pg.display.set_caption('tanks or whatever')
        self.gameDisplay = pg.display.set_mode((window_width, window_height))
        self.gameDisplay.fill((250, 250, 250))
        self.running = False
        self.win = False
        self.grid = np.zeros((grid_x, grid_y), dtype=Tile)
        pg.display.flip()


class Tile:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.img = pg.image.load(tile_img_paths[self.type])

    def get_screen_coords(self):
        return self.x * tile_width, window_height - (self.y + 1) * tile_height


class Projectile:

    # direction constants
    (DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)

    # bullet's stated
    (STATE_REMOVED, STATE_ACTIVE, STATE_EXPLODING) = range(3)

    (OWNER_PLAYER, OWNER_ENEMY) = range(2)

    def __init__(self, color):
        self.color = color
        self.loaded = False


class Timer(object):
    def __init__(self):
        self.timers = []

    def add(self, interval, f, repeat = -1):
        options = {
            "interval": interval,
            "callback": f,
            "repeat": repeat,
            "times": 0,
            "uuid": uuid.uuid4(),
            "time": 0
        }
        self.timers.append(options)
        return options["uuid"]

def destroy(self, uuid_nr):
    for timer in self.timers:
        if timer["uuid"] == uuid_nr:
            self.timers.remove(timer)
            return


    def update(self, time_passed):
        for timer in self.timers:
            timer["time"] += time_passed
            if timer["time"] > timer["interval"]:
                timer["time"] -= timer["interval"]
                timer["times"] += 1
                if timer["repeat"] > -1 and timer["times"] == timer["repeat"]:
                    self.timers.remove(timer)
                try:
                    timer["callback"]()
                except:
                    try:
                        self.timers.remove(timer)
                    except:
                        pass

class Player(object):

    (STATE_SPAWNING, STATE_DEAD, STATE_ALIVE, STATE_EXPLODING) = range(4)

    def __init__(self, id, game, tile_x, tile_y, direction):
        self.id = id
        self.original_image = pg.image.load('img/tank.PNG')
        self.img = self.original_image
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.direction = direction
        self.ammo = []
        self.game = game
        self.state = self.STATE_SPAWNING

    def update_direction(self):
        if np.array_equal(self.direction, [1, 0, 0, 0]):
            self.img = self.original_image
        elif np.array_equal(self.direction, [0, 1, 0, 0]):
            self.img = pg.transform.rotate(self.original_image, 90)
        elif np.array_equal(self.direction, [0, 0, 1, 0]):
            self.img = pg.transform.rotate(self.original_image, 180)
        elif np.array_equal(self.direction, [0, 0, 0, 1]):
            self.img = pg.transform.rotate(self.original_image, -90)

    def enable_manual_move(self):
        # events = pg.event.get()
        #     for event in events:
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

    # array of 0 and 1: [up, left, down, right]
    def move(self, move):
        if np.array_equal(move, [1, 0, 0, 0]):
            self.tile_y += 1
        elif np.array_equal(move, [0, 1, 0, 0]):
            self.tile_x -= 1
        elif np.array_equal(move, [0, 0, 1, 0]):
            self.tile_y -= 1
        elif np.array_equal(move, [0, 0, 0, 1]):
            self.tile_x += 1
        self.direction = move
        self.update_direction()


def display_player(player, tile):
    player.game.gameDisplay.blit(pg.transform.scale(player.img, (int(tile_width), int(tile_height))), tile.get_screen_coords())


def init_world(game):
    for col_idx, col in enumerate(game.grid):
        for row_idx, row in enumerate(col):
            tile = Tile(row_idx, col_idx, 'ground')
            game.grid[row_idx, col_idx] = tile


def draw_world(game):
    for col in game.grid:
        for tile in col:
            game.gameDisplay.blit(pg.transform.scale(tile.img, (int(tile_width), int(tile_height))), (tile.get_screen_coords()))


def update_screen(game, players):
    # game.gameDisplay.fill((255,255,255))
    draw_world(game)
    for player in players:
        display_player(player, game.grid[player.tile_x, player.tile_y])
    pg.display.update()


def run():
    game = Game()
    player = Player(1, game, 7, 7, [0, 0, 1, 0])
    game.running = True
    pg.init()
    init_world(game)
    while game.running:
        if manual_controls:
            player.enable_manual_move()
        update_screen(game, [player])
        # else: auto
        for event in pg.event.get():
            if event.type == pg.QUIT:
                game.running = False
                pg.quit()


run()
