from unittest import TestCase

from blackjack.cards import CARDS_PER_DECK
from blackjack.cards import Card
from blackjack.cards import Deck
from blackjack.cards import Shoe


class TestCard(TestCase):
    test_card_rank = '2'
    test_card_value = 2
    test_card_suit = 'clubs'

    def test___str__(self):
        card = Card(TestCard.test_card_rank, TestCard.test_card_value, TestCard.test_card_suit)
        self.assertEqual(str(card), '{} - {}'.format(TestCard.test_card_rank, TestCard.test_card_suit.title()))


class TestDeck(TestCase):
    def test___init__(self):
        deck = Deck()

        self.assertEqual(len(set(deck.cards)), len(deck.cards))
        self.assertEqual(CARDS_PER_DECK, len(deck.cards))


class TestShoe(TestCase):
    test_shoe_sizes = [1, 4, 8]

    def test___init__(self):
        with self.assertRaises(ValueError):
            Shoe(num_decks=0)

    def test_draw(self):
        shoe = Shoe(num_decks=1)

        card_count_pre_draw = shoe.num_cards
        last_card = shoe.cards[-1]
        drawn_card = shoe.draw()

        self.assertEqual(last_card, drawn_card)
        self.assertEqual(card_count_pre_draw - 1, shoe.num_cards)

        shoe.stop_card = shoe.num_cards
        shoe.draw()

        self.assertTrue(shoe.last_round)

        shoe.cards = []
        with self.assertRaises(IndexError):
            shoe.draw()

    def test_reset(self):
        for num_decks in TestShoe.test_shoe_sizes:
            shoe = Shoe(num_decks=num_decks)

            shoe.reset()

            self.assertEqual(CARDS_PER_DECK * num_decks, shoe.num_cards)
            self.assertEqual(False, shoe.last_round)

    def test_shuffle(self):
        for num_decks in TestShoe.test_shoe_sizes:
            shoe = Shoe(num_decks=num_decks)
            cards_pre_shuffle = shoe.cards[:]

            shoe.shuffle()

            self.assertEqual(CARDS_PER_DECK * num_decks, shoe.num_cards)
            self.assertNotEqual(cards_pre_shuffle, shoe.cards)
            self.assertIsNotNone(shoe.stop_card)
