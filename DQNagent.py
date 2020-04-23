from keras.optimizers import Adam
from keras.models import Sequential
from keras.layers.core import Dense, Dropout
import random
import numpy as np
import pandas as pd
from operator import add

READ_WEIGHTS = False

class DQNAgent(object):

    def __init__(self):
        self.reward = 0
        self.gamma = 0.9
        self.short_memory = np.array([])
        self.agent_target = 1
        self.agent_predict = 0
        self.learning_rate = 0.0005
        if READ_WEIGHTS:
            self.model = self.network("weights.hdf5")
        else:
            self.model = self.network()
        self.epsilon = 100
        self.actual = []
        self.memory = []

    def get_state(self, game, tank, flag, castle):
        # state:
        # flag: left right top bot in_inventory
        # base left right top bot
        # last move: left right top bot
        state = [int(flag.tile.x < tank.tile.x),  #flag is in left direction
                 int(flag.tile.x > tank.tile.x),  #flag is in right direction
                 int(flag.tile.y > tank.tile.y),  #flag is in top direction
                 int(flag.tile.y < tank.tile.y),  #flag is in bottom direction

                 int(tank.tile.x - 1 < 0 or not game.grid[tank.tile.x-1, tank.tile.y].type in ('empty', 'castle_zone')),  # obstacle is in left direction
                 int(tank.tile.x + 1 > game.grid_x - 1 or not game.grid[tank.tile.x+1, tank.tile.y].type in ('empty', 'castle_zone')),  # obstacle is in right direction
                 int(tank.tile.y + 1 > game.grid_y - 1 or not game.grid[tank.tile.x, tank.tile.y+1].type in ('empty', 'castle_zone')),  # obstacle is in top direction
                 int(tank.tile.y - 1 < 0 or not game.grid[tank.tile.x, tank.tile.y-1].type in ('empty', 'castle_zone')),  # obstacle is in bottom direction

                 int(tank.has_flag and tank.flag == flag),  # flag is picked up

                 int(castle.x < tank.tile.x),  # castle is in left direction
                 int(castle.x > tank.tile.x),  # castle is in right direction
                 int(castle.y > tank.tile.y),  # castle is in top direction
                 int(castle.y < tank.tile.y)  # castle is in bottom direction
                 ]

        state.extend(tank.last_move) # last move: [up, left, down, right]

        return np.asarray(state)

    def network(self, weights=None):
        model = Sequential()
        model.add(Dense(output_dim=120, activation='relu', input_dim=17))
        model.add(Dropout(0.15))
        model.add(Dense(output_dim=120, activation='relu'))
        model.add(Dropout(0.15))
        model.add(Dense(output_dim=120, activation='relu'))
        model.add(Dropout(0.15))
        model.add(Dense(output_dim=4, activation='softmax'))
        opt = Adam(self.learning_rate)
        model.compile(loss='mse', optimizer=opt)

        if weights:
            model.load_weights(weights)
        return model

    def replay_new(self, memory):
        if len(memory) > 1000:
            minibatch = random.sample(memory, 1000)
        else:
            minibatch = memory
        for state, action, reward, next_state, loss in minibatch:
            target = reward
            if not loss:
                target = reward + self.gamma * np.amax(self.model.predict(np.array([next_state]))[0])
            target_f = self.model.predict(np.array([state]))
            target_f[0][np.argmax(action)] = target
            self.model.fit(np.array([state]), target_f, epochs=1, verbose=0)

    def set_reward(self, tank, game):
        self.reward = 0
        if (tank.tile.x, tank.tile.y) in list(tank.prev_tiles.queue):
            self.reward = -1
            print('Backtracking! reward: ', self.reward)
        if tank.took_flag:
            self.reward = 5
            print('Took flag! reward: ', self.reward)
        if game.victory:
            self.reward = 50
            print('Delivered flag! reward: ', self.reward)
        elif game.loss:
            self.reward = -10
            print('Crashed! reward: ', self.reward)
        return self.reward

    def remember(self, state, action, reward, next_state, loss):
        self.memory.append((state, action, reward, next_state, loss))
        # print(len(self.memory))

    def train_short_memory(self, state, action, reward, next_state, loss):
        target = reward
        if not loss:
            target = reward + self.gamma * np.amax(self.model.predict(next_state.reshape((1, 17)))[0])
        target_f = self.model.predict(state.reshape((1, 17)))
        target_f[0][np.argmax(action)] = target
        self.model.fit(state.reshape((1, 17)), target_f, epochs=1, verbose=0)
