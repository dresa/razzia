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
    DEFAULT_PLAYER_NAMES = ('Player A', 'Player B', 'Player C', 'Player D', 'Player E')

    def __init__(self, num_players, ai=None, random_seed=None):
        self._player_agents = Razzia.DEFAULT_PLAYER_NAMES
        if ai is None or ai.lower() == 'trivial':
            ai_agent = agent.TrivialPlayerAgent
        elif ai.lower() == 'stealing':
            ai_agent = agent.StealingPlayerAgent
        else:
            raise Exception('Unknown AI player setup: {}'.format(ai))
        self._player_agents = [ai_agent(name) for name in self._player_agents[:num_players]]
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
        print(analytics.analyze_cheque_value(multi_scorings))
    def print_scores(self, scorings):
        print('Detailed scores:\n' + '\n'.join(str(s) for p, s in scorings.items()))
        print('Accumulated card scores: ' + ', '.join('"{}" = {}'.format(p, s.final_accumulated_card_score()) for p, s in scorings.items()))
        print('Adjusted card scores: ' + ', '.join('"{}" = {}'.format(p, s.final_adjusted_card_score()) for p, s in scorings.items()))
        print('Cheque scores: ' + ', '.join('"{}" = {}'.format(p, s.final_cheque_score()) for p, s in scorings.items()))
        print('Total scores: ' + ', '.join('"{}" = {}'.format(p, s.final_score()) for p, s in scorings.items()))


def main(args):
    logging.basicConfig(level=logging.INFO)
    r = Razzia(4, ai='stealing', random_seed=1)
    scorings = r.play_game()
    r.print_scores(scorings)
    r.run_statistics(1000)

if __name__ == '__main__':
    main(sys.argv[1:])
