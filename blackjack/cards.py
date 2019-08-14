import random
from collections import namedtuple
from itertools import product
from random import shuffle

CARD_RANKS = [
    ('2', 2), ('3', 3), ('4', 4), ('5', 5),
    ('6', 6), ('7', 7), ('8', 8), ('9', 9),
    ('10', 10), ('J', 10), ('Q', 10), ('K', 10), ('A', 11)
]

CARD_SUITS = ['clubs', 'diamonds', 'hearts', 'spades']

CARDS_PER_DECK = 52

CUT_CARD_PENETRATION_MIN = 0.25
CUT_CARD_PENETRATION_MAX = 0.75
STOP_CARD_PENETRATION_MIN = 0.6
STOP_CARD_PENETRATION_MAX = 0.7


class Card(namedtuple('Card', ['rank', 'value', 'suit'])):
    def __str__(self):
        return '{} - {}'.format(self.rank, self.suit.title())


class Deck:
    def __init__(self):
        self.cards = [Card(*card_type[0] + (card_type[1],)) for card_type in product(CARD_RANKS, CARD_SUITS)]


class Shoe:
    def __init__(self, num_decks):
        if num_decks <= 0:
            raise ValueError('Shoe must contain one or more decks')

        self.cards = []
        self.last_round = False
        self.num_decks = num_decks
        self.stop_card = None

        self.reset()

    @property
    def num_cards(self):
        return len(self.cards)

    def draw(self):
        if self.num_cards <= 0:
            raise IndexError('Shoe contains no cards`')

        if self.stop_card and self.num_cards <= self.stop_card:
            self.last_round = True

        return self.cards.pop()

    def reset(self):
        self.cards = [card for card in Deck().cards for _ in range(self.num_decks)]
        self.last_round = False
        self.stop_card = None

        self.shuffle()

    def shuffle(self):
        shuffle(self.cards)

        cut_card_min = round(self.num_cards * CUT_CARD_PENETRATION_MIN * self.num_decks)
        cut_card_max = round(self.num_cards * CUT_CARD_PENETRATION_MAX * self.num_decks)

        cut_card = random.randint(cut_card_min, cut_card_max)
        self.cards = self.cards[cut_card:] + self.cards[:cut_card]

        stop_card_min = round(self.num_cards * STOP_CARD_PENETRATION_MIN * self.num_decks)
        stop_card_max = round(self.num_cards * STOP_CARD_PENETRATION_MAX * self.num_decks)

        self.stop_card = random.randint(stop_card_min, stop_card_max)
