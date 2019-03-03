from enum import Enum


class AuctionMode(Enum):
    ByPlayer = 1
    ByFullBoard = 2
    ByPoliceman = 3


class Auction:
    def __init__(self, auction_mode, initiator, auctioned_cards, auctioned_cheque):
        self._auction_mode = auction_mode
        self._initiator = initiator
        self._highest_bid = None
        self._highest_bidder = None
        self._auctioned_cards = auctioned_cards
        self._auctioned_cheque = auctioned_cheque
    def set_highest_bid(self, bidded_cheque, bidder_state):
        if not bidder_state.has_cheque_available(bidded_cheque):
            raise Exception('Trying to bid a cheque that is not available.')
        if self._highest_bid and bidded_cheque <= self._highest_bid:
            raise Exception('Cheque is not able to outbid an existing bid.')
        self._highest_bid = bidded_cheque
        self._highest_bidder = bidder_state

    @property
    def auction_mode(self):
        return self._auction_mode
    @property
    def initiator(self):
        return self._initiator
    @property
    def highest_bid(self):
        return self._highest_bid
    @property
    def highest_bidder(self):
        return self._highest_bidder
    @property
    def auctioned_cards(self):
        return self._auctioned_cards
    @property
    def auctioned_cheque(self):
        return self._auctioned_cheque
