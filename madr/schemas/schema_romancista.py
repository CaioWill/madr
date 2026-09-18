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


class ListLivros(BaseModel):
    livros: list[LivrosSchema]


class DelLivro(BaseModel):
    author: str
    livro: str
