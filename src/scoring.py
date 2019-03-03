from enum import Enum
from pieces import Card

class Score(Enum):
    Trinkets=1
    Bodyguards=2
    Cars=3
    Drivers=4
    GoldCoins=5
    Thieves=6
    Businesses=7
    Cheques=8


class ScoringCard:
    def __init__(self, card, round, cheque_value, cheque_ordinal):
        self.card = card
        self.round = round
        self.cheque_value = cheque_value
        self.cheque_ordinal = cheque_ordinal
        self.scored_points = 0
    def __str__(self):
        return '{card:14s} (won by cheque {val} (ordinal {ord}) on Round {round}) scored {score} points'.format(
            card=self.card, val=self.cheque_value, ord=self.cheque_ordinal, round=self.round, score=self.scored_points)


class ScoringCheque:
    def __init__(self, cheque):
        self.cheque = cheque
        self.scored_points = 0
    def __str__(self):
        return 'Cheque {cheque:2s} scored {score} points.'.format(cheque=self.cheque, score=self.scored_points)


class Scoring:
    def __init__(self, name):
        self._name = name
        self._scores = {s: 0 for s in Score}

    def total_score(self):
        return sum(self._scores.values())

    def _count_cards(self, scoring_cards):
        return {c: len([sc for sc in scoring_cards if sc.card == c]) for c in Card}

    def score_round(self, min_bodyguard, max_bodyguard, scoring_cards):
        counts = self._count_cards(scoring_cards)
        score_gold = 3 * counts[Card.GoldCoin]
        score_thief = 2 * counts[Card.Thief]
        trinkets = [Card.Ring, Card.Watch, Card.Brooch, Card.Chain, Card.Diamond]  # TODO: unify
        num_unique_trinkets = len([t for t in trinkets if counts[t]])
        score_trinkets = {0: -5, 1: 0, 2: 0, 3: 5, 4: 10, 5: 15}[num_unique_trinkets]
        bodyguard_low = -2 if counts[Card.Bodyguard] == min_bodyguard else 0
        bodyguard_high = 5 if counts[Card.Bodyguard] == max_bodyguard else 0
        score_bodyguard = bodyguard_low + bodyguard_high
        score_car = 1 * counts[Card.Car] if counts[Card.Driver] else 0
        score_driver = 1 * counts[Card.Driver]

        self._scores[Score.GoldCoins] += score_gold
        self._scores[Score.Thieves] += score_thief
        self._scores[Score.Trinkets] += score_trinkets
        self._scores[Score.Bodyguards] += score_bodyguard
        self._scores[Score.Cars] += score_car
        self._scores[Score.Drivers] += score_driver

    def assign_round_card_scores(self, min_bodyguard, max_bodyguard, scoring_cards):
        counts = self._count_cards(scoring_cards)
        trinkets = [Card.Ring, Card.Watch, Card.Brooch, Card.Chain, Card.Diamond]  # TODO: unify
        num_unique_trinkets = len([t for t in trinkets if counts[t]])
        added_score_per_unique_trinket = None
        if num_unique_trinkets:
            score_trinkets = {0: -5, 1: 0, 2: 0, 3: 5, 4: 10, 5: 15}[num_unique_trinkets]
            added_score_per_unique_trinket = (5 + score_trinkets) / num_unique_trinkets
        bodyguards = counts[Card.Bodyguard]
        cars = counts[Card.Car]
        drivers = counts[Card.Driver]
        bodyguard_low = -2 if counts[Card.Bodyguard] == min_bodyguard else 0
        bodyguard_high = 5 if counts[Card.Bodyguard] == max_bodyguard else 0
        added_score_per_bodyguard = None
        if bodyguards:
            if bodyguard_low and bodyguard_high: added_score_per_bodyguard = 5 / bodyguards  # (5 - 2) + 2, like max - min + start
            elif bodyguard_low: added_score_per_bodyguard = 0 / bodyguards
            elif bodyguard_high: added_score_per_bodyguard = (2 + 5) / bodyguards
            else: added_score_per_bodyguard = 2 / bodyguards  # scores 0 points instead of -2, so impact is +2
        for sc in scoring_cards:
            if sc.card in trinkets: sc.scored_points += added_score_per_unique_trinket / counts[sc.card]
            elif sc.card == Card.GoldCoin: sc.scored_points += 3
            elif sc.card == Card.Thief: sc.scored_points += 2
            elif sc.card == Card.Bodyguard: sc.scored_points += added_score_per_bodyguard
            elif sc.card == Card.Car: sc.scored_points += 0.5 if drivers else 0
            elif sc.card == Card.Driver: sc.scored_points += 1 + 0.5 * cars / drivers
        # For trinkets, starting points are -5.
        # For Bodyguards, starting points are +3 (both max and min: 5 - 2 = 3).
        # In total, starting points are -2 (rather than 0).

    def score_businesses(self, scoring_cards):
        counts = self._count_cards(scoring_cards)
        businesses = [Card.Casino, Card.Transportation, Card.Film, Card.HorseRacing,
                      Card.RealEstate, Card.NightClub, Card.Restaurant]  # TODO: unify
        num_unique_businesses = len([b for b in businesses if counts[b]])
        got_all_businesses = num_unique_businesses == len(businesses)
        business_bonus = 3 if got_all_businesses else 0
        score_unique_businesses = num_unique_businesses + business_bonus
        score_multi_businesses = sum([5 * (counts[b] - 2) for b in businesses if counts[b] >= 3])
        self._scores[Score.Businesses] += score_unique_businesses + score_multi_businesses

    def assign_business_card_scores(self, scoring_cards):
        counts = self._count_cards(scoring_cards)
        businesses = [Card.Casino, Card.Transportation, Card.Film, Card.HorseRacing,
                      Card.RealEstate, Card.NightClub, Card.Restaurant]  # TODO: unify duplicates
        num_unique_businesses = len([b for b in businesses if counts[b]])  # TODO: combine with "score_businesses"
        got_all_businesses = num_unique_businesses == len(businesses)
        for sc in scoring_cards:
            if sc.card in businesses:
                n = counts[sc.card]
                # one point for each unique Business, divided by number of Business cards
                unique_points = 1 / n
                # 3 bonus points if all Businesses exist --> so 3/7 points per unique, divided by duplicates
                bonus_points = 3 / len(businesses) / n if got_all_businesses else 0
                # extra points for duplicate Businesses, if three or four cards of each, divided by like cards.
                multi_points = 5 * (n - 2) / n if n >= 3 else 0
                sc.scored_points += unique_points + bonus_points + multi_points

    def score_cheques(self, min_money, max_money, scoring_cheques):
        total_cheques_value = sum(sc.cheque for sc in scoring_cheques)
        money_low = -5 if total_cheques_value == min_money else 0
        money_high = 5 if total_cheques_value == max_money else 0
        score_money = money_low + money_high
        self._scores[Score.Cheques] += score_money

    def assign_cheque_scores(self, min_money, max_money, scoring_cheques):
        total_cheques_value = sum(sc.cheque for sc in scoring_cheques)  # TODO: unify with "score_cheques"
        money_low = -5 if total_cheques_value == min_money else 0
        money_high = 5 if total_cheques_value == max_money else 0
        score_money = money_low + money_high
        for sc in scoring_cheques:
            sc.scored_points += score_money / len(scoring_cheques)

    def __str__(self):
        s  = 'Scoring {} total {}:\n'.format(self._name, self.total_score())
        s += '\n'.join('  {}: {}'.format(k, v) for k, v in self._scores.items())
        return s
