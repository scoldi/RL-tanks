import pygame as pg
import numpy as np
import random
from keras.utils import to_categorical
from DQNagent import DQNAgent

pg.font.init()
pg.display.init()
###
MANUAL_MODE = False
speed = 150
###
GAMES_TOTAL = 100
GAMES_ELAPSED = 0
win_count = 0
lose_count = 0
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

tanks = []
flags = []
castles = []
tile_img_paths = {'empty': None, 'water': 'img/water.png', 'ground': 'img/ground.png', 'brick': 'img/brick.png',
                'castle': 'img/castle.png'}
tile_durabilities = {'empty': 0, 'water': 0, 'ground': 2, 'brick': 4, 'castle': 1, 'castle_zone': 0}

BG_COLOR = (240, 240, 240)


class Game:

    def __init__(self):
        pg.display.set_caption('tanks or whatever')
        self.gameDisplay = pg.display.set_mode((window_width, window_height))
        self.gameDisplay.fill(BG_COLOR)
        #self.screen_area = pg.Rect(0, 0, screen_width, screen_height)
        #self.info_area = pg.Rect((screen_width + 25, screen_height + 25),
        #                         (window_width - screen_width - 50, window_height - screen_height - 50))
        self.running = True
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.ended = False
        self.victory = False
        self.loss = False
        self.grid = np.zeros((grid_x, grid_y), dtype=Tile)
        pg.display.update()

    def win(self):
        global win_count
        win_count += 1
        print('win')
        self.victory = True
        self.running = False
        self.ended = True

    def lose(self):
        global lose_count
        lose_count += 1
        print('lose')
        self.loss = True
        self.running = False
        self.ended = True


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
        castles.append(self)

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
        self.ammo = []
        self.target = None
        self.took_flag = False
        self.has_flag = False
        self.flag = None
        self.get_target()
        tanks.append(self)

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

    def check_delivery(self):
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

def draw_info():
    games_textsurface = info_font.render('Game:' + str(GAMES_ELAPSED + 1) + '/' + str(GAMES_TOTAL), False, (0, 0, 0))
    wl_textsurface = info_font.render('W/L:' + str(win_count) + '/' + str(lose_count), False, (0, 0, 0))
    game.gameDisplay.blit(games_textsurface, (screen_width + 80, 50))
    game.gameDisplay.blit(wl_textsurface, (screen_width + 80, 100))

def draw_flag(flag):
    if not flag.picked_up:
        game.gameDisplay.blit(pg.transform.scale(flag.img, (int(tile_width), int(tile_height))), flag.tile.get_screen_coords())


def init_world():
    clear()
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
    flag = Flag(game.grid[random.randint(0, grid_x - 1), random.randint(int(grid_y / 2), grid_y - 1)])
    tank = Tank(1, game.grid[random.randint(0, grid_x - 1), random.randint(1, int(grid_y / 2))], [1, 0, 0, 0])
    update_screen()


def clear():
    global tanks
    global flags
    global castles
    tanks = []
    flags = []
    castles = []


def draw_world():
    for col in game.grid:
        for tile in col:
            draw_tile(tile)


def draw_tile(tile, show_durability = True):
    game.gameDisplay.blit(pg.transform.scale(tile.img, (int(tile_width), int(tile_height))), (tile.get_screen_coords()))
    if tile.durability > 0 and show_durability:
        textsurface = tile_font.render(str(tile.durability), False, (255, 0, 0))
        game.gameDisplay.blit(textsurface, tile.get_screen_coords())


def update_screen():
    # game.gameDisplay.fill((255,255,255))
    draw_world()
    draw_info()
    for tank in tanks:
        draw_tank(tank)
    for flag in flags:
        draw_flag(flag)
    pg.display.update()


def run(agent=None):
    pg.init()
    init_world()
    global GAMES_ELAPSED
    while game.running:
        if MANUAL_MODE:
            for tank in tanks:
                tank.enable_manual_controls()
        else:
            agent.epsilon = 30 - GAMES_ELAPSED
            state_old = agent.get_state(game, tanks[0], flags[0], castles[0])
            # perform random actions based on agent.epsilon, or choose the action
            if random.randint(0, 200) < agent.epsilon:
                move = to_categorical(random.randint(0, 3), num_classes=4)
            else:
                # predict action based on the old state
                prediction = agent.model.predict(state_old.reshape((1, 17)))
                move = to_categorical(np.argmax(prediction[0]), num_classes=4)
            tanks[0].move(move)

            state_new = agent.get_state(game, tanks[0], flags[0], castles[0])

            reward = agent.set_reward(tanks[0], game)

            # train short memory base on the new action and state
            agent.train_short_memory(state_old, move, reward, state_new, game.loss)

            # store the new data into a long term memory
            agent.remember(state_old, move, reward, state_new, game.loss)
            pg.time.wait(speed)



        update_screen()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                game.running = False
                pg.quit()
        if game.ended:
            GAMES_ELAPSED += 1
            if not MANUAL_MODE:
                agent.replay_new(agent.memory)
            break


agent = DQNAgent()
while GAMES_ELAPSED < GAMES_TOTAL:
    game = Game()
    game.running = True
    run(agent)
