from typing import List, Optional
from src.patterns import DeckFacade, Card, GameSubject, IObserver, INITIAL_HAND_SIZE

class Game(GameSubject):
    def __init__(self, num_players: int, observer: Optional[IObserver] = None):
        super().__init__()
        if observer:
            self.attach(observer)
        
        self.num_players = num_players
        self.current_player_id = 0
        self.winner: Optional[int] = None
        
        self.deck_manager = DeckFacade() 
        self.players_hands: List[List[Card]] = [[] for _ in range(num_players)]
        
        self._start_game()
        self.notify("NEW_GAME")

    def _start_game(self):
        for _ in range(INITIAL_HAND_SIZE):
            for player_idx in range(self.num_players):
                self.players_hands[player_idx].append(self.deck_manager.draw_card())
        self.deck_manager.get_top_card()

    # Novo método: Encapsula o acesso à mão do jogador
    def get_player_hand(self, player_id: int) -> List[Card]:
        if not 0 <= player_id < self.num_players:
            raise Exception("Jogador inexistente")
        return self.players_hands[player_id]

    def is_move_valid(self, card_to_play: Card) -> bool:
        top_card = self.deck_manager.get_top_card()
        return (card_to_play.color == top_card.color or 
                card_to_play.value == top_card.value)

    def next_turn(self):
        self.current_player_id = (self.current_player_id + 1) % self.num_players

    # Lógica: O jogo se protege de jogadas inválidas agora
    def play_card(self, player_id: int, card_idx: int) -> str:
        if self.winner is not None:
             raise Exception("O jogo já acabou")
        
        if player_id != self.current_player_id:
            raise Exception("Não é sua vez")
            
        hand = self.players_hands[player_id]
        if not 0 <= card_idx < len(hand):
            raise Exception("Índice inválido")

        card = hand[card_idx]
        
        if not self.is_move_valid(card):
            raise Exception("Jogada inválida")

        # Se passou por tudo, executa a jogada
        self.players_hands[player_id].pop(card_idx)
        self.deck_manager.add_to_discard(card)
        
        msg = card.action_strategy.execute(self)
        
        if not self.players_hands[player_id]:
            self.winner = player_id
            return f"UNO! O Jogador {player_id} venceu!"
            
        return msg

    def draw_and_pass(self, player_id: int) -> Card:
        if player_id != self.current_player_id:
            raise Exception("Não é sua vez")
            
        new_card = self.deck_manager.draw_card()
        self.players_hands[player_id].append(new_card)
        self.next_turn()
        return new_card