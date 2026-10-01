from http import HTTPStatus

from fastapi import FastAPI

from madr.routes import accounts, admin, auth, authors, books, loans
from madr.schemas.schema import Mensagem

app = FastAPI(
    title='Biblioteca API',
    description=(
        'API para fazer o gerenciamento de autores, livros e emprestimos'
    ),
    version='1.0.1',
)

app.include_router(accounts.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(books.router)
app.include_router(authors.router)
app.include_router(loans.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Mensagem)
def pagina_inicial():
    return {'mensagem': 'Olá, Adicione um /docs no link.'}
