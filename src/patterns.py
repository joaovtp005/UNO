from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from enum import Enum
import random

# Constante para evitar Magic Number
INITIAL_HAND_SIZE = 5

class Color(str, Enum):
    RED = "Red"
    GREEN = "Green"
    BLUE = "Blue"
    YELLOW = "Yellow"

@dataclass
class Card:
    color: Color
    value: str
    action_strategy: 'ICardStrategy'

class ICardStrategy(ABC):
    @abstractmethod
    def execute(self, game_context) -> str:
        pass

class NumberCardStrategy(ICardStrategy):
    def execute(self, game_context) -> str:
        game_context.next_turn()
        return "Turno passado para o próximo jogador."

class CardFactory:
    @staticmethod
    def create_card(color: Color, value: str) -> Card:
        strategy = NumberCardStrategy()
        return Card(color=color, value=value, action_strategy=strategy)

class DeckFacade:
    def __init__(self):
        self._deck: List[Card] = []
        self._discard_pile: List[Card] = []
        self._initialize_deck()

    def _initialize_deck(self):
        values = [str(i) for i in range(10)]
        self._deck = []
        for color in Color:
            self._deck.append(CardFactory.create_card(color, "0"))
            for v in values[1:]:
                self._deck.append(CardFactory.create_card(color, v))
                self._deck.append(CardFactory.create_card(color, v))
        self.shuffle()

    def shuffle(self):
        random.shuffle(self._deck)

    def draw_card(self) -> Card:
        if not self._deck:
            if not self._discard_pile:
                raise Exception("Não há cartas para comprar")
            top_card = self._discard_pile.pop()
            self._deck = self._discard_pile
            self._discard_pile = []
            self.shuffle()
            self._discard_pile.append(top_card)
        return self._deck.pop()

    def add_to_discard(self, card: Card):
        self._discard_pile.append(card)

    def get_top_card(self) -> Card:
        if not self._discard_pile:
             self._discard_pile.append(self.draw_card())
        return self._discard_pile[-1]

class IObserver(ABC):
    @abstractmethod
    def update(self, event_type: str):
        pass

class MatchCounterObserver(IObserver):
    def __init__(self):
        self.match_count = 0

    def update(self, event_type: str):
        if event_type == "NEW_GAME":
            self.match_count += 1

class GameSubject:
    def __init__(self):
        self._observers: List[IObserver] = []
    
    def attach(self, observer: IObserver):
        self._observers.append(observer)
    
    def notify(self, event_type: str):
        for observer in self._observers:
            observer.update(event_type)