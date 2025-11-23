from typing import List, Optional
from src.patterns import DeckFacade, Card, GameSubject, match_stats

class Game(GameSubject):
    def __init__(self, num_players: int):
        super().__init__()
        self.attach(match_stats)
        
        self.num_players = num_players
        self.current_player_id = 0
        self.winner: Optional[int] = None
        
        self.deck_manager = DeckFacade() 
        self.players_hands: List[List[Card]] = [[] for _ in range(num_players)]
        
        self._start_game()
        
        self.notify("NEW_GAME")

    def _start_game(self):
        for _ in range(5):
            for player_idx in range(self.num_players):
                card = self.deck_manager.draw_card()
                self.players_hands[player_idx].append(card)
        
        self.deck_manager.get_top_card()

    def is_move_valid(self, card_to_play: Card) -> bool:
        top_card = self.deck_manager.get_top_card()
        return (card_to_play.color == top_card.color or 
                card_to_play.value == top_card.value)

    def next_turn(self):
        self.current_player_id = (self.current_player_id + 1) % self.num_players

    def play_card(self, player_id: int, card_idx: int) -> str:
        card = self.players_hands[player_id][card_idx]
        
        self.players_hands[player_id].pop(card_idx)
        self.deck_manager.add_to_discard(card)
        
        msg = card.action_strategy.execute(self)
        
        if not self.players_hands[player_id]:
            self.winner = player_id
            return f"UNO! O Jogador {player_id} venceu!"
            
        return msg

    def draw_and_pass(self, player_id: int) -> Card:
        new_card = self.deck_manager.draw_card()
        self.players_hands[player_id].append(new_card)
        self.next_turn()
        return new_card