from enum import Enum
from pieces import Card
import pieces
import control
import logging

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
    def __init__(self, card, round, cheque, cheque_ordinal):
        self.card = card
        self.round = round
        self.cheque = cheque
        self.cheque_ordinal = cheque_ordinal
        self.scored_points = 0
    def __str__(self):
        return '{card:14s} (won by cheque {val} (ordinal {ord}) on Round {round}) scored {score} points'.format(
            card=self.card, val=self.cheque, ord=self.cheque_ordinal, round=self.round, score=self.scored_points)


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
        self._scoring_cards = None
        self._scoring_cheques = None

    def final_score(self):
        return round(sum(self._scores.values()))

    def final_score_by_type(self):
        return dict(self._scores)

    def final_card_score(self):
        return round(sum(sc.scored_points for sc in self._scoring_cards))

    def final_cheque_score(self):
        return round(sum(sc.scored_points for sc in self._scoring_cheques))

    def final_accumulated_card_score(self):
        return round(sum(sc.scored_points for sc in self._scoring_cards))

    def final_adjusted_card_score(self):
        raw_scores = round(sum(sc.scored_points for sc in self._scoring_cards))
        r = control.GAME_ROUNDS
        return raw_scores + (-5 * r - 2 * r)  # Trinkets and bodyguards start with negative points

    def final_scoring_cards(self):
        return self._scoring_cards

    def final_scoring_cheques(self):
        return self._scoring_cheques

    def attach_final_scoring_cards(self, scoring_cards):
        self._scoring_cards = scoring_cards

    def attach_final_scoring_cheques(self, scoring_cheques):
        self._scoring_cheques = scoring_cheques

    def _count_cards(self, scoring_cards):
        return {c: len([sc for sc in scoring_cards if sc.card == c]) for c in Card}

    def score_round(self, min_bodyguard, max_bodyguard, scoring_cards):
        counts = self._count_cards(scoring_cards)
        score_gold = 3 * counts[Card.GoldCoin]
        score_thief = 2 * counts[Card.Thief]
        num_unique_trinkets = len([t for t in pieces.TRINKET_CARDS if counts[t]])
        score_trinkets = {0: -5, 1: 0, 2: 0, 3: 5, 4: 10, 5: 15}[num_unique_trinkets]
        bodyguard_low = -2 if counts[Card.Bodyguard] == min_bodyguard else 0
        bodyguard_high = 5 if counts[Card.Bodyguard] == max_bodyguard else 0
        score_bodyguard = bodyguard_low + bodyguard_high
        score_car = 1 * counts[Card.Car] if counts[Card.Driver] else 0
        score_driver = 1 * counts[Card.Driver]

        scores = [score_bodyguard, score_car, score_driver, score_gold, score_thief, score_trinkets, ]
        groups = [Card.Bodyguard.name, Card.Car.name, Card.Driver.name, Card.GoldCoin.name, Card.Thief.name, 'Trinkets']
        group_scores_str = ', '.join('{}({:+})'.format(g, s) for g, s in zip(groups, scores))
        logging.debug('  Round scoring for {}: {}'.format(self._name, group_scores_str))

        self._scores[Score.GoldCoins] += score_gold
        self._scores[Score.Thieves] += score_thief
        self._scores[Score.Trinkets] += score_trinkets
        self._scores[Score.Bodyguards] += score_bodyguard
        self._scores[Score.Cars] += score_car
        self._scores[Score.Drivers] += score_driver

    def assign_round_card_scores(self, min_bodyguard, max_bodyguard, scoring_cards):
        counts = self._count_cards(scoring_cards)
        num_unique_trinkets = len([t for t in pieces.TRINKET_CARDS if counts[t]])
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
            if sc.card in pieces.TRINKET_CARDS: sc.scored_points += added_score_per_unique_trinket / counts[sc.card]
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
        num_unique_businesses = len([b for b in pieces.BUSINESS_CARDS if counts[b]])
        got_all_businesses = num_unique_businesses == len(pieces.BUSINESS_CARDS)
        business_bonus = 3 if got_all_businesses else 0
        score_unique_businesses = num_unique_businesses + business_bonus
        score_multi_businesses = sum([5 * (counts[b] - 2) for b in pieces.BUSINESS_CARDS if counts[b] >= 3])

        logging.debug('  Business scores for {}: unique({}), multiple({})'.format(self._name, score_unique_businesses, score_multi_businesses))

        self._scores[Score.Businesses] += score_unique_businesses + score_multi_businesses

    def assign_business_card_scores(self, scoring_cards):
        counts = self._count_cards(scoring_cards)
        num_unique_businesses = len([b for b in pieces.BUSINESS_CARDS if counts[b]])  # TODO: combine with "score_businesses"
        got_all_businesses = num_unique_businesses == len(pieces.BUSINESS_CARDS)
        for sc in scoring_cards:
            if sc.card in pieces.BUSINESS_CARDS:
                n = counts[sc.card]
                # one point for each unique Business, divided by number of Business cards
                unique_points = 1 / n
                # 3 bonus points if all Businesses exist --> so 3/7 points per unique, divided by duplicates
                bonus_points = 3 / len(pieces.BUSINESS_CARDS) / n if got_all_businesses else 0
                # extra points for duplicate Businesses, if three or four cards of each, divided by like cards.
                multi_points = 5 * (n - 2) / n if n >= 3 else 0
                sc.scored_points += unique_points + bonus_points + multi_points

    def score_cheques(self, min_money, max_money, scoring_cheques):
        total_cheques_value = sum(sc.cheque.value for sc in scoring_cheques)
        money_low = -5 if total_cheques_value == min_money else 0
        money_high = 5 if total_cheques_value == max_money else 0
        score_money = money_low + money_high
        self._scores[Score.Cheques] += score_money

    def assign_cheque_scores(self, min_money, max_money, scoring_cheques):
        total_cheques_value = sum(sc.cheque.value for sc in scoring_cheques)  # TODO: unify with "score_cheques"
        money_low = -5 if total_cheques_value == min_money else 0
        money_high = 5 if total_cheques_value == max_money else 0
        score_money = money_low + money_high
        for sc in scoring_cheques:
            sc.scored_points += score_money / len(scoring_cheques)

    def __str__(self):
        s  = 'Scoring {} total {}:\n'.format(self._name, self.final_score())
        s += '\n'.join('  {}: {}'.format(k, v) for k, v in self._scores.items())
        return s


class ExpectedScore:
    @staticmethod
    def _static_card_score(card_counts, min_bodyguard, max_bodyguard, num_rounds_remaining):
        """Score when all remaining rounds are played out but no more cards are gained."""
        score_gold = 3 * card_counts[Card.GoldCoin]
        score_thief = 2 * card_counts[Card.Thief]
        num_unique_trinkets = len([t for t in pieces.TRINKET_CARDS if card_counts[t]])
        score_trinkets = {0: -5, 1: 0, 2: 0, 3: 5, 4: 10, 5: 15}[num_unique_trinkets]
        bodyguard_low = -2 if card_counts[Card.Bodyguard] == min_bodyguard else 0
        bodyguard_high = 5 if card_counts[Card.Bodyguard] == max_bodyguard else 0
        score_bodyguard = bodyguard_low + bodyguard_high
        score_car = 1 * card_counts[Card.Car] if card_counts[Card.Driver] else 0
        score_driver = 1 * card_counts[Card.Driver]

        score_round = score_gold + score_thief + score_trinkets + score_bodyguard + score_car + score_driver
        score_remaining = num_rounds_remaining * (score_bodyguard + 0 - 5)  # cars 0 (without driver); trinkets -5

        # Businesses
        num_unique_businesses = len([b for b in pieces.BUSINESS_CARDS if card_counts[b]])
        got_all_businesses = num_unique_businesses == len(pieces.BUSINESS_CARDS)
        business_bonus = 3 if got_all_businesses else 0
        score_unique_businesses = num_unique_businesses + business_bonus
        score_multi_businesses = sum([5 * (card_counts[b] - 2) for b in pieces.BUSINESS_CARDS if card_counts[b] >= 3])
        score_business = score_unique_businesses + score_multi_businesses

        score = score_round + score_remaining + score_business
        return score

    @staticmethod
    def marginal_card_score(counts, gained_counts, min_oppo_bodyguards, max_oppo_bodyguards, num_rounds_remaining):
        score_now = ExpectedScore._static_card_score(
            counts,
            min(min_oppo_bodyguards, counts[Card.Bodyguard]),
            max(max_oppo_bodyguards, counts[Card.Bodyguard]),
            num_rounds_remaining)
        after_counts = {c: counts[c] + gained_counts[c] for c in counts}
        score_after = ExpectedScore._static_card_score(
            after_counts,
            min(min_oppo_bodyguards, after_counts[Card.Bodyguard]),
            max(max_oppo_bodyguards, after_counts[Card.Bodyguard]),
            num_rounds_remaining)
        marginal_gain = score_after - score_now
        return marginal_gain

