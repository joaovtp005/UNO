from typing import Dict
from fastapi import FastAPI, HTTPException
from src.game import Game
from src.patterns import MatchCounterObserver

app = FastAPI(title="UNO Básico", description="UNO simplificado")

games_db: Dict[int, Game] = {}
next_game_id = 0

# Instância única gerenciada pelo app (Singleton explícito)
global_match_stats = MatchCounterObserver()

@app.get("/novoJogo")
async def novo_jogo(quantidadeJog: int):
    global next_game_id
    if not 2 <= quantidadeJog <= 10:
        raise HTTPException(status_code=400, detail="Jogadores entre 2 e 10")

    game_id = next_game_id
    next_game_id += 1
    
    # Injeta o observer global
    new_game = Game(num_players=quantidadeJog, observer=global_match_stats)
    games_db[game_id] = new_game
    
    return {"game_id": game_id}

@app.get("/stats/partidas")
async def estatisticas_partidas():
    return {"partidas_iniciadas": global_match_stats.match_count}

@app.get("/jogo/{id_jogo}/jogador_da_vez")
async def jogador_da_vez(id_jogo: int):
    if id_jogo not in games_db:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")
    game = games_db[id_jogo]
    if game.winner is not None:
        return {"message": f"Vencedor: {game.winner}"}
    return {"current_player_id": game.current_player_id}

@app.get("/jogo/{id_jogo}/{id_jogador}")
async def ver_cartas(id_jogo: int, id_jogador: int):
    if id_jogo not in games_db:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")
    return {"hand": games_db[id_jogo].players_hands[id_jogador]}

@app.put("/jogo/{id_jogo}/jogar")
async def jogar_carta(id_jogo: int, id_jogador: int, id_carta: int):
    if id_jogo not in games_db:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")
    game = games_db[id_jogo]

    if game.winner is not None:
         raise HTTPException(status_code=400, detail="O jogo já acabou")
    if id_jogador != game.current_player_id:
        raise HTTPException(status_code=400, detail="Não é sua vez")
    if not 0 <= id_carta < len(game.players_hands[id_jogador]):
        raise HTTPException(status_code=400, detail="Índice inválido")

    card = game.players_hands[id_jogador][id_carta]
    
    if game.is_move_valid(card):
        msg = game.play_card(id_jogador, id_carta)
        return {
            "message": "Jogada realizada", 
            "action_result": msg,
            "next_player": game.current_player_id
        }
    else:
        raise HTTPException(status_code=400, detail="Jogada inválida")

@app.put("/jogo/{id_jogo}/passa")
async def passar_a_vez(id_jogo: int, id_jogador: int):
    if id_jogo not in games_db:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")
    game = games_db[id_jogo]
    
    if id_jogador != game.current_player_id:
        raise HTTPException(status_code=400, detail="Não é sua vez")

    new_card = game.draw_and_pass(id_jogador)
    return {"message": "Passou a vez", "new_card": new_card, "next_player": game.current_player_id}