from enum import Enum


class Player:
    class State(Enum):
        INIT = 0
        REVEAL_FIRST = 1
        REVEAL_SECOND = 2
        WAIT_TURN = 3
        DECIDE_TAKE_DECK_OR_DISCARDED = 4
        DECIDE_WHERE_TO_PUT = 5
        DECIDE_KEEP_OR_DISCARD = 6
        DECIDE_WHICH_CARD_TO_REVEAL = 7
        WAIT_NEXT_ROUND = 8

    def __init__(self, name: str):
        self.name = name
        self.state = Player.State.INIT
        self.cards = [None]*12
        self.revealed = [False] * len(self.cards)
        self.drawn = None
        self.results = []

    def get_json_state(self):
        return {
            'name': self.name,
            'state': str(self.state),
            'cards': self.get_revealed_cards(),
            'drawn': self.drawn,
            'results': self.results
        }

    def get_revealed_cards(self):
        return [self.cards[i] if self.revealed[i] else None for i in range(0, len(self.cards))]

    def start_game(self, cards: [int]):
        assert(len(cards) == 12)
        self.state = Player.State.REVEAL_FIRST
        self.cards = cards
        self.revealed = [False] * len(self.cards)
        self.drawn = None

    def start_turn(self):
        assert(self.state == Player.State.WAIT_TURN)
        self.state = Player.State.DECIDE_TAKE_DECK_OR_DISCARDED

    def take_discarded(self, card: int):
        assert(self.state == Player.State.DECIDE_TAKE_DECK_OR_DISCARDED)
        self.drawn = card
        self.state = Player.State.DECIDE_WHERE_TO_PUT

    def take_deck(self, card: int):
        assert(self.state == Player.State.DECIDE_TAKE_DECK_OR_DISCARDED)
        self.drawn = card
        self.state = Player.State.DECIDE_KEEP_OR_DISCARD

    def keep(self):
        assert(self.state == Player.State.DECIDE_KEEP_OR_DISCARD)
        self.state = Player.State.DECIDE_WHERE_TO_PUT

    def discard(self) -> int:
        assert(self.state == Player.State.DECIDE_KEEP_OR_DISCARD)
        self.state = Player.State.DECIDE_WHICH_CARD_TO_REVEAL
        card = self.drawn
        self.drawn = None
        return card

    def put(self, card_index: int) -> int:
        assert(self.state == Player.State.DECIDE_WHERE_TO_PUT)
        assert(card_index < len(self.cards))
        old = self.cards[card_index]
        self.cards[card_index] = self.drawn
        self.revealed[card_index] = True
        self.drawn = None
        self.state = Player.State.WAIT_TURN
        return old

    def reveal(self, card_index: int):
        assert(self.state in (Player.State.DECIDE_WHICH_CARD_TO_REVEAL, Player.State.REVEAL_FIRST, Player.State.REVEAL_SECOND))
        assert(card_index < len(self.revealed))
        assert(self.revealed[card_index] is False)
        self.revealed[card_index] = True
        if self.state == Player.State.REVEAL_FIRST:
            self.state = Player.State.REVEAL_SECOND
        else:
            self.state = Player.State.WAIT_TURN

    def next_round(self):
        assert(self.state == Player.State.WAIT_NEXT_ROUND)
        self.state = Player.State.REVEAL_FIRST

    def check_discard_columns(self) -> [int]:
        rev = self.get_revealed_cards()
        for i in range(int(len(self.cards)/3)):
            c0, c1, c2 = rev[3*i+0], rev[3*i+1], rev[3*i+2]
            if (c0 is not None) and (c0 == c1 == c2):
                del self.cards[3*i:3*i+3]
                del self.revealed[3*i:3*i+3]
                return [c0, c1, c2] + self.check_discard_columns()
        return []

    def is_all_revealed(self):
        return all(self.revealed)

    def finish_round(self):
        self.revealed = [True] * len(self.cards)
        self.results.append(sum(self.cards))
        self.state = Player.State.WAIT_NEXT_ROUND
