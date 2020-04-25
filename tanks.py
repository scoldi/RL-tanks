import pygame as pg
import numpy as np
import random
from keras.utils import to_categorical
from DQNagent import DQNAgent
import queue
import datetime
import gc

gc.enable()
pg.font.init()
pg.display.init()
###
MANUAL_MODE = False
speed = 10
###
screen_width = 700
screen_height = 700
window_width = 1050
window_height = 750
grid_x = 9
grid_y = 9
tile_margin = 3
tile_width = screen_width / grid_x - tile_margin
tile_height = screen_height / grid_y - tile_margin
tile_font = pg.font.SysFont('Arial', int(tile_width / 2))
info_font = pg.font.SysFont('Calibri', 36)

tile_img_paths = {'empty': None, 'water': 'img/water.png', 'ground': 'img/ground.png', 'brick': 'img/brick.png',
                'castle': 'img/castle.png'}
tile_durabilities = {'empty': 0, 'water': 0, 'ground': 2, 'brick': 4, 'castle': 1, 'castle_zone': 0}

BG_COLOR = (240, 240, 240)


class Game:

    def __init__(self, epochs):
        pg.display.set_caption('tanks teach themselves')
        self.gameDisplay = pg.display.set_mode((window_width, window_height))
        self.gameDisplay.fill(BG_COLOR)
        #self.screen_area = pg.Rect(0, 0, screen_width, screen_height)
        #self.info_area = pg.Rect((screen_width + 25, screen_height + 25),
        #                         (window_width - screen_width - 50, window_height - screen_height - 50))
        self.running = True
        self.epochs = epochs
        self.epochs_elapsed = 0
        self.turns_limit = 500
        self.turns = 0
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.ended = False
        self.victory = False
        self.win_count = 0
        self.lose_count = 0
        self.grid = np.zeros((grid_x, grid_y), dtype=Tile)
        self.tanks = []
        self.flags = []
        self.castles = []

    def win(self):
        self.win_count += 1
        self.victory = True
        self.running = False
        self.ended = True

    def lose(self):
        self.lose_count += 1
        self.running = False
        self.ended = True

    def reset(self):
        print('reset')
        self.over_turn_limit = False
        self.ended = False
        self.victory = False
        self.running = True
        self.tanks = []
        self.flags = []
        self.castles = []
        for col in self.grid:
            for tile in col:
                del tile
        self.turns = 0
        self.grid = np.zeros((grid_x, grid_y), dtype=Tile)

    def update_screen(self):
        self.gameDisplay.fill(BG_COLOR)
        self.draw_world()
        self.draw_info()
        for tank in self.tanks:
            tank.draw_tank()
        for flag in self.flags:
            flag.draw_flag()
        pg.display.update()

    def draw_world(self):
        for col in self.grid:
            for tile in col:
                tile.draw_tile()

    def init_world(self, base_loc='bottom', brick_chance=0.2):
        for col_idx, col in enumerate(self.grid):
            for row_idx, row in enumerate(col):
                if base_loc == 'bottom':
                    if col_idx in range(int(grid_x / 2) - 1, int(grid_x / 2) + 2) and row_idx in range(0, 2):
                        if col_idx == int(grid_x / 2) and row_idx == 0:
                            self.grid[col_idx, row_idx] = Castle(col_idx, row_idx)
                        else:
                            self.grid[col_idx, row_idx] = Castle_zone(col_idx, row_idx)
                    else:
                        type = 'empty'
                        if random.random() < brick_chance:
                            type = 'brick'
                        self.grid[col_idx, row_idx] = Tile(col_idx, row_idx, type)

                elif base_loc == 'top':
                    if col_idx in range(int(grid_x / 2) - 1, int(grid_x / 2) + 2) and row_idx in range(grid_y - 2,
                                                                                                       grid_y):
                        if col_idx == int(grid_x / 2) and row_idx == grid_y - 1:
                            self.grid[col_idx, row_idx] = Castle(col_idx, row_idx)
                        else:
                            self.grid[col_idx, row_idx] = Castle_zone(col_idx, row_idx)
                    else:
                        # tile = Tile(row_idx, col_idx, random.choice(['ground', 'brick', 'water', 'empty']))
                        # tile = Tile(row_idx, col_idx, random.choice(['empty']))
                        type = 'empty'
                        if random.random() < brick_chance:
                            type = 'brick'
                        self.grid[col_idx, row_idx] = Tile(col_idx, row_idx, type)

                elif base_loc == 'right':
                    if col_idx in range(grid_x - 2, grid_x) and row_idx in range(int(grid_y / 2) - 1,
                                                                                 int(grid_y / 2) + 2):
                        if col_idx == grid_x - 1 and row_idx == int(grid_y / 2):
                            self.grid[col_idx, row_idx] = Castle(col_idx, row_idx)
                        else:
                            self.grid[col_idx, row_idx] = Castle_zone(col_idx, row_idx)
                    else:
                        # tile = Tile(row_idx, col_idx, random.choice(['ground', 'brick', 'water', 'empty']))
                        # tile = Tile(row_idx, col_idx, random.choice(['empty']))
                        type = 'empty'
                        if random.random() < brick_chance:
                            type = 'brick'
                        self.grid[col_idx, row_idx] = Tile(col_idx, row_idx, type)

                elif base_loc == 'left':
                    if col_idx in range(0, 2) and row_idx in range(int(grid_y / 2) - 1, int(grid_y / 2) + 2):
                        if col_idx == 0 and row_idx == int(grid_y / 2):
                            self.grid[col_idx, row_idx] = Castle(col_idx, row_idx)
                        else:
                            self.grid[col_idx, row_idx] = Castle_zone(col_idx, row_idx)
                    else:
                        # tile = Tile(row_idx, col_idx, random.choice(['ground', 'brick', 'water', 'empty']))
                        # tile = Tile(row_idx, col_idx, random.choice(['empty']))
                        type = 'empty'
                        if random.random() < brick_chance:
                            type = 'brick'
                        self.grid[col_idx, row_idx] = Tile(col_idx, row_idx, type)

                elif base_loc == 'center':
                    if col_idx in range(int(grid_x / 2) - 1, int(grid_x / 2) + 2) and row_idx in range(
                            int(grid_y / 2) - 1, int(grid_y / 2) + 2):
                        if col_idx == int(grid_x / 2) and row_idx == int(grid_y / 2):
                            self.grid[col_idx, row_idx] = Castle(col_idx, row_idx)
                        else:
                            self.grid[col_idx, row_idx] = Castle_zone(col_idx, row_idx)
                    else:
                        # tile = Tile(row_idx, col_idx, random.choice(['ground', 'brick', 'water', 'empty']))
                        # tile = Tile(row_idx, col_idx, random.choice(['empty']))
                        type = 'empty'
                        if random.random() < brick_chance:
                            type = 'brick'
                        self.grid[col_idx, row_idx] = Tile(col_idx, row_idx, type)

        if base_loc in ('top', 'bottom'):
            tank_location_x = self.castles[0].x + 1
            tank_location_y = self.castles[0].y
        else:
            tank_location_x = self.castles[0].x
            tank_location_y = self.castles[0].y + 1

        flag_location_x = random.randint(0, grid_x - 1)
        flag_location_y = random.randint(0, grid_y - 1)
        while self.grid[flag_location_x, flag_location_y].type != 'empty':
            flag_location_x = random.randint(0, grid_x - 1)
            flag_location_y = random.randint(int(grid_y / 2), grid_y - 1)
        flag = Flag(self.grid[flag_location_x, flag_location_y])
        tank = Tank(1, self.grid[tank_location_x, tank_location_y], [1, 0, 0, 0])
        self.update_screen()

    def draw_info(self):
        games_textsurface = info_font.render('Epoch: ' + str(self.epochs_elapsed + 1) + '/' + str(self.epochs), True,
                                             (0, 0, 0))
        wl_textsurface = info_font.render('W/L: ' + str(self.win_count) + '/' + str(self.lose_count), True, (0, 0, 0))
        turns_textsurface = info_font.render('Turns: ' + str(self.turns) + '/' + str(self.turns_limit), True, (0, 0, 0))
        self.gameDisplay.blit(games_textsurface, (screen_width + 80, 50))
        self.gameDisplay.blit(wl_textsurface, (screen_width + 80, 100))
        self.gameDisplay.blit(turns_textsurface, (screen_width + 80, 150))

    def run(self, agent=None):
        self.running = True
        while self.epochs_elapsed < self.epochs:
            self.init_world(random.choice(['top', 'bottom', 'right', 'left', 'center']), 0.2)
            #self.init_world('bottom', 0)
            while self.running:
                if MANUAL_MODE:
                    self.tanks[0].enable_manual_controls()
                else:
                    state_old = agent.get_state(self, self.tanks[0], self.flags[0], self.castles[0])
                    # perform random actions based on agent.epsilon, or choose the action
                    if random.randint(0, agent.epsilon) < agent.epsilon - self.epochs_elapsed:
                        move = to_categorical(random.randint(0, 3), num_classes=4)
                    else:
                        # predict action based on the old state
                        prediction = agent.model.predict(state_old.reshape((1, 13)))
                        move = to_categorical(np.argmax(prediction[0]), num_classes=4)
                    self.tanks[0].move(move)

                    state_new = agent.get_state(self, self.tanks[0], self.flags[0], self.castles[0])

                    reward = agent.set_reward(self, self.tanks[0])

                    # train short memory base on the new action and state
                    defeat = self.ended and not self.victory
                    agent.train_short_memory(state_old, move, reward, state_new, defeat)

                    # store the new data into a long term memory
                    agent.remember(state_old, move, reward, state_new, defeat)
                    pg.time.wait(speed)
                    self.turns += 1
                    self.over_turn_limit = self.turns >= self.turns_limit
                    if self.over_turn_limit:
                        self.lose()
                        print('over turn limit!')

                pg.display.update()
                # self.turns += 1
                self.update_screen()
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.running = False
                        pg.quit()
                if self.ended:
                    self.epochs_elapsed += 1
                    if not MANUAL_MODE:
                        agent.replay_new(agent.memory)
                    self.reset()
                    break


class Tile:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.durability = tile_durabilities[self.type]
        self.color = (0, 0, 0)
        self.items = []
        if type == 'empty':
            self.img = pg.Surface((tile_width, tile_height))
        elif type == 'castle_zone':
            self.img = pg.Surface((tile_width, tile_height))
            self.img.fill((255, 0, 0))
        else:
            self.img = pg.image.load(tile_img_paths[type])

    def draw_tile(self, show_durability=True):
        game.gameDisplay.blit(pg.transform.scale(self.img, (int(tile_width), int(tile_height))),
                              (self.get_screen_coords()))
        if self.durability > 0 and show_durability:
            textsurface = tile_font.render(str(self.durability), False, (255, 0, 0))
            game.gameDisplay.blit(textsurface, self.get_screen_coords())

    def destroy(self):
        img = pg.Surface((tile_width, tile_height))
        self.type = 'empty'
        self.img = img

    def get_screen_coords(self):
        return 25 + self.x * tile_width + tile_margin * (self.x + 1), \
                screen_height - (self.y + 1) * tile_height - tile_margin * (self.y + 1) + 25

    def show_shot(self, horizontal):
        return
        #coords = self.get_screen_coords()
        #game.gameDisplay.blit()


class Castle(Tile):

    def __init__(self, x, y):
        Tile.__init__(self, x, y, 'castle')
        game.castles.append(self)

    def destroy(self):
        img = pg.Surface((tile_width, tile_height))
        self.type = 'empty'
        self.img = img
        game.lose()


class Castle_zone(Tile):

    def __init__(self, x, y):
        Tile.__init__(self, x, y, 'castle_zone')

    def deliver(self, flag):
        game.win()

class Tank(object):

    def __init__(self, id, tile, direction):
        self.id = id
        self.original_image = pg.image.load('img/tank.PNG')
        self.img = self.original_image
        self.tile = tile
        self.direction = direction
        self.last_move = [0, 0, 0, 0]
        self.prev_tiles = queue.Queue(4)
        self.ammo = []
        self.target = None
        self.took_flag = False
        self.has_flag = False
        self.flag = None
        self.get_target()
        game.tanks.append(self)

    # [up, left, down, right]
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
        # game.update_screen()

    # [up, left, down, right]
    def shoot(self):
        if self.target:
            self.target.durability -= 1
            if self.target.durability == 0:
                self.target.destroy()
                self.target.draw_tile()
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

    def draw_tank(tank):
        game.gameDisplay.blit(pg.transform.scale(tank.img, (int(tile_width), int(tile_height))),
                              tank.tile.get_screen_coords())
        if tank.has_flag:
            game.gameDisplay.blit(pg.transform.scale(tank.flag.img, (int(tile_width / 2), int(tile_height / 2))),
                                  tank.tile.get_screen_coords())

    def check_delivery(self):
        if self.tile.type == 'castle_zone' and self.has_flag:
            self.tile.deliver(self.flag)

    # [up, left, down, right]
    def move(self, move):
        new_tile = None
        self.last_move = move
        if np.array_equal(move, [1, 0, 0, 0]) and self.tile.y < grid_y - 1:
            new_tile = game.grid[self.tile.x, self.tile.y + 1]
        elif np.array_equal(move, [0, 0, 0, 1]) and self.tile.x < grid_x - 1:
            new_tile = game.grid[self.tile.x + 1, self.tile.y]
        elif np.array_equal(move, [0, 1, 0, 0]) and self.tile.x > 0:
            new_tile = game.grid[self.tile.x - 1, self.tile.y]
        elif np.array_equal(move, [0, 0, 1, 0]) and self.tile.y > 0:
            new_tile = game.grid[self.tile.x, self.tile.y - 1]
        if new_tile and new_tile.type in ('empty', 'castle_zone'):
            # manage prev tiles queue
            if self.prev_tiles.full():
                self.prev_tiles.get_nowait()
            self.prev_tiles.put_nowait((self.tile.x, self.tile.y))

            self.tile = new_tile
            if self.has_flag:
                self.flag.tile = new_tile
        else:
            game.lose()
        self.took_flag = False
        self.direction = move
        self.update_direction()
        self.get_target()
        self.pickup(self.tile)
        self.check_delivery()

    def pickup(self, tile):
        for item in tile.items:
            if isinstance(item, Flag):
                self.pickup_flag(item)

    def pickup_flag(self, flag):
        self.has_flag = True
        self.took_flag = True
        self.flag = flag
        flag.hide()

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
        game.flags.append(self)

    def show(self, tile):
        Pickup.show(self, tile)
        self.img = pg.image.load('img/flag_white.PNG')

    def hide(self):
        Pickup.hide(self)
        self.img = pg.image.load('img/flag.PNG')

    def draw_flag(self):
        if not self.picked_up:
            game.gameDisplay.blit(pg.transform.scale(self.img, (int(tile_width), int(tile_height))),
                                  self.tile.get_screen_coords())


pg.init()
agent = DQNAgent()
game = Game(epochs=1000)
game.run(agent)
now = datetime.datetime.now()
agent.model.save_weights('weights/weights_' + now.strftime("%Y-%m-%d_%H-%M-%S") + '.hdf5')
