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

        strategy = BetStrategy(GameSettings(min_bet=limit * 2, max_bet=limit))
        self.assertEqual(limit, strategy.bet())

    def test_bet_limit_player(self):
        limit = 0

        strategy = BetStrategy(BetStrategyTest.game_settings, player_limit=limit)
        self.assertEqual(limit, strategy.bet())

    def test_bet_strategy_martingale(self):
        strategy = BetStrategy(BetStrategyTest.game_settings, strategy_type=BetStrategyType.MARTINGALE)
        self.assertEqual(BetStrategyTest.game_settings.min_bet, strategy.bet())

        strategy.last_hand = Hand()
        strategy.last_hand.result = HandResult.PUSH
        self.assertEqual(BetStrategyTest.game_settings.min_bet, strategy.bet())

        strategy.last_hand.result = HandResult.LOSE
        self.assertEqual(BetStrategyTest.game_settings.min_bet * 2, strategy.bet())

    def test_bet_strategy_parlay(self):
        strategy = BetStrategy(BetStrategyTest.game_settings, strategy_type=BetStrategyType.PARLAY)
        self.assertEqual(BetStrategyTest.game_settings.min_bet, strategy.bet())

        strategy.last_hand = Hand()
        strategy.last_hand.result = HandResult.WIN
        strategy.last_hand.winnings = BetStrategyTest.game_settings.min_bet
        self.assertEqual(BetStrategyTest.game_settings.min_bet * 2, strategy.bet())

    def test_bet_strategy_series(self):
        strategy = BetStrategy(BetStrategyTest.game_settings, strategy_type=BetStrategyType.SERIES)
        with self.assertRaises(ValueError):
            strategy.bet()

        series = [1, 2, 3]
        strategy = BetStrategy(BetStrategyTest.game_settings, series=series, strategy_type=BetStrategyType.SERIES)
        for multiplier in series:
            self.assertEqual(BetStrategyTest.game_settings.min_bet * multiplier, strategy.bet())

        strategy.last_hand = Hand()
        strategy.last_hand.result = HandResult.WIN

        self.assertEqual(BetStrategyTest.game_settings.min_bet, strategy.bet())

    def test_bet_strategy_static(self):
        strategy = BetStrategy(BetStrategyTest.game_settings, strategy_type=BetStrategyType.STATIC)
        self.assertEqual(BetStrategyTest.game_settings.min_bet, strategy.bet())


class BetStrategyTypeTest(TestCase):
    def test___str__(self):
        self.assertEqual('Series', str(BetStrategyType.SERIES))


class PlayerTest(TestCase):
    game_settings = GameSettings(min_bet=10, max_bet=100)

    def test___format__(self):
        player = Player(PlayerTest.game_settings)
        self.assertEqual('Player 1  ', '{:10s}'.format(player))

    def test___str__player(self):
        player = Player(PlayerTest.game_settings)
        self.assertEqual('Player 1', str(player))

    def test___str__dealer(self):
        dealer = Player(PlayerTest.game_settings, dealer=True)
        self.assertEqual('Dealer', str(dealer))

    def test_action_basic_strategy_blackjack(self):
        player = Player(PlayerTest.game_settings)
        hand = build_hand('blackjack')

        self.assertEqual(PlayerAction.STAND, player.action(hand, Card('K', 10, 'clubs')))

    def test_action_basic_strategy_double_down(self):
        player = Player(PlayerTest.game_settings)
        hand = build_hand('double_down')

        self.assertEqual(PlayerAction.DOUBLE_DOWN, player.action(hand, Card('5', 5, 'clubs')))

    def test_action_basic_strategy_double_down_with_three_cards(self):
        player = Player(PlayerTest.game_settings)
        hand = build_hand('three_card_11')

        self.assertEqual(PlayerAction.HIT, player.action(hand, Card('K', 10, 'clubs')))

    def test_action_basic_strategy_hard(self):
        player = Player(PlayerTest.game_settings)
        hand = build_hand('hard')

        self.assertEqual(PlayerAction.STAND, player.action(hand, Card('K', 10, 'clubs')))

    def test_action_basic_strategy_low_bankroll_doubledown(self):
        player = Player(PlayerTest.game_settings, bankroll=0)
        hand = build_hand('soft')
        hand.bet = 1

        self.assertEqual(PlayerAction.HIT, player.action(hand, Card('5', 5, 'clubs')))

    def test_action_basic_strategy_low_bankroll_split_hard(self):
        player = Player(PlayerTest.game_settings, bankroll=0)

        hand = build_hand('hard_pair')
        hand.bet = 1

        self.assertEqual(PlayerAction.STAND, player.action(hand, Card('5', 5, 'clubs')))

    def test_action_basic_strategy_low_bankroll_split_soft(self):
        player = Player(PlayerTest.game_settings, bankroll=0)

        hand = build_hand('soft_pair')
        hand.bet = 1

        self.assertEqual(PlayerAction.HIT, player.action(hand, Card('5', 5, 'clubs')))

    def test_action_basic_strategy_pair(self):
        player = Player(PlayerTest.game_settings)
        hand = build_hand('soft_pair')

        self.assertEqual(PlayerAction.SPLIT, player.action(hand, Card('K', 10, 'clubs')))

    def test_action_basic_strategy_soft(self):
        player = Player(PlayerTest.game_settings)
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
        player = Player(PlayerTest.game_settings)

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
        player = Player(PlayerTest.game_settings, bankroll=bankroll)

        hand = player.new_hand(bet=PlayerTest.game_settings.min_bet)

        self.assertEqual(bankroll - PlayerTest.game_settings.min_bet, player.bankroll)
        self.assertEqual(1, len(player.hands))
        self.assertEqual(1, hand.number)
        self.assertEqual(PlayerTest.game_settings.min_bet, hand.bet)

    def test_reset_hands(self):
        player = Player(PlayerTest.game_settings)
        self.assertEqual(0, len(player.hands))

        player.new_hand()
        player.reset_hands()
        self.assertEqual(0, len(player.hands))


class PlayerActionTest(TestCase):
    def test___str__(self):
        self.assertEqual('Double Down', str(PlayerAction.DOUBLE_DOWN))
