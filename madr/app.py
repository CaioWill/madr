from http import HTTPStatus

from fastapi import FastAPI

from madr.routes import admin, auth, contas
from madr.schemas.schema import Mensagem

app = FastAPI()

app.include_router(contas.router)
app.include_router(auth.router)
app.include_router(admin.router)
# app.include_router(livros.router)
# app.include_router(autores.router)
# app.include_router(emprestimos.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Mensagem)
def pagina_inicial():
    return {'mensagem': 'olá'}
