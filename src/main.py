import random
from dataclasses import dataclass
from typing import List, Dict, Optional

from fastapi import FastAPI, HTTPException

@dataclass
class Card:
    color: str
    value: str

class Game:
    def __init__(self, num_players: int):
        self.num_players = num_players
        self.current_player_id = 0
        self.winner: Optional[int] = None
        
        self.deck: List[Card] = self._create_deck()
        self.players_hands: List[List[Card]] = [[] for _ in range(num_players)]
        self.discard_pile: List[Card] = []
        
        self._start_game()

    def _create_deck(self) -> List[Card]:
        colors = ["Red", "Green", "Blue", "Yellow"]
        values = [str(i) for i in range(10)]
        deck = []
        
        for color in colors:
            deck.append(Card(color=color, value="0"))
            for v in values[1:]:
                deck.append(Card(color=color, value=v))
                deck.append(Card(color=color, value=v))
        
        random.shuffle(deck)
        return deck

    def _start_game(self):
        for _ in range(5):
            for player_idx in range(self.num_players):
                self.players_hands[player_idx].append(self.draw_card_from_deck())
        
        self.discard_pile.append(self.draw_card_from_deck())

    def draw_card_from_deck(self) -> Card:
        if not self.deck:
            print("--- REEMBARALHANDO O BARALHO ---")
            top_card = self.discard_pile.pop()
            self.deck = self.discard_pile
            random.shuffle(self.deck)
            self.discard_pile = [top_card]
            
        return self.deck.pop()

    def get_top_card(self) -> Card:
        return self.discard_pile[-1]

    def is_move_valid(self, card_to_play: Card) -> bool:
        top_card = self.get_top_card()
        return (card_to_play.color == top_card.color or 
                card_to_play.value == top_card.value)

    def next_turn(self):
        self.current_player_id = (self.current_player_id + 1) % self.num_players

app = FastAPI(
    title="UNO Básico",
    description="UNO simplificado"
)

games_db: Dict[int, Game] = {}
next_game_id = 0

@app.get("/novoJogo", summary="Inicia um novo jogo")
async def novo_jogo(quantidadeJog: int):
    global next_game_id
    game_id = next_game_id
    next_game_id += 1
    
    if not 2 <= quantidadeJog <= 10:
        raise HTTPException(status_code=400, detail="A quantidade de jogadores deve ser entre 2 e 10.")

    new_game = Game(num_players=quantidadeJog)
    games_db[game_id] = new_game
    
    print(f"Novo jogo criado [ID: {game_id}] com {quantidadeJog} jogadores.")
    return {"game_id": game_id}


@app.get("/jogo/{id_jogo}/jogador_da_vez", summary="Verificar quem é o jogador da vez")
async def jogador_da_vez(id_jogo: int):
    if id_jogo not in games_db:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")
    
    game = games_db[id_jogo]
    
    if game.winner is not None:
        return {"message": f"O jogo acabou! Vencedor: Jogador {game.winner}"}

    return {"current_player_id": game.current_player_id}

@app.get("/jogo/{id_jogo}/{id_jogador}", summary="Ver as cartas de um jogador")
async def ver_cartas(id_jogo: int, id_jogador: int):
    if id_jogo not in games_db:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")
    
    game = games_db[id_jogo]
    
    if not 0 <= id_jogador < game.num_players:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")
        
    return {"hand": game.players_hands[id_jogador]}

@app.put("/jogo/{id_jogo}/jogar", summary="Jogar uma carta")
async def jogar_carta(id_jogo: int, id_jogador: int, id_carta: int):
    if id_jogo not in games_db:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")
    
    game = games_db[id_jogo]

    if game.winner is not None:
        raise HTTPException(status_code=400, detail=f"O jogo já acabou! Vencedor: Jogador {game.winner}")

    if id_jogador != game.current_player_id:
        raise HTTPException(status_code=400, detail="Não é a sua vez de jogar.")

    if not 0 <= id_carta < len(game.players_hands[id_jogador]):
        raise HTTPException(status_code=400, detail="Índice de carta inválido.")

    card_to_play = game.players_hands[id_jogador][id_carta]

    if game.is_move_valid(card_to_play):
        played_card = game.players_hands[id_jogador].pop(id_carta)
        game.discard_pile.append(played_card)
        
        if not game.players_hands[id_jogador]:
            game.winner = id_jogador
            return {"message": f"UNO! O Jogador {id_jogador} venceu o jogo!"}
        
        game.next_turn()
        return {
            "message": "Jogada realizada com sucesso.",
            "next_player": game.current_player_id
        }
    else:
        raise HTTPException(status_code=400, detail="Jogada inválida! A carta não combina com a cor ou valor do topo da pilha.")

@app.put("/jogo/{id_jogo}/passa", summary="Passar a vez (comprar carta)")
async def passar_a_vez(id_jogo: int, id_jogador: int):
    if id_jogo not in games_db:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")
        
    game = games_db[id_jogo]
    
    if game.winner is not None:
        raise HTTPException(status_code=400, detail=f"O jogo já acabou! Vencedor: Jogador {game.winner}")

    if id_jogador != game.current_player_id:
        raise HTTPException(status_code=400, detail="Não é a sua vez de jogar.")
        
    new_card = game.draw_card_from_deck()
    game.players_hands[id_jogador].append(new_card)
    
    game.next_turn()
    
    return {
        "message": "Você comprou uma carta e passou a vez.",
        "new_card": new_card,
        "next_player": game.current_player_id
    }