from datetime import date

from pydantic import BaseModel


class RomancistaSchema(BaseModel):
    name: str


class ListRomancistas(BaseModel):
    autores: list[RomancistaSchema]


class LivrosSchema(BaseModel):
    name: str
    publication: date
    author: str
    estoque: int


class LivrosPublic(BaseModel):
    name: str
    publication: date
    author_id: int
    estoque: int


class ListLivros(BaseModel):
    livros: list[LivrosPublic]


class DelLivro(BaseModel):
    author: str
    livro: str
