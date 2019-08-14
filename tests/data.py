from blackjack.cards import Card

HANDS = {
    'blackjack': {
        'cards': [Card('Q', 10, 'clubs'), Card('A', 11, 'spades')],
        'score': 21,
        'blackjack': True,
        'bust': False,
        'soft': True
    },
    'bust': {
        'cards': [Card('5', 5, 'hearts'), Card('K', 10, 'diamonds'), Card('J', 10, 'clubs')],
        'score': 25,
        'blackjack': False,
        'bust': True,
        'soft': False,
    },
    'double_down': {
        'cards': [Card('5', 5, 'hearts'), Card('6', 6, 'diamonds')],
        'score': 11,
        'blackjack': False,
        'bust': False,
        'soft': False,
    },
    'hard': {
        'cards': [Card('10', 10, 'clubs'), Card('7', 7, 'spades')],
        'score': 17,
        'blackjack': False,
        'bust': False,
        'soft': False
    },
    'hard_pair': {
        'cards': [Card('8', 8, 'clubs'), Card('8', 8, 'spades')],
        'score': 16,
        'blackjack': False,
        'bust': False,
        'soft': False
    },
    'soft': {
        'cards': [Card('A', 11, 'clubs'), Card('2', 2, 'spades')],
        'score': 13,
        'blackjack': False,
        'bust': False,
        'soft': True
    },
    'soft_pair': {
        'cards': [Card('A', 11, 'clubs'), Card('A', 11, 'spades')],
        'score': 12,
        'blackjack': False,
        'bust': False,
        'soft': True
    },
    'three_card_11': {
        'cards': [Card('5', 5, 'hearts'), Card('4', 4, 'diamonds'), Card('2', 2, 'clubs')],
        'score': 11,
        'blackjack': False,
        'bust': False,
        'soft': False,

    }
}
