#!/usr/bin/python

import random
import numpy as np
from copy import deepcopy


EMPTY = 0
PLAYER_X = 1
PLAYER_O = 2
DRAW = 3


class Board(object):

    FORMATTER = \
    "-------------\n" + \
    "| {0} | {1} | {2} |\n" + \
    "|-----------|\n" + \
    "| {3} | {4} | {5} |\n" + \
    "|-----------|\n" + \
    "| {6} | {7} | {8} |\n" + \
    "-------------"
    NAMES = [' ', 'X', 'O']

    def __init__(self):
        self.state = np.array([EMPTY] * 9)

    def act(self, move, player):
        self.state[move] = player

    def get_valid(self):
        return np.where(self.state == EMPTY)[0]

    def game_state(self):
        state_mat = self.state.reshape((3, 3))
        p1_win = [PLAYER_X] * 3
        p2_win = [PLAYER_O] * 3

        for i in range(3):
            # check rows
            row = state_mat[i, :]
            if np.all(row == p1_win) or np.all(row == p2_win):
                return state_mat[i, i]
            # check cols
            col = state_mat[:, i]
            if np.all(col == p1_win) or np.all(col == p2_win):
                return state_mat[i, i]
            
        # check first diagonal
        first_diag = state_mat.diagonal()
        if np.all(first_diag == p1_win) or np.all(first_diag == p1_win):
            return first_diag[0]
        # check second diagonal
        second_diag = np.fliplr(state_mat).diagonal()
        if np.all(second_diag == p1_win) or np.all(second_diag == p1_win):
            return second_diag[0]

        if len(state_mat == EMPTY) > 0:
            return EMPTY

        return DRAW

    def __str__(self):
        return Board.FORMATTER.format(*[Board.NAMES[s] for s in self.state])

    def __len__(self):
        return len(self.state)


class Agent(object):

    def __init__(self, player, verbose = False):
        self.player = player
        self.verbose = verbose
        self.epsilon = 0.1
        self.alpha = 0.95
        self.loose_reward = 0

        self.values = {}
        self.prev_board = None
        self.prev_value = 0

    def action(self, board):
        self.log('valid moves', board.get_valid())

        if random.random() > self.epsilon:
            # greedy action
            move, value = self.greedy(board)
        else:
            # exploratory action
            move, value = self.random(board)

        board.act(move, self.player)
        self.prev_board = deepcopy(board)
        self.prev_value = value
        return move

    def greedy(self, board):
        max_value = -1
        max_move = None

        for move in board.get_valid():
            board.act(move, self.player)
            value = self.lookup(board)
            if value > max_value:
                max_value = value
                max_move = move
            board.act(move, EMPTY)

        self.backup(max_value)
        return max_move, max_value

    def lookup(self, board):
        state_tpl = tuple(board.state)
        if not state_tpl in self.values:
            self.add(board)
        return self.values[state_tpl]

    def add(self, board):
        game_state = board.game_state()
        state_tpl = tuple(board.state)
        reward = self.reward(game_state)
        self.log('adding {0} -> {1}'.format(state_tpl, reward))
        self.values[state_tpl] = reward

    def reward(self, game_state):
        if game_state == self.player:
            return 1
        elif game_state == EMPTY:
            return 0.5
        elif game_state == DRAW:
            return 0
        else:
            return self.loose_reward

    def backup(self, next_value):
        if self.prev_board != None:
            prev_state = tuple(self.prev_board.state)
            delta = self.alpha * (next_value - self.prev_value)
            self.log('backing up', prev_state, 'by', delta)
            self.values[prev_state] += delta

    def random(self, board):
        move = random.choice(board.get_valid())
        board.act(move, self.player)
        value = self.lookup(board)
        return move, value

    def log(self, *what):
        if self.verbose:
            s = 'Player ' + str(self.player) + ':'
            print s, ' '.join(map(str, list(what)))


def play(agent1, agent2, modulo = 1):
    board = Board()

    for i in range(9):
        agent = agent1 if i % 2 == 0 else agent2
        
        move = agent.action(board)
        board.act(move, agent.player)

        if modulo != None and i % modulo == 0:
            print '\nBoard', i, '\n', board, '\n'

        game_state = board.game_state()
        if game_state != EMPTY:
            break

    return game_state, board


if __name__ == '__main__':
    
    agent1 = Agent(PLAYER_X)
    agent2 = Agent(PLAYER_O)

    for run in range(10):
        game_state, board = play(agent1, agent2, modulo = None)
        print 'Game %d ended %d\n%s' % (run, game_state, board)
