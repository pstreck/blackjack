from unittest import TestCase

from blackjack.game import Game
from blackjack.game import GameSettings
from blackjack.player import BetStrategyType
from tests.utils import build_hand


class TestGame(TestCase):
    def test_add_player_default(self):
        game = Game()

        bankroll = 100
        game.add_player(bankroll)

        self.assertEqual(2, len(game.players))
        self.assertEqual(bankroll, game.players[0].bankroll)
        self.assertEqual(False, game.players[0].dealer)
        self.assertEqual(1, game.players[0].number)

    def test_add_player_multiple(self):
        game = Game()

        num_players = 3
        bankroll = 100
        for _ in range(num_players):
            game.add_player(bankroll)

        self.assertEqual(num_players + 1, len(game.players))

        for i in range(num_players):
            self.assertEqual(i + 1, game.players[i].number)

    def test_add_player_options(self):
        game = Game()

        bankroll = 100
        bet_strategy_type = BetStrategyType.MARTINGALE
        player_limit = 25

        game.add_player(bankroll, bet_strategy_type=bet_strategy_type, player_limit=player_limit)

        self.assertEqual(2, len(game.players))
        self.assertEqual(bankroll, game.players[0].bankroll)
        self.assertEqual(bet_strategy_type, game.players[0].bet_strategy.strategy_type)
        self.assertEqual(False, game.players[0].dealer)
        self.assertEqual(player_limit, game.players[0].player_limit)
        self.assertEqual(1, game.players[0].number)

    def test_play_hand_double_down(self):
        game = Game()

        bankroll = 100
        game.add_player(bankroll)

        game.players[-1].hands.append(build_hand('soft'))
        game.players[0].hands.append(build_hand('double_down'))
        game.players[0].bankroll -= game.settings.min_bet

        game.play_hand(game.players[0], game.players[0].hands[0])

        self.assertEqual(bankroll - (game.settings.min_bet * 2), game.players[0].bankroll)
        self.assertEqual(game.settings.min_bet * 2, game.players[0].hands[0].bet)
        self.assertEqual(3, len(game.players[0].hands[0].cards))

    def test_play_hand_hit(self):
        game = Game()

        bankroll = 100
        game.add_player(bankroll)

        game.players[-1].hands.append(build_hand('hard'))
        game.players[0].hands.append(build_hand('soft'))

        game.play_hand(game.players[0], game.players[0].hands[0])

        self.assertLess(2, len(game.players[0].hands[0].cards))

    def test_play_hand_split(self):
        game = Game()

        bankroll = 100
        game.add_player(bankroll)

        game.players[-1].hands.append(build_hand('hard'))
        game.players[0].hands.append(build_hand('hard_pair'))
        game.players[0].bankroll -= game.settings.min_bet

        game.play_hand(game.players[0], game.players[0].hands[0])
        game.play_hand(game.players[0], game.players[0].hands[1])

        self.assertEqual(bankroll - (game.settings.min_bet * 2), game.players[0].bankroll)
        self.assertEqual(2, len(game.players[0].hands))
        self.assertLessEqual(2, len(game.players[0].hands[0].cards))
        self.assertLessEqual(2, len(game.players[0].hands[1].cards))
        self.assertEqual(game.settings.min_bet, game.players[0].hands[0].bet)
        self.assertEqual(game.settings.min_bet, game.players[0].hands[1].bet)

    def test_play_hand_stand(self):
        game = Game()

        bankroll = 100
        game.add_player(bankroll)

        game.players[-1].hands.append(build_hand('hard'))
        game.players[0].hands.append(build_hand('hard'))

        self.assertEqual(2, len(game.players[0].hands[0].cards))

    def test_play_round(self):
        game = Game()

        bankroll = 100
        game.add_player(bankroll)

        pre_round_count = game.round_count
        game.play_round()

        self.assertEqual(pre_round_count + 1, game.round_count)

        for player in game.players:
            self.assertLess(0, len(player.hands[0].cards))

        for player in game.players[:-1]:
            self.assertNotEqual(None, player.hands[0].result)

    def test_start(self):
        game = Game(GameSettings(num_decks=1))

        bankroll = 100
        game.add_player(bankroll)

        num_rounds = 10
        game.start(rounds=num_rounds)

        self.assertEqual(num_rounds, game.round_count)
