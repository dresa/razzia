from pieces import Card

class GameView:
    def __init__(self, game, active_player, all_players, board):
        self._game_state = game
        self._active_player = active_player
        self._all_players = all_players
        self._board = board
        from agent import PlayerAgent
        if isinstance(active_player, PlayerAgent):
            raise Exception('wrong type of arg: got PlayerAgent instead of player')

    def get_active_player_view(self):
        return PlayerView(self._active_player)
    def get_all_player_views(self):
        return [PlayerView(p) for p in self._all_players]
    def get_board_view(self):
        return BoardView(self._board)
    @property
    def rounds_remaining(self):
        return self._game_state.rounds_remaining

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
        from agent import PlayerAgent
        if isinstance(player, PlayerAgent):
            raise Exception('wrong type of arg: got PlayerAgent instead of player')
    def available_cheques(self):
        return self._player.available_cheques()  # copy
    def num_available_thieves(self):
        return self._player.num_cards(Card.Thief)
    @property
    def highest_cheque(self):
        return self._player.highest_cheque
    def card_counts(self):
        return self._player.card_counts()  # copy
    def is_same_player(self, player):
        return player == self._player

class BoardView:
    def __init__(self, board):
        self._board = board
    def card_counts(self):
        return self._board.get_card_counts()  # copy


