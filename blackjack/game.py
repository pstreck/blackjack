from blackjack.cards import Shoe
from blackjack.player import Player
from blackjack.player import PlayerAction


class GameSettings:
    def __init__(self, blackjack_payout=1.5, min_bet=10, max_bet=1000, num_decks=8):
        self.blackjack_payout = blackjack_payout
        self.min_bet = min_bet
        self.max_bet = max_bet
        self.num_decks = num_decks


class Game:
    def __init__(self, settings=None):
        self.settings = settings if settings else GameSettings()
        self.players = [Player.dealer(self.settings)]
        self.round_count = 0
        self.shoe = Shoe(num_decks=self.settings.num_decks)

    def add_player(self, player_settings=None):
        player_settings = player_settings if player_settings else {}
        player_settings['game_settings'] = self.settings

        player_settings['number'] = len(self.players)
        self.players.insert(len(self.players) - 1, Player(player_settings))

    def play_hand(self, player, hand):
        stop = False

        if len(hand.cards) == 1:
            hand.deal(self.shoe.draw())

        dealer_card = self.players[-1].hands[0].cards[1]

        while not stop:
            action = player.action(hand, dealer_card)

            if action == PlayerAction.HIT:
                hand.deal(self.shoe.draw())
            elif action == PlayerAction.DOUBLE_DOWN:
                player.bankroll -= hand.bet
                hand.bet *= 2
                hand.deal(self.shoe.draw())
                stop = True
            elif action == PlayerAction.SPLIT:
                split_hand = player.new_hand(bet=hand.bet)
                split_hand.cards.append(hand.cards.pop())

                hand.deal(self.shoe.draw())
            elif action == PlayerAction.STAND:
                stop = True

            if hand.score >= 21:
                stop = True

    def play_round(self):
        self.round_count += 1

        for player in self.players:
            player.reset_hands()
            player.new_hand()

        for _ in range(2):
            for player in self.players:
                for hand in player.hands:
                    hand.deal(self.shoe.draw())

        for player in self.players:
            for hand in player.hands:
                self.play_hand(player, hand)

        for player in self.players[:-1]:
            player.calculate_hand_results(self.players[-1].hands[0])

        if self.shoe.last_round:
            self.shoe.reset()

    def start(self, rounds=25):
        self.shoe.reset()

        for _ in range(rounds):
            self.play_round()
