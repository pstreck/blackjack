from unittest import TestCase

from blackjack.cards import Card
from blackjack.game import GameSettings
from blackjack.hand import Hand
from blackjack.hand import HandResult
from blackjack.player import BetStrategy
from blackjack.player import BetStrategyType
from blackjack.player import Player
from blackjack.player import PlayerAction
from tests.utils import build_hand


class BetStrategyTest(TestCase):
    game_settings = GameSettings()

    def test_bet_limit_game(self):
        limit = 25

        settings = {
            'game_settings': GameSettings(min_bet=limit * 2, max_bet=limit)
        }

        strategy = BetStrategy(settings)
        self.assertEqual(limit, strategy.bet())

    def test_bet_limit_player(self):
        limit = 0

        settings = {
            'bet_limit': limit,
            'game_settings': BetStrategyTest.game_settings
        }

        strategy = BetStrategy(settings)
        self.assertEqual(limit, strategy.bet())

    def test_bet_strategy_martingale(self):
        settings = {
            'game_settings': BetStrategyTest.game_settings,
            'strategy_type': BetStrategyType.MARTINGALE
        }

        strategy = BetStrategy(settings)
        self.assertEqual(BetStrategyTest.game_settings.min_bet, strategy.bet())

        strategy.last_hand = Hand()
        strategy.last_hand.result = HandResult.PUSH
        self.assertEqual(BetStrategyTest.game_settings.min_bet, strategy.bet())

        strategy.last_hand.result = HandResult.LOSE
        self.assertEqual(BetStrategyTest.game_settings.min_bet * 2, strategy.bet())

    def test_bet_strategy_parlay(self):
        settings = {
            'game_settings': BetStrategyTest.game_settings,
            'strategy_type': BetStrategyType.PARLAY
        }

        strategy = BetStrategy(settings)
        self.assertEqual(BetStrategyTest.game_settings.min_bet, strategy.bet())

        strategy.last_hand = Hand()
        strategy.last_hand.result = HandResult.WIN
        strategy.last_hand.winnings = BetStrategyTest.game_settings.min_bet
        self.assertEqual(BetStrategyTest.game_settings.min_bet * 2, strategy.bet())

    def test_bet_strategy_series(self):
        settings = {
            'game_settings': BetStrategyTest.game_settings,
            'strategy_type': BetStrategyType.SERIES
        }

        strategy = BetStrategy(settings)
        with self.assertRaises(ValueError):
            strategy.bet()

        settings['series'] = [1, 2, 3]
        strategy = BetStrategy(settings)

        for multiplier in settings['series']:
            self.assertEqual(BetStrategyTest.game_settings.min_bet * multiplier, strategy.bet())

        strategy.last_hand = Hand()
        strategy.last_hand.result = HandResult.WIN

        self.assertEqual(BetStrategyTest.game_settings.min_bet, strategy.bet())

    def test_bet_strategy_series_reset_on_lose(self):
        settings = {
            'game_settings': BetStrategyTest.game_settings,
            'strategy_type': BetStrategyType.SERIES,
            'series': [1, 2, 3]
        }

        strategy = BetStrategy(settings)

        strategy.last_hand = Hand()
        strategy.last_hand.result = HandResult.LOSE

        self.assertEqual(BetStrategyTest.game_settings.min_bet, strategy.bet())

    def test_bet_strategy_streak_no_streak_rates(self):
        settings = {
            'game_settings': BetStrategyTest.game_settings,
            'strategy_type': BetStrategyType.STREAK
        }

        strategy = BetStrategy(settings)

        with self.assertRaises(ValueError):
            strategy.bet()

    def test_bet_strategy_streak_lose_streak(self):
        streak_rates = {-2: 2, -1: 1, 0: 1, 1: 2, 2: 3}

        settings = {
            'game_settings': BetStrategyTest.game_settings,
            'strategy_type': BetStrategyType.STREAK,
            'streak_rates': streak_rates
        }

        strategy = BetStrategy(settings)

        streak_count = 2

        for _ in range(streak_count):
            strategy.last_hand = Hand()
            strategy.last_hand.result = HandResult.LOSE

        self.assertEqual(BetStrategyTest.game_settings.min_bet * streak_rates[streak_count * -1], strategy.bet())

    def test_bet_strategy_streak_mixed_streak(self):
        streak_rates = {-2: 2, -1: 1, 0: 1, 1: 2, 2: 3}

        settings = {
            'game_settings': BetStrategyTest.game_settings,
            'strategy_type': BetStrategyType.STREAK,
            'streak_rates': streak_rates
        }

        strategy = BetStrategy(settings)

        strategy.last_hand = Hand()
        strategy.last_hand.result = HandResult.LOSE

        streak_count = 2

        for _ in range(streak_count):
            strategy.last_hand = Hand()
            strategy.last_hand.result = HandResult.WIN

        self.assertEqual(BetStrategyTest.game_settings.min_bet * streak_rates[streak_count], strategy.bet())

    def test_bet_strategy_streak_no_streak(self):
        streak_rates = {-2: 2, -1: 1, 0: 1, 1: 2, 2: 3}

        settings = {
            'game_settings': BetStrategyTest.game_settings,
            'strategy_type': BetStrategyType.STREAK,
            'streak_rates': streak_rates
        }

        strategy = BetStrategy(settings)
        self.assertEqual(BetStrategyTest.game_settings.min_bet, strategy.bet())

    def test_bet_strategy_streak_win_streak(self):
        streak_rates = {-2: 2, -1: 1, 0: 1, 1: 2, 2: 3}

        settings = {
            'game_settings': BetStrategyTest.game_settings,
            'strategy_type': BetStrategyType.STREAK,
            'streak_rates': streak_rates
        }

        strategy = BetStrategy(settings)

        streak_count = 2

        for _ in range(streak_count):
            strategy.last_hand = Hand()
            strategy.last_hand.result = HandResult.WIN

        self.assertEqual(BetStrategyTest.game_settings.min_bet * streak_rates[streak_count], strategy.bet())

    def test_bet_strategy_static(self):
        settings = {
            'game_settings': BetStrategyTest.game_settings,
            'strategy_type': BetStrategyType.STATIC
        }

        strategy = BetStrategy(settings)
        self.assertEqual(BetStrategyTest.game_settings.min_bet, strategy.bet())


class BetStrategyTypeTest(TestCase):
    def test___str__(self):
        self.assertEqual('Series', str(BetStrategyType.SERIES))


class PlayerTest(TestCase):
    game_settings = GameSettings(min_bet=10, max_bet=100)

    def test___format__(self):
        player = Player({'game_settings': PlayerTest.game_settings})
        self.assertEqual('Player 1  ', '{:10s}'.format(player))

    def test___init___(self):
        player_settings = {
            'bankroll': 10000,
            'bet_limit': 1000,
            'dealer': True,
            'game_settings': PlayerTest.game_settings,
            'number': 10,
            'unknown': False
        }

        player = Player(player_settings.copy())

        self.assertEqual(player_settings['bankroll'], player.bankroll)
        self.assertEqual(player_settings['bet_limit'], player.bet_limit)
        self.assertEqual(player_settings['dealer'], player.dealer)
        self.assertEqual(player_settings['number'], player.number)
        self.assertEqual(player_settings['unknown'], player.extra_settings['unknown'])

    def test___init__without_game_settings(self):
        with self.assertRaises(ValueError):
            Player({})

    def test___str__player(self):
        player = Player({'game_settings': PlayerTest.game_settings})
        self.assertEqual('Player 1', str(player))

    def test___str__dealer(self):
        dealer = Player.dealer(PlayerTest.game_settings)
        self.assertEqual('Dealer', str(dealer))

    def test_action_basic_strategy_blackjack(self):
        player = Player({'game_settings': PlayerTest.game_settings})
        hand = build_hand('blackjack')

        self.assertEqual(PlayerAction.STAND, player.action(hand, Card('K', 10, 'clubs')))

    def test_action_basic_strategy_double_down(self):
        player = Player({'game_settings': PlayerTest.game_settings})
        hand = build_hand('double_down')

        self.assertEqual(PlayerAction.DOUBLE_DOWN, player.action(hand, Card('5', 5, 'clubs')))

    def test_action_basic_strategy_double_down_with_three_cards(self):
        player = Player({'game_settings': PlayerTest.game_settings})
        hand = build_hand('three_card_11')

        self.assertEqual(PlayerAction.HIT, player.action(hand, Card('K', 10, 'clubs')))

    def test_action_basic_strategy_hard(self):
        player = Player({'game_settings': PlayerTest.game_settings})
        hand = build_hand('hard')

        self.assertEqual(PlayerAction.STAND, player.action(hand, Card('K', 10, 'clubs')))

    def test_action_basic_strategy_low_bankroll_double_down(self):
        player = Player({'bankroll': 0, 'game_settings': PlayerTest.game_settings})
        hand = build_hand('soft')
        hand.bet = 1

        self.assertEqual(PlayerAction.HIT, player.action(hand, Card('5', 5, 'clubs')))

    def test_action_basic_strategy_low_bankroll_split_hard(self):
        player = Player({'bankroll': 0, 'game_settings': PlayerTest.game_settings})

        hand = build_hand('hard_pair')
        hand.bet = 1

        self.assertEqual(PlayerAction.STAND, player.action(hand, Card('5', 5, 'clubs')))

    def test_action_basic_strategy_low_bankroll_split_soft(self):
        player = Player({'bankroll': 0, 'game_settings': PlayerTest.game_settings})

        hand = build_hand('soft_pair')
        hand.bet = 1

        self.assertEqual(PlayerAction.HIT, player.action(hand, Card('5', 5, 'clubs')))

    def test_action_basic_strategy_pair(self):
        player = Player({'game_settings': PlayerTest.game_settings})
        hand = build_hand('soft_pair')

        self.assertEqual(PlayerAction.SPLIT, player.action(hand, Card('K', 10, 'clubs')))

    def test_action_basic_strategy_soft(self):
        player = Player({'game_settings': PlayerTest.game_settings})
        hand = build_hand('soft')

        self.assertEqual(PlayerAction.HIT, player.action(hand, Card('K', 10, 'clubs')))

    def test_action_dealer_hit(self):
        dealer = Player.dealer(PlayerTest.game_settings)
        hand = build_hand('soft')

        self.assertEqual(PlayerAction.HIT, dealer.action(hand, None))

    def test_action_dealer_stand(self):
        dealer = Player.dealer(PlayerTest.game_settings)
        hand = build_hand('hard')

        self.assertEqual(PlayerAction.STAND, dealer.action(hand, None))

    def test_calculate_hand_results(self):
        player = Player({'game_settings': PlayerTest.game_settings})

        hands = [
            build_hand('blackjack'),
            build_hand('hard'),
            build_hand('bust')
        ]

        player.hands = hands
        dealer_hand = build_hand('hard_pair')

        bankroll_start = player.bankroll

        player.calculate_hand_results(dealer_hand)

        self.assertEqual(player.hands[0].bet * PlayerTest.game_settings.blackjack_payout,
                         player.hands[0].winnings)
        self.assertEqual(PlayerTest.game_settings.min_bet, player.hands[1].winnings)
        self.assertEqual(0, player.hands[2].winnings)
        self.assertEqual(bankroll_start +
                         player.hands[0].bet * 2 +
                         player.hands[1].bet +
                         player.hands[1].bet * PlayerTest.game_settings.blackjack_payout,
                         player.bankroll)

    def test_dealer(self):
        dealer = Player.dealer(PlayerTest.game_settings)
        self.assertEqual(True, dealer.dealer)

    def test_new_hand(self):
        bankroll = 100
        player = Player({'bankroll': bankroll, 'game_settings': PlayerTest.game_settings})

        hand = player.new_hand(bet=PlayerTest.game_settings.min_bet)

        self.assertEqual(bankroll - PlayerTest.game_settings.min_bet, player.bankroll)
        self.assertEqual(1, len(player.hands))
        self.assertEqual(1, hand.number)
        self.assertEqual(PlayerTest.game_settings.min_bet, hand.bet)

    def test_reset_hands(self):
        player = Player({'game_settings': PlayerTest.game_settings})
        self.assertEqual(0, len(player.hands))

        player.new_hand()
        player.reset_hands()
        self.assertEqual(0, len(player.hands))


class PlayerActionTest(TestCase):
    def test___str__(self):
        self.assertEqual('Double Down', str(PlayerAction.DOUBLE_DOWN))
