class GameView:
    def __init__(self, game, active_player):
        self._game_state = game
        self._active_player = active_player

class AuctionView:
    def __init__(self, auction):
        self._auction = auction
    @property
    def auctioned_cards(self):
        return self._auction.auctioned_cards
    @property
    def highest_bid(self):
        return self._auction.highest_bid

class PlayerView:
    def __init__(self, player):
        self._player = player
    def available_cheques(self):
        return self._player.available_cheques()  # copy
