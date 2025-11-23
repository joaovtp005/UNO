import pytest
from src.patterns import CardFactory, DeckFacade, MatchCounterObserver, NumberCardStrategy
from src.game import Game

def test_card_factory():
    card = CardFactory.create_card("Blue", "9")
    assert card.color == "Blue"
    assert card.value == "9"
    assert isinstance(card.action_strategy, NumberCardStrategy)

def test_deck_facade():
    deck = DeckFacade()
    card = deck.draw_card()
    assert card is not None
    assert card.color in ["Red", "Green", "Blue", "Yellow"]

def test_strategy_execution():
    game = Game(num_players=2)
    initial_player = game.current_player_id
    
    strategy = NumberCardStrategy()
    msg = strategy.execute(game)
    
    assert game.current_player_id != initial_player
    assert msg == "Turno passado para o próximo jogador."

def test_observer_match_count():
    from src.patterns import match_stats
    initial_count = match_stats.match_count
    
    _ = Game(num_players=2)
    
    assert match_stats.match_count == initial_count + 1

def test_game_initialization():
    game = Game(num_players=3)
    assert len(game.players_hands[0]) == 5
    assert game.deck_manager.get_top_card() is not None