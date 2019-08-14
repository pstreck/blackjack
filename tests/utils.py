from blackjack.hand import Hand
from tests.data import HANDS


def build_hand(hand_type):
    hand = Hand()
    for card in HANDS[hand_type]['cards']:
        hand.deal(card)

    return hand
