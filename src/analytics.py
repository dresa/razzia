from pieces import Card
import control

def _determine_winner(scores):
    player_scores = {p: s.final_score() for p, s in scores.items()}
    return max(player_scores, key=player_scores.get)

def analyze_player_order(multi_scorings):
    wins = {}
    for scores in multi_scorings:
        if not wins:
            for p in scores:
                wins[p] = 0
        winner = _determine_winner(scores)
        wins[winner] += 1
    print(', '.join(['{} won {} times'.format(p, c) for p, c in wins.items()]))

def analyze_card_value(multi_scorings):
    points = {c: 0 for c in Card if c != Card.Policeman}
    counts = {c: 0 for c in Card if c != Card.Policeman}
    all_scoring_cards = [sc for scores in multi_scorings for s in scores.values() for sc in s.final_scoring_cards()]
    for card in points:
        for sc in all_scoring_cards:
            if sc.card == card:
                counts[card] += 1
                points[card] += sc.scored_points
    avg_points = {card: points[card] / counts[card] if counts[card] else None for card in points}
    print('\n'.join(['{} is worth {} points'.format(c, a) for c, a in avg_points.items()]))

    for round in range(1, control.GAME_ROUNDS + 1):
        for card in points:
            for sc in all_scoring_cards:
                if sc.card == card and sc.round == round:
                    counts[card] += 1
                    points[card] += sc.scored_points
        avg_points = {card: points[card] / counts[card] if counts[card] else None for card in points}
        print('\n'.join(['On Round {}, {} is worth {} points'.format(round, c, a) for c, a in avg_points.items()]))
