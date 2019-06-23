from enum import Enum
import random

class Board:
    def __init__(self, starting_cheque):
        self._cheque = starting_cheque
        self._cards = []
        self._num_policemen = 0
        self._discarded_booty = []
        self._num_discarded_policemen = 0

    def add_card(self, card):
        self._cards.append(card)
    def take_all_booty_cards(self):
        taken = self._cards
        self._cards = []
        return taken
    def take_booty_cards(self, cards_to_take):
        for c in cards_to_take:
            self._cards.remove(c)
        return cards_to_take
    def discard_booty_cards(self):
        self._discarded_booty.extend(self._cards)
        self._cards = []
    def add_policeman(self):
        self._num_policemen += 1
    def discard_policemen(self):
        self._num_discarded_policemen += self._num_policemen
        self._num_policemen = 0
    def replace_cheque(self, cheque):
        c = self._cheque
        self._cheque = cheque
        return c
    def get_cards(self):
        return self._cards[:]  # copy
    def get_card_counts(self):
        counts = {c: 0 for c in Card if c != Card.Policeman}
        for c in self._cards:
            counts[c] += 1
        return counts
    @property
    def num_cards(self):
        return len(self._cards)
    @property
    def num_policemen(self):
        return self._num_policemen
    @property
    def num_discarded_policemen(self):
        return self._num_discarded_policemen
    @property
    def cheque(self):
        return self._cheque
    def __str__(self):
        s  = 'BOARD:\n'
        s += '  Cheque {}, Policemen {}\n'.format(self._cheque, self._num_policemen)
        s += '  {} booty cards: {}\n'.format(len(self._cards), ', '.join(str(c) for c in self._cards))
        s += '  Discarded {} policemen and {} booty cards: {}\n'.format(self._num_discarded_policemen, len(self._discarded_booty), ', '.join(str(c) for c in self._discarded_booty))
        return s


class Deck:
    def __init__(self):
        counts = {c : c.how_many for c in Card}
        batches = [[c] * c.how_many for c in Card]
        cards = [c for sublist in batches for c in sublist]
        random.shuffle(cards)
        self._cards = cards
        self._counts = counts
    def draw(self):
        if self._cards:
            card = self._cards.pop()
            self._counts[card] = self._counts[card] - 1
            return card
        else: raise Exception('Trying to draw from an empty deck.')
    def size(self):
        return len(self._cards)
    def count(self, card_type):
        return self._counts[card_type]
    def __str__(self):
        s = 'Deck size {} with contents:\n'.format(self.size())
        s += '\n'.join('  {} ({})'.format(k, v) for k, v in self._counts.items())
        return s


class Card(Enum):
    def __init__(self, id, how_many, is_trinket, is_business, permanent):
        self.how_many = how_many
        self.is_trinket = is_trinket
        self.is_business = is_business
        self.permanent = permanent
    def __str__(self):
        return self.name
    Policeman     =( 1, 21, False, False, False)
    Ring          =( 2,  4, True,  False, False)
    Watch         =( 3,  4, True,  False, False)
    Brooch        =( 4,  4, True,  False, False)
    Chain         =( 5,  4, True,  False, False)
    Diamond       =( 6,  4, True,  False, False)
    Bodyguard     =( 7, 16, False, False, True)
    Car           =( 8, 16, False, False, True)
    Driver        =( 9, 10, False, False, False)
    Thief         =(10,  6, False, False, False)
    GoldCoin      =(11,  3, False, False, False)
    Casino        =(12,  4, False, True,  True)
    Transportation=(13,  4, False, True,  True)
    Film          =(14,  4, False, True,  True)
    HorseRacing   =(15,  4, False, True,  True)
    RealEstate    =(16,  4, False, True,  True)
    NightClub     =(17,  4, False, True,  True)
    Restaurant    =(18,  4, False, True,  True)

TRINKET_CARDS = [c for c in Card if c.is_trinket]
REMOVABLE_CARDS = [c for c in Card if not c.permanent]
BUSINESS_CARDS = [c for c in Card if c.is_business]


class Cheque(Enum):
    def __str__(self):
        return 'Cheque({})'.format(self.value)
    def __eq__(self, other):
        return self.value == other.value
    def __lt__(self, other):
        return self.value < other.value
    def __le__(self, other):
        return self.value <= other.value
    def __hash__(self):
        return hash(self.value)
    One=1
    Two=2
    Three=3
    Four=4
    Five=5
    Six=6
    Seven=7
    Eight=8
    Nine=9
    Ten=10
    Eleven=11
    Twelve=12
    Thirteen=13
    Fourteen=14
    Fifteen=15
    Sixteen=16


##
## Cheque sets at the start of the game.
##

CHEQUE_STARTING = Cheque.One

CHEQUES_PLAYER_A_FOR_2 = [Cheque.Two, Cheque.Five, Cheque.Six, Cheque.Nine]
CHEQUES_PLAYER_B_FOR_2 = [Cheque.Three, Cheque.Four, Cheque.Seven, Cheque.Eight]
CHEQUES_FOR_2 = [CHEQUES_PLAYER_A_FOR_2[:], CHEQUES_PLAYER_B_FOR_2[:]]

CHEQUES_PLAYER_A_FOR_3 = [Cheque.Two, Cheque.Five, Cheque.Eight, Cheque.Thirteen]
CHEQUES_PLAYER_B_FOR_3 = [Cheque.Three, Cheque.Six, Cheque.Nine, Cheque.Twelve]
CHEQUES_PLAYER_C_FOR_3 = [Cheque.Four, Cheque.Seven, Cheque.Ten, Cheque.Eleven]
CHEQUES_FOR_3 = [CHEQUES_PLAYER_A_FOR_3[:], CHEQUES_PLAYER_B_FOR_3[:], CHEQUES_PLAYER_C_FOR_3[:]]

CHEQUES_PLAYER_A_FOR_4 = [Cheque.Two, Cheque.Six, Cheque.Thirteen]
CHEQUES_PLAYER_B_FOR_4 = [Cheque.Three, Cheque.Seven, Cheque.Twelve]
CHEQUES_PLAYER_C_FOR_4 = [Cheque.Four, Cheque.Eight, Cheque.Eleven]
CHEQUES_PLAYER_D_FOR_4 = [Cheque.Five, Cheque.Nine, Cheque.Ten]
CHEQUES_FOR_4 = [CHEQUES_PLAYER_A_FOR_4[:], CHEQUES_PLAYER_B_FOR_4[:], CHEQUES_PLAYER_C_FOR_4[:], CHEQUES_PLAYER_D_FOR_4[:]]

CHEQUES_PLAYER_A_FOR_5 = [Cheque.Two, Cheque.Seven, Cheque.Sixteen]
CHEQUES_PLAYER_B_FOR_5 = [Cheque.Three, Cheque.Eight, Cheque.Fifteen]
CHEQUES_PLAYER_C_FOR_5 = [Cheque.Four, Cheque.Nine, Cheque.Fourteen]
CHEQUES_PLAYER_D_FOR_5 = [Cheque.Five, Cheque.Ten, Cheque.Thirteen]
CHEQUES_PLAYER_E_FOR_5 = [Cheque.Six, Cheque.Eleven, Cheque.Twelve]
CHEQUES_FOR_5 = [CHEQUES_PLAYER_A_FOR_5[:], CHEQUES_PLAYER_B_FOR_5[:], CHEQUES_PLAYER_C_FOR_5[:], CHEQUES_PLAYER_D_FOR_5[:], CHEQUES_PLAYER_E_FOR_5[:]]
