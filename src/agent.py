import random
from scoring import ExpectedScore
from pieces import Card
from control import ActionType


class PlayerAgent:
    def __init__(self, name):
        self._name = name
    def act(self, game_view):
        raise NotImplementedError('Cannot use base PlayerAgent as agent: implement "act()" in derived class.')
    def bid(self, game_view, auction_view, player_view, is_mandated):
        raise NotImplementedError('Cannot use base PlayerAgent as agent: implement "bid()" in derived class.')
    def steal(self, game_view):
        raise NotImplementedError('Cannot use base PlayerAgent as agent: implement "steal()" in derived class.')
    def __str__(self):
        return self._name
    @property
    def name(self):
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

class StealingPlayerAgent(TrivialPlayerAgent):
    VALUABLE_THRESHOLD = 4.0  # Threshold (points per card) that counts as valuable in the face of a thief.

    def _remaining_board_value(self):
        pass  # FIXME
    def _identify_valuable_cards(self, player_view, board_view, min_oppo_bodyguards, max_oppo_bodyguards, num_rounds_remaining):
        # TODO: should consider possibility that two cards are stolen at once.
        player_card_counts = player_view.card_counts()
        board_card_counts = board_view.card_counts()
        def marginal_score(stolen_card):
            return ExpectedScore.marginal_card_score(
                player_card_counts,
                {c: 1 if c == stolen_card else 0 for c in Card},
                min_oppo_bodyguards,
                max_oppo_bodyguards,
                num_rounds_remaining)
        valuables = {c: marginal_score(c) if board_card_counts[c] >= 1 else None for c in Card if c != Card.Policeman}
        return {k: v for k, v in valuables.items() if v and v >= StealingPlayerAgent.VALUABLE_THRESHOLD}

    def _theft_plan(self, game_view):
        # TODO: allow stealing more than one card (that is, using more than one thief at once.
        player_view = game_view.get_active_player_view()
        all_player_views = game_view.get_all_player_views()
        board_view = game_view.get_board_view()
        if player_view.num_available_thieves() == 0:
            return False, None, None
        opponent_bg_counts = [p.card_counts()[Card.Bodyguard] for p in all_player_views]
        opponent_bg_counts.remove(player_view.card_counts()[Card.Bodyguard])  # remove first occurrence
        valuable_cards_available = self._identify_valuable_cards(
            player_view,
            board_view,
            min(opponent_bg_counts),
            max(opponent_bg_counts),
            game_view.rounds_remaining)
        #remaining_board_value_low =  # TODO: should consider possibility there is only one valuable, even when being last player.
        outbid_candidates = [p.highest_cheque for p in all_player_views if p.highest_cheque]
        opponents_can_outbid = outbid_candidates and max(outbid_candidates) > player_view.highest_cheque
        return True, valuable_cards_available, opponents_can_outbid

    def _is_theft_suggested(self, game_view):
        has_thief, valuable_cards_available, opponents_can_outbid = self._theft_plan(game_view)
        theft_suggested = has_thief and valuable_cards_available and opponents_can_outbid
        # TODO: theft_suggested = valuable_cards_available and (remaining_board_value_low or opponents_can_outbid)
        return theft_suggested

    def act(self, game_view):
        if self._is_theft_suggested(game_view):
            return ActionType.Thief  # FIXME: why is Thief action not used at all?
        else:
            return ActionType.Draw

    def steal(self, game_view):
        # TODO: enable stealing more than one card at once.
        _, valuable_cards_available, _ = self._theft_plan(game_view)
        v = valuable_cards_available
        most_valuable_card = max(v, key=v.get)
        return [most_valuable_card]  # list of all cards to steal (need to have enough Thief cards)





'''
Simple rule-based ideas for choosing actions:
NOT IMPLEMENTED YET
1. IF last player playing AND policemen <= 5, THEN ActionType.Draw (accumulate more cards safely)
2. IF thieves available AND critical card available AND value of rest of the board is low, THEN ActionType.Thief (cherry-picking, also when being last player) 
3. IF thieves available AND critical card available AND opponent has higher max cheque, THEN ActionType.Thief (safe-playing) 
4. IF last player playing AND policemen == 6 AND policemen density in deck low enough AND current board value low enough, THEN ActionType.Draw (push your luck)
5. IF opponent has higher max cheque AND value of board is higher than my max cheque expectation, THEN ActionType.AuctionByPlayer (minimize opponent gains)
6. IF opponent has higher min cheque
   AND value of board is higher than my min cheque expectation
   AND value of board almost reaches opponent's cheque expectation,
   THEN ActionType.AuctionByPlayer (provoke opponent)
7. IF value of board exceeds opponent's min cheque expectation,
   AND value of board almost reaches my min cheque expectation,
   THEN ActionType.AuctionByPlayer (provoke opponent, even if there is only a cheque and no cards)
X. Not knowing what to do, THEN ActionType.Draw (default choice)

Rule-based bidding ideas:
1. IF only player AND one cheque left AND value of board higher than expected from the rest of the deck, THEN Bid OTHERWISE Pass unless mandated.
2. IF only player AND several cheques left AND remaining deck is large AND value of board higher than expected from the rest of the deck, THEN Bid HIGHEST
3. IF only player AND several cheques left AND remaining deck is small AND value of board higher than expected from the rest of the deck, THEN Bid LOWEST
4. IF value is below all cheques, THEN Pass, unless Mandated THEN Bid lowest.
5. IF value exceeds expectation of min outbidding cheque, THEN Bid OTHERWISE Pass unless Mandated THEN Bid min cheque.
   Identify your bidding candidates: outbidding cheques for which expectation is below board value.
   For each opponent yet to bid, identify their rival cheques: maximum cheques whose expectation is below board value.
   Choose your bidding cheque: a minimum candidate cheque that exceeds the opponents' rival cheques.
   If none of your candidate cheques fits the bill, then Pass.
   In case you are last to bid, there are no further rival cheques to consider: bid the min outbidding cheque or Pass. 
'''
