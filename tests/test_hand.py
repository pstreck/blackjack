from unittest import TestCase

from blackjack.hand import HandResult
from tests.data import HANDS
from tests.utils import build_hand


class TestHand(TestCase):
    test_hand_data = [
    ]

    def __validate_hand(self, hand_type):
        hand = build_hand(hand_type)

        self.assertEqual(HANDS[hand_type]['blackjack'], hand.blackjack)
        self.assertEqual(HANDS[hand_type]['bust'], hand.bust)
        self.assertEqual(HANDS[hand_type]['score'], hand.score)
        self.assertEqual(HANDS[hand_type]['soft'], hand.soft)

    def test_calculate_result_bust(self):
        dealer_hand = build_hand('hard')
        hand = build_hand('bust')

        self.assertEqual(HandResult.LOSE, hand.calculate_result(dealer_hand))

    def test_calculate_result_dealer_bust(self):
        dealer_hand = build_hand('bust')
        hand = build_hand('hard')

        self.assertEqual(HandResult.WIN, hand.calculate_result(dealer_hand))

    def test_calculate_result_lose(self):
        dealer_hand = build_hand('hard')
        hand = build_hand('soft')

        self.assertEqual(HandResult.LOSE, hand.calculate_result(dealer_hand))

    def test_calculate_result_push(self):
        dealer_hand = build_hand('hard')
        hand = build_hand('hard')

        self.assertEqual(HandResult.PUSH, hand.calculate_result(dealer_hand))

    def test_calculate_result_win(self):
        dealer_hand = build_hand('soft')
        hand = build_hand('hard')

        self.assertEqual(HandResult.WIN, hand.calculate_result(dealer_hand))

    def test_deal_blackjack(self):
        self.__validate_hand('blackjack')

    def test_deal_bust(self):
        self.__validate_hand('bust')

    def test_deal_hard(self):
        self.__validate_hand('hard')

    def test_deal_soft(self):
        self.__validate_hand('soft')


class TestHandResult(TestCase):
    def test___str__(self):
        self.assertEqual('Win', str(HandResult.WIN))
