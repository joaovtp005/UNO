# UNO (Versão Simplificada)

> Projeto acadêmico de back-end para um jogo de UNO, utilizando FastAPI. Este projeto implementa as regras básicas de jogo.

---

## 🛠️ Tecnologias Utilizadas

* **Python 3.10+**
* **FastAPI:** Para a criação da API REST.
* **Uvicorn:** Como servidor ASGI para rodar a aplicação.

## ✨ Funcionalidades

* **Preparação:** Iniciar um novo jogo, definir a quantidade de jogadores e distribuir 5 cartas.
* **Status do Jogo:** Verificar as cartas na mão de um jogador e saber quem é o jogador da vez.
* **Rodada:** Jogar uma carta válida (combinando cor ou valor) ou passar a vez (comprando uma carta).
* **Vitória:** Detectar quando um jogador fica sem cartas.

## ⚙️ Como Executar Localmente

Siga os passos abaixo para rodar o projeto em sua máquina.

**1. Clone o Repositório**
```bash
git clone https://github.com/keilarobertasv/UNO.git
cd uno
```

**2. Crie um Ambiente Virtual**
```bash
# Para Windows
python -m venv venv
.\venv\Scripts\activate

# Para macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Instale as Dependências**
O arquivo `requirements.txt` contém tudo o que é necessário.
```bash
pip install -r requirements.txt
```

**4. Inicie o Servidor**
O Uvicorn será usado para iniciar a API. O `--reload` faz o servidor reiniciar automaticamente se você alterar o código.
```bash
uvicorn src.main:app --reload
```

**5. Acesse a Documentação!**
Abra seu navegador e acesse:
[**http://127.0.0.1:8000/docs**](http://127.0.0.1:8000/docs)

Você verá a documentação interativa (Swagger UI) onde pode testar todos os endpoints.

---

## 📚 Endpoints da API

Abaixo está o detalhamento de todas as rotas disponíveis.

### Preparação
`GET /novoJogo`
* Inicia uma nova partida.
* **Query Params:** `quantidadeJog` (int) - Número de jogadores.
* **Retorno:** `{"game_id": int}`

### Verificar Status do Jogo
`GET /jogo/{id_jogo}/{id_jogador}`
* Retorna a mão (lista de cartas) do jogador especificado.
* **Retorno:** `{"hand": [Cartas]}`

`GET /jogo/{id_jogo}/jogador_da_vez`
* Retorna o ID do jogador atual (jogador da vez).
* **Retorno:** `{"current_player_id": int}`

### Rodada
`PUT /jogo/{id_jogo}/jogar`
* Tenta jogar uma carta da mão do jogador.
* **Query Params:**
    * `id_jogador` (int)
    * `id_carta` (int) - O *índice* da carta na mão do jogador (ex: 0, 1, 2...).
* **Retorno (Sucesso):** Mensagem de sucesso ou de vitória.
* **Retorno (Erro):** Mensagem de "Não é sua vez" ou "Jogada inválida".

`PUT /jogo/{id_jogo}/passa`
* O jogador compra uma carta do baralho e passa a vez.
* **Query Params:** `id_jogador` (int)
* **Retorno:** Mensagem de sucesso e a carta comprada.