import pytest
from src.patterns import CardFactory, DeckFacade, MatchCounterObserver, NumberCardStrategy, Color, INITIAL_HAND_SIZE
# Importar as exceções para testar
from src.game import Game, InvalidMoveError, NotYourTurnError

def test_card_factory():
    card = CardFactory.create_card(Color.BLUE, "9")
    assert card.color == Color.BLUE
    assert card.value == "9"

def test_deck_facade():
    deck = DeckFacade()
    card = deck.draw_card()
    assert isinstance(card.color, Color)

def test_strategy_execution():
    game = Game(num_players=2)
    initial_player = game.current_player_id
    strategy = NumberCardStrategy()
    msg = strategy.execute(game)
    assert game.current_player_id != initial_player

def test_observer_match_count_isolated():
    stats1 = MatchCounterObserver()
    _ = Game(num_players=2, observer=stats1)
    assert stats1.match_count == 1

def test_game_initialization():
    game = Game(num_players=3)
    assert len(game.players_hands[0]) == INITIAL_HAND_SIZE



def test_game_validations_exceptions():
    game = Game(num_players=2)
    p1 = game.current_player_id
    p2 = (p1 + 1) % 2
    
    # Verifica se jogar fora de vez lança NotYourTurnError
    with pytest.raises(NotYourTurnError):
        game.play_card(p2, 0)

def test_invalid_move_exception():
    game = Game(num_players=2)
    player = game.current_player_id
    
    top_card = game.deck_manager.get_top_card()
    
    
    diff_color = Color.RED if top_card.color != Color.RED else Color.BLUE
    bad_card = CardFactory.create_card(diff_color, "99") 
    
    # Injeta a carta ruim na mão do jogador 
    game.players_hands[player][0] = bad_card
    
    # Verifica se jogar carta errada lança InvalidMoveError
    with pytest.raises(InvalidMoveError):
        game.play_card(player, 0)