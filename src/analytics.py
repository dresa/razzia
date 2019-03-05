from pieces import Card, Cheque
import control
import statistics

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
    score_cards = [c for c in Card if c != Card.Policeman]
    all_scoring_cards = [sc for scores in multi_scorings for s in scores.values() for sc in s.final_scoring_cards()]
    points = {c: {} for c in score_cards}
    for card in score_cards:
        card_points = [sc.scored_points for sc in all_scoring_cards if sc.card == card]
        points[card] = {'mean': statistics.mean(card_points), 'stdev': statistics.stdev(card_points)}
    print('\n'.join(['{} is worth {:.3f} points with {:.3f} stdev'.format(c, p['mean'], p['stdev']) for c, p in points.items()]))

    rounds = range(1, control.GAME_ROUNDS + 1)
    round_points = {r: {} for r in rounds}
    for r in rounds:
        for card in score_cards:
            round_card_points = [sc.scored_points for sc in all_scoring_cards if sc.card == card and sc.round == r]
            round_points[r][card] = {
                'mean': statistics.mean(round_card_points),
                'stdev': statistics.stdev(round_card_points),
                'n': len(round_card_points)
            }
    for r in rounds:
        s_template = 'On Round {}, {:14s} is worth {:.3f} points with {:.3f} stdev in {} samples'
        s = [s_template.format(r, c, p['mean'], p['stdev'], p['n']) for c, p in round_points[r].items()]
        print('\n'.join(s))

def analyze_cheque_value(multi_scorings):
    score_cheques = [c for c in Cheque]
    rounds = range(1, control.GAME_ROUNDS + 1)
    points = {}
    for game_idx, scores in enumerate(multi_scorings):
        game_scoring_cards = [sc for s in scores.values() for sc in s.final_scoring_cards()]
        points[game_idx] = {r: {c: 0 for c in score_cheques} for r in rounds}
        for r in rounds:
            for cheque in score_cheques:
                card_points = [sc.scored_points for sc in game_scoring_cards if sc.round == r and sc.cheque == cheque]
                n = len(card_points)
                points[game_idx][r][cheque] = {
                    'sum': sum(card_points) if n else 0,
                    'n': n
                }
    averages = {r: {c: {} for c in score_cheques} for r in rounds}
    for r in rounds:
        for cheque in score_cheques:
            accu_points = [points[game_idx][r][cheque]['sum'] for game_idx in points]
            accu_n = [points[game_idx][r][cheque]['n'] for game_idx in points]
            averages[r][cheque]['points'] = statistics.mean(accu_points)
            averages[r][cheque]['cards'] = statistics.mean(accu_n)

    for r in rounds:
        for cheque in score_cheques:
            s_template = 'On Round {}, {} is worth {:.3f} points with {:.3f} cards'
            p = averages[r][cheque]
            print(s_template.format(r, cheque, p['points'], p['cards']))

    money = {c: [] for c in Cheque}
    for scores in multi_scorings:
        for p, s in scores.items():
            for sc in s.final_scoring_cheques():
                money[sc.cheque].append(sc.scored_points)
    for cheque in money:
        s_template = 'At game end, {} is worth {:.3f} money points in {} samples'
        avg = statistics.mean(money[cheque]) if money[cheque] else 0
        print(s_template.format(cheque, avg, len(money[cheque])))





