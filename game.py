import itertools
import random
from enum import Enum
from player import Player


class Game:
    class State(Enum):
        INIT = 0
        WAIT_REVEAL = 1
        RUNNING = 2
        ROUND_FINISHED = 3

    def __init__(self, name: str):
        self.name = name
        self.players = []
        self.deck = []
        self.discard_pile = []
        self.active_player_index = 0
        self.state = Game.State.INIT
        self.finish_at_player = None
        self.start_player_index = None

    def create_player(self, player_name: str):
        assert(self.state == Game.State.INIT)
        return self.add_player(Player(name=player_name))

    def get_player(self, player_name: str):
        for p in self.players:
            if p.name == player_name:
                return p
        return None

    def get_or_create_player(self, player_name):
        player = self.get_player(player_name)
        if player is None:
            player = self.create_player(player_name)
        return player

    def get_active_player(self) -> Player:
        return self.players[self.active_player_index]

    def add_player(self, player: Player):
        assert(self.state == Game.State.INIT)
        self.players.append(player)
        return player

    def start(self):
        assert(self.state in (Game.State.INIT, Game.State.ROUND_FINISHED))
        if self.state == Game.State.INIT:
            self.start_player_index = random.randint(0, len(self.players) - 1)
        else:
            self.start_player_index = (self.start_player_index + 1) % len(self.players)

        self.finish_at_player = None
        self.active_player_index = self.start_player_index

        self.deck = self.generate_deck()
        for p in self.players:
            p.start_game([self.draw_card_from_deck() for _ in range(12)])

        self.discard_pile = [self.draw_card_from_deck()]
        self.state = Game.State.WAIT_REVEAL

    def next_player(self):
        player = self.get_active_player()

        for card in player.check_discard_columns():
            self.discard_card(card)

        if player.is_all_revealed() and (self.finish_at_player is None):
            self.finish_at_player = player

        self.active_player_index = (self.active_player_index + 1) % len(self.players)
        player = self.get_active_player()
        if player == self.finish_at_player:
            self.finish_round()
        else:
            player.start_turn()

    def finish_round(self):
        for p in self.players:
            p.finish_round()
        self.state = Game.State.ROUND_FINISHED

    def take_discarded(self, player: Player):
        assert(self.state == Game.State.RUNNING)
        self.assert_my_turn(player).take_discarded(self.draw_card_from_discard_pile())

    def take_deck(self, player: Player):
        assert(self.state == Game.State.RUNNING)
        self.assert_my_turn(player).take_deck(self.draw_card_from_deck())

    def keep(self, player: Player):
        assert(self.state == Game.State.RUNNING)
        self.assert_my_turn(player).keep()

    def discard(self, player: Player):
        assert(self.state == Game.State.RUNNING)
        self.discard_card(self.assert_my_turn(player).discard())

    def put(self, player: Player, card_index: int):
        assert(self.state == Game.State.RUNNING)
        self.assert_my_turn(player)
        self.discard_card(player.put(card_index=card_index))
        self.next_player()

    def reveal(self, player: Player, card_index: int):
        assert(self.state in (Game.State.WAIT_REVEAL, Game.State.RUNNING))
        if self.state == Game.State.WAIT_REVEAL:
            player.reveal(card_index=card_index)
            if all([p.state == Player.State.WAIT_TURN for p in self.players]):
                self.state = Game.State.RUNNING
                self.get_active_player().start_turn()
        else:
            self.assert_my_turn(player)
            player.reveal(card_index=card_index)
            self.next_player()

    def next_round(self, player: Player):
        assert(self.state == Game.State.ROUND_FINISHED)
        player.next_round()
        if all([p.state != Player.State.WAIT_NEXT_ROUND for p in self.players]):
            self.start()

    def draw_card_from_deck(self) -> int:
        return self.deck.pop()

    def draw_card_from_discard_pile(self) -> int:
        return self.discard_pile.pop()

    def discard_card(self, card: int):
        self.discard_pile.append(card)

    def assert_my_turn(self, player: Player) -> Player:
        active_player = self.get_active_player()
        assert(active_player == player)
        return active_player

    def get_json_state(self):
        return {
            'name': self.name,
            'state': str(self.state),
            'players': [p.get_json_state() for p in self.players],
            'active_player': self.active_player_index,
            'discard_pile': self.discard_pile
        }

    @staticmethod
    def generate_deck() -> [int]:
        cards = [0]*15 + [-2] * 5 + [-1] * 10 + list(itertools.chain.from_iterable([[i]*10 for i in range(1, 13)]))
        random.shuffle(cards)
        return cards
