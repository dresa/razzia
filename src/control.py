from enum import Enum
import itertools
import logging

from auction import Auction, AuctionMode
from agentview import AuctionView, GameView, PlayerView

from player import Player
from pieces import Deck, Card, Board
from pieces import CHEQUE_STARTING, CHEQUES_FOR_2, CHEQUES_FOR_3, CHEQUES_FOR_4, CHEQUES_FOR_5


GAME_ROUNDS = 3
ROUND_END_POLICEMEN = 7
ROUND_END_POLICEMEN_TWOPLAYER = 5
AUTOMATIC_AUCTION_NUM_CARDS = 7


class ActionType(Enum):
    Draw=1
    AuctionByPlayer=2
    Thief=3


class Trigger(Enum):
    Turn=1
    Round=2
    Game=3


class TurnOrder:
    def __init__(self, items, fn_init_pred):
        self._items = items
        self._predicate = fn_init_pred
    def _current_idx(self, initiator):
        return next(idx for idx, item in enumerate(self._items) if self._predicate(item, initiator))
    def _next_idx(self, item_idx):
        n = len(self._items)
        return (item_idx + 1) % n
    def next(self, item):
        init_idx = self._current_idx(item)
        next_idx = self._next_idx(init_idx)
        return self._items[next_idx]
    def circling_from(self, item):
        i = self._current_idx(item)
        while True:
            yield self._items[i]
            i = self._next_idx(i)
    def one_circle_from_next(self, item):
        n = len(self._items)
        return list(itertools.islice(self.circling_from(item), n + 1))[1:(n+1)]


class Game:
    def __init__(self, player_agents):
        n = len(player_agents)
        if not 2 <= n <= 5:
            raise Exception('Unsupported number of players: {}'.format(player_agents))
        cheques = {2: CHEQUES_FOR_2[:], 3: CHEQUES_FOR_3[:], 4: CHEQUES_FOR_4[:], 5: CHEQUES_FOR_5[:]}
        players = [Player(p, cs) for p, cs in zip(player_agents, cheques[n])]
        self._players = players
        self._deck = Deck()
        self._board = Board(CHEQUE_STARTING)
        self._round = 1
        self._round_end_policemen = ROUND_END_POLICEMEN if n > 2 else ROUND_END_POLICEMEN_TWOPLAYER
        self._end = False
        self._round_order_generator = TurnOrder(self._players, lambda x, y: x.player_agent == y.player_agent)

    def _execute_winning_bid(self, bidder, bid_cheque, board):
        cheque_ordinal = bidder.num_unavailable_cheques + 1
        new_cards = board.take_booty_cards()
        bidder.gain_cards(new_cards, self._round, bid_cheque, cheque_ordinal)
        gained_cheque = board.cheque
        bidder.remove_available_cheque(bid_cheque)
        bidder.add_unavailable_cheque(gained_cheque)
        board.replace_cheque(bid_cheque)
        logging.debug('  {} wins the auction:'.format(bidder.player_agent))
        logging.debug('    loses cheque {}'.format(bid_cheque))
        logging.debug('    gains cheque {} (as unavailable)'.format(gained_cheque))
        logging.debug('    gains cards: {}'.format(', '.join(c.name for c in new_cards)))

    def _execute_auction(self, auction_mode, initiator, board):
        auction = Auction(auction_mode, initiator, board.get_cards(), board.cheque)
        for player in self._round_order_generator.one_circle_from_next(auction.initiator):
            top = auction.highest_bid
            agent = player.player_agent
            if player.round_is_over:
                logging.debug('  {} PASSes bid because no cheques are available.'.format(agent))
                continue
            avail_cheques_str = ','.join(str(c) for c in player.available_cheques())
            if top and player.highest_cheque < top:
                logging.debug('  {} PASSes bid because cannot outbid (had {} available).'.format(agent, avail_cheques_str))
                continue
            is_mandated = auction.auction_mode == AuctionMode.ByPlayer and player == auction.initiator
            game_view = GameView(self, agent)
            auction_view = AuctionView(auction)
            player_view = PlayerView(player)
            bidded_cheque = player.player_agent.bid(game_view, auction_view, player_view, is_mandated)
            if bidded_cheque:
                logging.debug('  {} BIDs with cheque {} (had {} available).'.format(agent, bidded_cheque, avail_cheques_str))
                auction.set_highest_bid(bidded_cheque, player)
            elif is_mandated:
                raise Exception('Missing mandated bid.')
            else:
                logging.debug('  {} PASSes bid deliberately (had {} available).'.format(agent, avail_cheques_str))
        if auction.highest_bid:
            self._execute_winning_bid(auction.highest_bidder, auction.highest_bid, board)
        else:
            logging.debug('  No bids in this auction.')

    def _execute_auction_by_full_board(self, initiator):
        logging.debug('Starting an Auction (by full board)')
        highest_bidder = self._execute_auction(AuctionMode.ByFullBoard, initiator, self._board)
        if not highest_bidder:
            self._board.discard_booty_cards()
    def _execute_auction_by_player(self, initiator):
        pass  # FIXME
    def _execute_auction_by_policeman(self, initiator):
        logging.debug('Starting an Auction (by Policeman)')
        self._execute_auction(AuctionMode.ByPoliceman, initiator, self._board)
    def _execute_draw(self, initiator):
        card = self._deck.draw()
        logging.debug('Player agent {} DRAWs a card: {}'.format(initiator.player_agent, card))
        if card == Card.Policeman:
            self._board.add_policeman()
            logging.debug(  'added policeman (total {})'.format(self._board.num_policemen))
            is_instant_round_end = self._board.num_policemen == self._round_end_policemen
            if is_instant_round_end:
                logging.debug('Policemen limit reached.')
                if not self.last_round:
                    logging.debug('Round ends with {} cards in deck remaining.'.format(self._deck.size()))
                self._board.discard_booty_cards()
                self._board.discard_policemen()
                return Trigger.Round
            else:
                self._execute_auction_by_policeman(initiator)
                return Trigger.Turn
        else:
            self._board.add_card(card)
            board_is_full = self._board.num_cards == AUTOMATIC_AUCTION_NUM_CARDS
            if board_is_full:
                self._execute_auction_by_full_board(initiator)
            return Trigger.Turn

    def _advance_round(self):
        self._round += 1

    def _determine_starting_player(self):
        return max([p for p in self._players], key=lambda x: x.highest_cheque)

    def _play_one_turn(self, player):
        action = player.player_agent.act(GameView(self, player))
        logging.debug('{} chooses {}'.format(player.player_agent, action))
        t = type(action)
        if t == tuple or t == list:  # Thieves?
            pass  # FIXME: complete "Thief" action
        elif action == ActionType.Draw:
            return self._execute_draw(player)
        elif action == ActionType.AuctionByPlayer:
            return self._execute_auction_by_player(player)
        else:
            raise Exception('Unexpected action: {}'.format(action))

    def _score_round(self):
        nums_bodyguards = [player.num_bodyguards for player in self._players]
        for player in self._players:
            player.do_round_scoring(min(nums_bodyguards), max(nums_bodyguards))

    def _play_round(self, round_number):
        logging.debug('-------')
        logging.debug('Round {}'.format(round_number))
        logging.debug('-------')
        for player in self._players:
            player.refresh_cheques()
        starting_player = self._determine_starting_player()
        consecutive_passes = 0
        for player in self._round_order_generator.circling_from(starting_player):
            if player.round_is_over:
                logging.debug('Player agent {} passed (out of round).'.format(player.player_agent))
                consecutive_passes += 1
                if consecutive_passes < self.num_players:
                    continue
                else:
                    logging.debug('All cheques have been used.')
                    break
            consecutive_passes = 0
            trigger = self._play_one_turn(player)
            #logging.debug(player)
            #logging.debug(self._board)
            if trigger == Trigger.Round:
                break

    def _is_game_end_valid(self):
        expected_cards = sum([c.how_many for c in Card])
        deck_cards = self._deck.size()
        policemen = self._board.num_policemen
        discarded_booty_cards = len(self._board._discarded_booty)
        discarded_policemen = self._board._num_discarded_policemen
        player_cards = sum([len(p._cards) for p in self._players])
        player_scored_cards = sum([len(p._scored_cards) for p in self._players])
        num_cards = deck_cards + discarded_booty_cards + policemen + discarded_policemen + player_cards + player_scored_cards
        if num_cards != expected_cards:
            raise Exception('Unexpected number of cards at game end: expected {}, but had {}.'.format(expected_cards, num_cards))
        counted_player_cards = sum(v for p in self._players for k, v in p._counts.items())
        counted_cards = deck_cards + discarded_booty_cards + policemen + discarded_policemen + counted_player_cards + player_scored_cards
        if counted_cards != expected_cards:
            raise Exception('Unexpected card counts at game end: expected {}, but had {}.'.format(expected_cards, counted_cards))

    def _score_game_end(self):
        cheque_totals = [player.cheque_total for player in self._players]
        for player in self._players:
            player.do_game_end_scoring(min(cheque_totals), max(cheque_totals))

    def _get_player_scorings(self):
        return {player.player_agent: player.get_final_scoring() for player in self._players}

    def play_game(self):
        if self._end:
            raise Exception('Game has already ended.')
        logging.debug('===============================')
        logging.debug('Starting Razzia! with {} players'.format(self.num_players))
        logging.debug('===============================')
        for r in range(1, GAME_ROUNDS + 1):
            self._play_round(r)
            self._score_round()
            self._advance_round()
        logging.debug('Game ends with {} cards in deck remaining.'.format(self._deck.size()))
        self._end = True
        self._score_game_end()
        logging.debug('==============')
        logging.debug('Game has ended')
        logging.debug('==============')
        self._is_game_end_valid()
        scorings = self._get_player_scorings()
        return scorings

    def auctioned_cards(self):
        return len(self._board.get_cards())

    @property
    def num_players(self):
        return len(self._players)

    @property
    def last_round(self):
        return self._round == GAME_ROUNDS

    @property
    def end(self):
        return self._end
