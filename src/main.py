from typing import Dict
from fastapi import FastAPI, HTTPException
# Importamos as exceções personalizadas
from src.game import Game, GameError, InvalidMoveError, NotYourTurnError
from src.patterns import MatchCounterObserver

app = FastAPI(title="UNO Básico Refatorado", description="UNO simplificado")

games_db: Dict[int, Game] = {}
next_game_id = 0
global_match_stats = MatchCounterObserver()

@app.get("/novoJogo")
async def novo_jogo(quantidadeJog: int):
    global next_game_id
    if not 2 <= quantidadeJog <= 10:
        raise HTTPException(status_code=400, detail="Jogadores entre 2 e 10")

    game_id = next_game_id
    next_game_id += 1
    games_db[game_id] = Game(num_players=quantidadeJog, observer=global_match_stats)
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
    try:
        return {"hand": games_db[id_jogo].get_player_hand(id_jogador)}
    except ValueError:
        raise HTTPException(status_code=404, detail="Jogador inválido")

@app.put("/jogo/{id_jogo}/jogar")
async def jogar_carta(id_jogo: int, id_jogador: int, id_carta: int):
    if id_jogo not in games_db:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")
    game = games_db[id_jogo]
    try:
        msg = game.play_card(id_jogador, id_carta)
        return {
            "message": "Jogada realizada", 
            "action_result": msg, 
            "next_player": game.current_player_id
        }
    # Captura erros específicos 
    except (InvalidMoveError, NotYourTurnError, IndexError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    # Captura qualquer outro erro de jogo
    except GameError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/jogo/{id_jogo}/passa")
async def passar_a_vez(id_jogo: int, id_jogador: int):
    if id_jogo not in games_db:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")
    try:
        new_card = games_db[id_jogo].draw_and_pass(id_jogador)
        return {
            "message": "Passou a vez", 
            "new_card": new_card, 
            "next_player": games_db[id_jogo].current_player_id
        }
    except NotYourTurnError as e:
        raise HTTPException(status_code=400, detail=str(e))