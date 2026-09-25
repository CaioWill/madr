# MADR - API

Essa API funciona como uma biblioteca, onde você pode criar uma conta e fazer login, criar contas de admin para cadastrar autores e livros, e onde usuários conseguem visualizar e criar empréstimos dos livros.

A aplicação foi construída usando o framework FastAPI, e os testes foram escritos usando a biblioteca Pytest.

Aplicação desenvolvida como projeto final (TCC) do curso FastAPI do Zero (Dunossauro), para comprovar que aprendi os conteúdos ensinados e consigo colocá-los em prática.

## Instruções de instalação

```bash
poetry install
alembic upgrade head
```

### Pré-requisitos
`Python 3.13`

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
DATABASE_URL=          # conexão com o banco de dados
SECRET_KEY=             # chave usada para assinar/verificar o JWT
ALGORITHM=               # algoritmo de assinatura do JWT (ex: HS256)
ACCESS_TOKEN_EXPIRE_MINUTES=   # tempo de validade do token de acesso, em minutos
ADMIN_KEY=              # senha para o endpoint de alteração de conta para admin
```

## Instruções de uso

Para iniciar a aplicação, rode o comando na pasta raiz:

```bash
poetry run fastapi dev madr/app.py
```

## Como rodar com o Docker

```bash
docker compose up -d
```

## Como rodar os testes

```bash
pytest -vv --cov=madr
coverage html
```

## Documentação da API (Swagger)

Esta API foi desenvolvida com **FastAPI** e utiliza a especificação OpenAPI para documentar todos os endpoints automaticamente.

Para visualizar todas as rotas disponíveis, os parâmetros aceitos e realizar testes práticos em ambiente de desenvolvimento:

1. Certifique-se de que a aplicação está rodando localmente (`fastapi dev` ou `uvicorn...`).
2. Acesse o painel interativo pelo navegador em: **[http://localhost:8000/docs](http://localhost:8000/docs)**

> 💡 **Dica:** O FastAPI também disponibiliza uma documentação alternativa no formato ReDoc em `http://localhost:8000/redoc`.