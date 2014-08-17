from random import choice
import time
from game import Game, AIM
import json
import itertools
import math


# Player Parameters Weights

ENEMY_LIFE_OFFSET = 21

ENEMY_WEAK_SCALE = 0.5
ENEMY_WEAK_CENTRAL_RADIUS = 0.2
ENEMY_WEAK_RADIAL_RADIUS = 0.0

ENEMY_STRONG_SCALE = 1.0
ENEMY_STRONG_CENTRAL_RADIUS = 0.2
ENEMY_STRONG_RADIAL_RADIUS = 0.8

MINE_STRENGTH = 64
MINE_RADIUS = 0.9
MINE_HERO_LIFE_OFFSET = 20

TAVERN_SCALE = 1.0
TAVERN_OFFSET = 0.0
TAVERN_RADIUS = 0.8


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


class GradientBot:

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
            if(player.pos != self.game.hero.pos):
                pos = (player.pos['x'], player.pos['y'])
                enemyScore = -(player.life + ENEMY_LIFE_OFFSET - self.game.hero.life)
                if enemyScore < 0:
                    enemyScore = enemyScore * ENEMY_STRONG_SCALE
                    self.heurAddWeight(pos, enemyScore*2, ENEMY_STRONG_CENTRAL_RADIUS)
                    self.heurAddWeight(pos, enemyScore, ENEMY_STRONG_RADIAL_RADIUS)
                else:
                    enemyScore = enemyScore * ENEMY_WEAK_SCALE
                    self.heurAddWeight(pos, enemyScore*2, ENEMY_WEAK_CENTRAL_RADIUS)
                    self.heurAddWeight(pos, enemyScore, ENEMY_WEAK_RADIAL_RADIUS)

        # Go After Mines if Enough Life
        for mine in self.game.mines_locs:
            if self.game.mines_locs[mine] == '-' or int(self.game.mines_locs[mine]) != int(self.game.heroid):
                mineStrength = (self.game.hero.life - MINE_HERO_LIFE_OFFSET) * MINE_STRENGTH
                # Mines should only be good
                if mineStrength > 0:
                    self.heur[mine[1]][mine[0]] += mineStrength
                    self.heurAddWeight(mine, mineStrength/2, MINE_RADIUS)
            else:
                pass #self.heurAddWeight(mine, -64, 0.85)


        tavernScore = (100 - self.game.hero.life) * TAVERN_SCALE - TAVERN_OFFSET
        # Taverns should only be good
        if tavernScore > 0:
            for tavern in self.game.taverns_locs:
                self.heur[tavern[1]][tavern[0]] += tavernScore
                self.heurAddWeight(tavern, tavernScore/2.0, TAVERN_RADIUS)


    def heurAddWeight(self, pos, strength, decay):
        dim = self.game.board.size
        wildfire = dict()
        for x in list(itertools.product(*[xrange(dim),xrange(dim)])):
            wildfire[x] = 0

        firespaces = []
        def addWildFire(pos, strength, force = False):
            if force or (self.game.board.passable(pos) and wildfire[pos] == 0):
                # decayAdditional = 1.0 if self.game.board.passable(pos) else 0.7
                firespaces.append(((pos[0], pos[1]), strength))
                wildfire[pos] = 1

        addWildFire(pos, strength, True)
        while len(firespaces) > 0:
            fire = firespaces.pop(0)
            pos = fire[0]
            if wildfire[pos] == 2:
                continue
            wildfire[pos] = 2
            self.heur[pos[1]][pos[0]] += fire[1]
            # Spread the File
            for direction in AIM:
                offset = AIM[direction]
                newPos = (pos[0] + offset[0], pos[1] + offset[1])
                if 0 <=  newPos[0] < dim and 0 <= newPos[1] < dim:
                    addWildFire(newPos, fire[1]*decay)


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

        curPos = self.game.hero.pos

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
