from datetime import date

from pydantic import BaseModel, Field


class RomancistaSchema(BaseModel):
    name: str = Field(
        description='Nome do autor.', examples=['Brando Sanderson']
    )


class ListRomancistas(BaseModel):
    autores: list[RomancistaSchema]


class LivrosSchema(BaseModel):
    name: str = Field(description='Nome do livro.', examples=['Mistborn'])
    publication: date = Field(
        description='Data da publicação', examples=['2000-10-10']
    )
    author: str = Field(
        description='Nome do Autor do livro cadastrado',
        examples=['Brandon Sanderson']
    )
    estoque: int = Field(
        description='Quantidade do estoque.', examples=[2]
    )


class LivrosPublic(BaseModel):
    name: str
    publication: date
    author_id: int
    estoque: int


class ListLivros(BaseModel):
    livros: list[LivrosPublic]


class LivrosPut(BaseModel):
    name: str
    author: str
    new_inventory: int


class DelLivro(BaseModel):
    author: str
    livro: str
