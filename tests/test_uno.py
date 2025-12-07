import pytest
from src.patterns import CardFactory, DeckFacade, MatchCounterObserver, NumberCardStrategy, Color, INITIAL_HAND_SIZE
from src.game import Game

def test_card_factory():
    # Uso do Enum Color
    card = CardFactory.create_card(Color.BLUE, "9")
    assert card.color == Color.BLUE
    assert card.value == "9"
    assert isinstance(card.action_strategy, NumberCardStrategy)

def test_deck_facade():
    deck = DeckFacade()
    card = deck.draw_card()
    assert card is not None
    # Verifica se a cor é uma instância válida do Enum
    assert isinstance(card.color, Color)

def test_strategy_execution():
    game = Game(num_players=2)
    initial_player = game.current_player_id
    
    strategy = NumberCardStrategy()
    msg = strategy.execute(game)
    
    assert game.current_player_id != initial_player
    assert msg == "Turno passado para o próximo jogador."

def test_game_initialization():
    game = Game(num_players=3)
    # Uso da constante
    assert len(game.players_hands[0]) == INITIAL_HAND_SIZE
    assert game.deck_manager.get_top_card() is not None