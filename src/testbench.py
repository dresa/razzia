import unittest
from razzia import Razzia
from scoring import Score

class TestRazziaScoring(unittest.TestCase):

    def test_fixed_game_1(self):
        n = 4
        r = Razzia(n, ai='trivial', random_seed=1)
        scorings = r.play_game()
        name_to_agent = {agent.name : agent for agent in scorings.keys()}
        expected_total_scores = [0, 4, 22, 34]
        expected_detailed_scores = [
            # Trinkets, Bodyguards, Cars, Drivers, GoldCoins, Thieves, Businesses, Cheques
            [ -5, -6, 2, 3, 0, 2,  4,  0],
            [-10, -4, 5, 1, 0, 2,  5,  5],
            [ -5, 15, 4, 1, 0, 2, 10, -5],
            [  5,  3, 4, 2, 3, 6,  6,  5]
        ]
        for player_id in range(n):
            s = scorings[name_to_agent[Razzia.DEFAULT_PLAYER_NAMES[player_id]]]
            by_type = s.final_score_by_type()
            self.assertEqual(s.final_score(), expected_total_scores[player_id])
            self.assertEqual([by_type[s] for s in Score], expected_detailed_scores[player_id])

    def test_fixed_game_2(self):
        n = 4
        r = Razzia(n, ai='stealing', random_seed=1)
        scorings = r.play_game()
        name_to_agent = {agent.name : agent for agent in scorings.keys()}
        expected_total_scores = [42, 4, -2, -2]
        expected_detailed_scores = [
            # Trinkets, Bodyguards, Cars, Drivers, GoldCoins, Thieves, Businesses, Cheques
            [ 10, 15, 0, 0, 0, 6,  6,  5],
            [-10, -2, 6, 2, 3, 0,  5,  0],
            [-10, -4, 7, 2, 0, 0,  3,  0],
            [ -5, -2, 3, 2, 0, 0,  5, -5]
        ]
        for player_id in range(n):
            s = scorings[name_to_agent[Razzia.DEFAULT_PLAYER_NAMES[player_id]]]
            by_type = s.final_score_by_type()
            self.assertEqual(s.final_score(), expected_total_scores[player_id])
            self.assertEqual([by_type[s] for s in Score], expected_detailed_scores[player_id])



if __name__ == '__main__':
    unittest.main()
