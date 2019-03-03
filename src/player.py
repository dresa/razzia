from pieces import Card
from scoring import Scoring, ScoringCard, ScoringCheque
import control

class Player:
    def __init__(self, player_agent, starting_cheques):
        self._player_agent = player_agent
        self._available_cheques = starting_cheques
        self._unavailable_cheques = []
        self._cards = []
        self._scored_cards = []
        self._counts = {c: 0 for c in Card if c != Card.Policeman}
        self._scoring_cheques = None
        self._scoring = Scoring(player_agent)
    @property
    def player_agent(self):
        return self._player_agent
    @property
    def round_is_over(self):
        return len(self._available_cheques) == 0
    @property
    def num_unavailable_cheques(self):
        return len(self._unavailable_cheques)
    @property
    def highest_cheque(self):
        if not self.round_is_over:
            return max(self._available_cheques)
    @property
    def cheque_total(self):
        cheques = self._available_cheques[:]  # copy
        cheques.extend(self._unavailable_cheques)
        return sum(cheques)
    @property
    def num_bodyguards(self):
        return self._counts[Card.Bodyguard]
    @property
    def score(self):
        return self._scoring.total_score()
    @property
    def detailed_score(self):
        return self._scoring
    @property
    def accumulated_card_score(self):
        round_scores = sum(sc.scored_points for sc in self._scored_cards)
        game_end_scores = sum(sc.scored_points for sc in self._cards)
        return round_scores + game_end_scores
    @property
    def adjusted_card_score(self):
        round_scores = sum(sc.scored_points for sc in self._scored_cards)
        game_end_scores = sum(sc.scored_points for sc in self._cards)
        r = control.GAME_ROUNDS
        return round_scores + game_end_scores + (-5 * r - 2 * r)  # Trinkets and bodyguards start with negative points
    @property
    def cheque_score(self):
        return sum(sc.scored_points for sc in self._scoring_cheques)

    def available_cheques(self):
        return self._available_cheques
    def has_cheque_available(self, cheque):
        return cheque in self._available_cheques
    def refresh_cheques(self):
        self._available_cheques.extend(self._unavailable_cheques)
        self._unavailable_cheques = []
    def remove_available_cheque(self, cheque):
        self._available_cheques.remove(cheque)  # removes first occurrence
    def add_unavailable_cheque(self, cheque):
        self._unavailable_cheques.append(cheque)
    def total_cheque_value(self):
        return sum(self._available_cheques) + sum(self._unavailable_cheques)
    def gain_cards(self, cards, round, cheque_value, cheque_ordinal):
        gained = [ScoringCard(c, round, cheque_value, cheque_ordinal) for c in cards]
        self._cards.extend(gained)
        for c in cards:
            self._counts[c] += 1

    def round_scoring(self, min_bodyguard, max_bodyguard):
        self._scoring.score_round(min_bodyguard, max_bodyguard, self._cards)
        self._scoring.assign_round_card_scores(min_bodyguard, max_bodyguard, self._cards)

        to_remove = [Card.GoldCoin, Card.Thief, Card.Ring, Card.Watch, Card.Brooch, Card.Chain, Card.Diamond, Card.Driver]  # TODO: unify
        self._scored_cards.extend(sc for sc in self._cards if sc.card in to_remove)
        self._cards = [sc for sc in self._cards if sc.card not in to_remove]
        for card_type in to_remove:
            self._counts[card_type] = 0

    def game_end_scoring(self, min_money, max_money):
        cheques = self._available_cheques[:]  # copy
        cheques.extend(self._unavailable_cheques)
        self._scoring_cheques = [ScoringCheque(c) for c in cheques]
        self._scoring.score_businesses(self._cards)
        self._scoring.score_cheques(min_money, max_money, self._scoring_cheques)
        self._scoring.assign_business_card_scores(self._cards)
        self._scoring.assign_cheque_scores(min_money, max_money, self._scoring_cheques)

    def __str__(self):
        s  = '\n' + str(self._player_agent) + '\n'
        s += '  Available cheques: ' + ', '.join(str(c) for c in self._available_cheques) + '\n'
        s += '  Unavailable cheques: ' + ', '.join(str(c) for c in self._unavailable_cheques) + '\n'
        s += '  Gained cards: \n    ' + '\n    '.join(str(c) for c in self._cards) + '\n'
        s += '  Counts: ' + ', '.join(['{} {}'.format(k.name, v) for k, v in self._counts.items() if v])
        return s

