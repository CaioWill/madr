from datetime import date

from pydantic import BaseModel


class EmprestimosSchema(BaseModel):
    livro: str
    author: str
    data_entrega: date


class Emprestimos_public(EmprestimosSchema):
    solicitador: str
    ativo: bool


class ListEmprestimos(BaseModel):
    emprestimos: list[Emprestimos_public]


class DevolverEmprestimo(BaseModel):
    nome_livro: str
    nome_author: str
