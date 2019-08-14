from enum import Enum


class HandResult(Enum):
    WIN = 1
    PUSH = 2
    LOSE = 3

    def __str__(self):
        return str(self.name).title()


class Hand:
    def __init__(self, bet=10, number=1):
        self.bet = bet
        self.blackjack = False
        self.bust = False
        self.cards = []
        self.number = number
        self.result = None
        self.soft = False
        self.score = 0
        self.winnings = 0

    def __update_score(self):
        self.score = sum([card.value for card in self.cards])

        ace_count = 0
        hard_ace_count = 0

        for card in self.cards:
            if card.rank == 'A':
                ace_count += 1

                if self.score > 21:
                    hard_ace_count += 1
                    self.score -= 10

        if ace_count > hard_ace_count:
            self.soft = True
        else:
            self.soft = False

        if self.score > 21:
            self.bust = True

        if self.score == 21 and len(self.cards) == 2:
            self.blackjack = True

    def calculate_result(self, dealer_hand):
        if not self.bust and (dealer_hand.bust or (self.score > dealer_hand.score)):
            self.result = HandResult.WIN
        elif not self.bust and (self.score == dealer_hand.score):
            self.result = HandResult.PUSH
        else:
            self.result = HandResult.LOSE

        return self.result

    def deal(self, card):
        self.cards.append(card)
        self.__update_score()
