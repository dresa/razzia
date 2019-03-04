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
import analytics


class Razzia:
    def __init__(self, num_players, random_seed=None):
        self._player_agents = ('Player A', 'Player B', 'Player C', 'Player D', 'Player E')
        self._player_agents = [agent.TrivialPlayerAgent(name) for name in self._player_agents[:num_players]]
        self._random_seed = random_seed
    def _play_one_game(self):
        return Game(self._player_agents).play_game()
    def play_game(self):
        if self._random_seed:
            random.seed(self._random_seed)
        return self._play_one_game()
    def run_statistics(self, num_games):
        if self._random_seed:
            random.seed(self._random_seed)
        multi_scorings = [self._play_one_game() for _ in range(num_games)]
        print(analytics.analyze_player_order(multi_scorings))
        print(analytics.analyze_card_value(multi_scorings))




def main(args):
    logging.basicConfig(level=logging.INFO)
    r = Razzia(4, random_seed=1)
    r.play_game()
    #r.run_statistics(100)

if __name__ == '__main__':
    main(sys.argv[1:])
