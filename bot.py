from random import choice
import time
from game import Game
import json

import math

def sigdist(x, mean, sd):
    return 1.0 / (1.0 + math.exp(x*sd))


def normpdf(x, mean, sd):
    var = float(sd)**2
    pi = 3.1415926
    denom = var * ((2*pi)**.5)
    v = -(float(x)-float(mean))**2
    if v == 0:
        v = 0.01
    num = math.exp(v)/(2*var)
    return num/denom


class GradientBot(Bot):

    def __init__(self):
        self.name = None
        self.heur = None
        self.game = None

    def checkHeur(self):
        dim = self.game.board.size
        self.heur = [[0 for x in xrange(dim)] for x in xrange(dim)] 

    def updateHeur(self):
        # Try To Avoid Other Players
        for player in self.game.heroes:
            if(player.pos != self.game.hero["pos"]):
                self.heurAddWeight(player.pos, -64, 0.7)

        for mine in self.game.mines_locs:
            pos = dict(y=mine[1], x=mine[0])
            if self.game.mines_locs[mine] == '-' or int(self.game.mines_locs[mine]) != int(self.game.hero['id']):
                self.heurAddWeight(pos, 64, 0.7)
            else:
                self.heurAddWeight(pos, -64, 2)


    def heurAddWeight(self, pos, strength, dist):
        maxpdf = sigdist(0, 0, dist)
        for y in xrange(self.game.board.size):
            for x in xrange(self.game.board.size):
                d = math.sqrt((y - pos['y'])**2 + (x - pos['x'])**2)
                s = (sigdist(d, 0, dist)  / maxpdf) * strength
                self.heur[y][x] += s


    def move(self, state):
        self.game = Game(state)
        self.checkHeur()
        self.updateHeur()

        moves = dict(
            Stay = (0,0),
            North = (-1, 0),
            South = (1, 0),
            East = (0, 1),
            West = (0, -1),
        )

        curPos = self.game.hero['pos']

        maxScore = None
        maxDir = None
        for direction in moves:
            move = moves[direction]
            y = curPos['y'] + move[1]
            if y < 0 or y > 9:
                continue
            x = curPos['x'] + move[0]
            if x < 0 or x > 9:
                continue
            val = self.heur[y][x]
            if maxScore is None or val > maxScore:
                maxScore = val
                maxDir = direction
            print str(y) + ", " + str(x) + " : " + direction + " : " + str(val)

        dirs = ['Stay', 'North', 'South', 'East', 'West']
        return maxDir
