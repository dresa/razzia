"""
Razzia! card game simulator.

https://boardgamegeek.com/boardgame/12589/razzia/

Implemented in Python 3.7, originally by Esa Junttila.
"""

__author__ = 'Esa Junttila'

import sys
import logging
import random

from control import Game
import agent


class Razzia:
    def __init__(self, num_players, random_seed=None):
        self._player_agents = ('Player A', 'Player B', 'Player C', 'Player D', 'Player E')
        self._player_agents = [agent.TrivialPlayerAgent(name) for name in self._player_agents[:num_players]]
        self._random_seed = random_seed
    def play_game(self):
        if self._random_seed:
            random.seed(self._random_seed)
        game = Game(self._player_agents)
        game.play_game()


def main(args):
    logging.basicConfig(level=logging.DEBUG)
    r = Razzia(4, random_seed=None)
    r.play_game()

if __name__ == '__main__':
    main(sys.argv[1:])
