import random
from control import ActionType


class PlayerAgent:
    def __init__(self, name):
        self._name = name
    def act(self, game_view):
        raise NotImplementedError('Cannot use base PlayerAgent as agent: implement "act()" in derived class.')
    def bid(self, game_view, auction_view, player_view, is_mandated):
        raise NotImplementedError('Cannot use base PlayerAgent as agent: implement "bid()" in derived class.')
    def __str__(self):
        return self._name


class TrivialPlayerAgent(PlayerAgent):
    def act(self, game_view):
        return ActionType.Draw  # FIXME
    def bid(self, game_view, auction_view, player_view, is_mandated):
        bid_probs = {0: 0.05, 1: 0.15, 2: 0.30, 3: 0.50, 4: 0.65, 5: 0.75, 6: 0.85, 7: 0.95}
        prob = bid_probs[len(auction_view.auctioned_cards)]
        willing_to_bid = random.random() < prob
        if willing_to_bid:
            # always bid the lowest cheque that exceeds current highest bid
            cheques = player_view.available_cheques()
            top = auction_view.highest_bid
            if top:
                exceeding_cheques = [c for c in cheques if c > top]
                return min(exceeding_cheques)
            else:
                return min(cheques)
