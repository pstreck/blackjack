from enum import Enum

from blackjack.hand import Hand
from blackjack.hand import HandResult


class BetStrategyType(Enum):
    MARTINGALE = 1
    PARLAY = 2
    SERIES = 3
    STATIC = 4

    def __str__(self):
        return str(self.name).title()


class PlayerAction(Enum):
    HIT = 1
    STAND = 2
    DOUBLE_DOWN = 3
    SPLIT = 4

    def __str__(self):
        return str(self.name).replace('_', ' ').title()


CHART_BASIC_STRATEGY = {
    'hard': {
        21: [PlayerAction.STAND] * 10,
        20: [PlayerAction.STAND] * 10,
        19: [PlayerAction.STAND] * 10,
        18: [PlayerAction.STAND] * 10,
        17: [PlayerAction.STAND] * 10,
        16: [PlayerAction.STAND] * 5 + [PlayerAction.HIT] * 5,
        15: [PlayerAction.STAND] * 5 + [PlayerAction.HIT] * 5,
        14: [PlayerAction.STAND] * 5 + [PlayerAction.HIT] * 5,
        13: [PlayerAction.STAND] * 5 + [PlayerAction.HIT] * 5,
        12: [PlayerAction.HIT] * 2 + [PlayerAction.STAND] * 3 + [PlayerAction.HIT] * 5,
        11: [PlayerAction.DOUBLE_DOWN] * 10,
        10: [PlayerAction.DOUBLE_DOWN] * 8 + [PlayerAction.HIT] * 2,
        9: [PlayerAction.HIT] + [PlayerAction.DOUBLE_DOWN] * 4 + [PlayerAction.STAND] * 5,
        8: [PlayerAction.HIT] * 10,
        7: [PlayerAction.HIT] * 10,
        6: [PlayerAction.HIT] * 10,
        5: [PlayerAction.HIT] * 10,
        4: [PlayerAction.HIT] * 10,
    },
    'soft': {
        21: [PlayerAction.STAND] * 10,
        20: [PlayerAction.STAND] * 10,
        19: [PlayerAction.STAND] * 10,
        18: [PlayerAction.STAND] + [PlayerAction.DOUBLE_DOWN] * 4 + [PlayerAction.STAND] * 2 + [PlayerAction.HIT] * 3,
        17: [PlayerAction.HIT] + [PlayerAction.DOUBLE_DOWN] * 4 + [PlayerAction.HIT] * 5,
        16: [PlayerAction.HIT] * 2 + [PlayerAction.DOUBLE_DOWN] * 3 + [PlayerAction.HIT] * 5,
        15: [PlayerAction.HIT] * 2 + [PlayerAction.DOUBLE_DOWN] * 3 + [PlayerAction.HIT] * 5,
        14: [PlayerAction.HIT] * 3 + [PlayerAction.DOUBLE_DOWN] * 2 + [PlayerAction.HIT] * 5,
        13: [PlayerAction.HIT] * 3 + [PlayerAction.DOUBLE_DOWN] * 2 + [PlayerAction.HIT] * 5,
        12: [PlayerAction.HIT] * 10,
    },
    'pair': {
        'A': [PlayerAction.SPLIT] * 10,
        'K': [PlayerAction.STAND] * 10,
        'Q': [PlayerAction.STAND] * 10,
        'J': [PlayerAction.STAND] * 10,
        '10': [PlayerAction.STAND] * 10,
        '9': [PlayerAction.SPLIT] * 5 + [PlayerAction.STAND] + [PlayerAction.SPLIT] * 2 + [PlayerAction.STAND] * 2,
        '8': [PlayerAction.SPLIT] * 10,
        '7': [PlayerAction.SPLIT] * 6 + [PlayerAction.HIT] * 4,
        '6': [PlayerAction.SPLIT] * 5 + [PlayerAction.HIT] * 5,
        '5': [PlayerAction.DOUBLE_DOWN] * 8 + [PlayerAction.HIT] * 2,
        '4': [PlayerAction.HIT] * 3 + [PlayerAction.SPLIT] * 2 + [PlayerAction.HIT] * 5,
        '3': [PlayerAction.SPLIT] * 6 + [PlayerAction.HIT] * 4,
        '2': [PlayerAction.SPLIT] * 6 + [PlayerAction.HIT] * 4,
    }
}


class BetStrategy:
    def __init__(self, game_settings, player_limit=None, series=None, strategy_type=None):
        self.game_settings = game_settings
        self.last_hand = None
        self.player_limit = player_limit
        self.series = series
        self.series_index = 0
        self.strategy_type = strategy_type

        if self.strategy_type == BetStrategyType.MARTINGALE:
            self.strategy = self.__strategy_martingale
        elif self.strategy_type == BetStrategyType.PARLAY:
            self.strategy = self.__strategy_parlay
        elif self.strategy_type == BetStrategyType.SERIES:
            self.strategy = self.__strategy_series
        else:
            self.strategy = self.__strategy_static

    def __strategy_martingale(self):
        bet = self.game_settings.min_bet

        if self.last_hand:
            if self.last_hand.result == HandResult.PUSH:
                bet = self.last_hand.bet
            elif self.last_hand.result == HandResult.LOSE:
                bet = self.last_hand.bet * 2

        return self.__validate_bet(bet)

    def __strategy_parlay(self):
        bet = self.game_settings.min_bet

        if self.last_hand and self.last_hand.result.WIN:
            bet = self.last_hand.bet + self.last_hand.winnings

        return self.__validate_bet(bet)

    def __strategy_series(self):
        if not self.series or not isinstance(self.series, list) or len(self.series) <= 0:
            raise ValueError('Series is not valid')

        if self.series_index == len(self.series) or (self.last_hand and self.last_hand.result == HandResult.WIN):
            self.series_index = 0

        bet = self.game_settings.min_bet * self.series[self.series_index]

        self.series_index += 1
        return self.__validate_bet(bet)

    def __strategy_static(self):
        return self.__validate_bet(self.game_settings.min_bet)

    def __validate_bet(self, bet):
        if self.game_settings.max_bet is not None and bet > self.game_settings.max_bet:
            bet = self.game_settings.max_bet

        if self.player_limit is not None and bet > self.player_limit:
            bet = self.player_limit

        return bet

    def bet(self):
        return self.strategy()


class Player:
    def __init__(self, game_settings, bankroll=100, bet_strategy_type=None,
                 dealer=False, number=1, player_limit=None):
        self.bankroll = bankroll
        self.dealer = dealer
        self.game_settings = game_settings
        self.hands = []
        self.number = number
        self.player_limit = player_limit

        self.bet_strategy = BetStrategy(self.game_settings,
                                        player_limit=self.player_limit,
                                        strategy_type=bet_strategy_type)

    def __str__(self):
        return 'Dealer' if self.dealer else 'Player {}'.format(self.number)

    def __format__(self, format_spec):
        return format(str(self), format_spec)

    def action(self, hand, dealer_card):
        if self.dealer:
            if hand.score < 17 or (hand.score == 17 and hand.soft):
                action = PlayerAction.HIT
            else:
                action = PlayerAction.STAND
        else:
            chart_value = hand.score

            if len(hand.cards) == 2 and hand.cards[0].rank == hand.cards[1].rank:
                chart_key = 'pair'
                chart_value = hand.cards[0].rank
            elif hand.soft:
                chart_key = 'soft'
            else:
                chart_key = 'hard'

            chart_index = dealer_card.value - 2

            action = CHART_BASIC_STRATEGY[chart_key][chart_value][chart_index]

            if action == PlayerAction.DOUBLE_DOWN and len(hand.cards) > 2:
                action = PlayerAction.HIT

            if hand.bet > self.bankroll and action != PlayerAction.HIT and action != PlayerAction.STAND:
                if action == PlayerAction.DOUBLE_DOWN:
                    action = PlayerAction.HIT
                elif action == PlayerAction.SPLIT:
                    if hand.soft:
                        chart_key = 'soft'
                    else:
                        chart_key = 'hard'

                    action = CHART_BASIC_STRATEGY[chart_key][hand.score][chart_index]

        return action

    def calculate_hand_results(self, dealer_hand):
        for hand in self.hands:
            hand.calculate_result(dealer_hand)

            if hand.result == HandResult.WIN:
                hand.winnings = hand.bet if not hand.blackjack else hand.bet * self.game_settings.blackjack_payout

            if not hand.result == HandResult.LOSE:
                self.bankroll += hand.bet + hand.winnings

        self.bet_strategy.last_hand = self.hands[-1]

    @classmethod
    def dealer(cls, game_settings):
        return cls(game_settings, dealer=True)

    def new_hand(self, bet=None):
        hand_number = len(self.hands) + 1

        if not self.dealer:
            if not bet:
                bet = self.bet_strategy.bet()

            self.bankroll -= bet

        hand = Hand(bet=bet, number=hand_number)
        self.hands.append(hand)

        return hand

    def reset_hands(self):
        self.hands = []
