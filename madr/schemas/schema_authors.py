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
        examples=['Brandon Sanderson'],
    )
    stock: int = Field(description='Quantidade do estoque.', examples=[2])


class LivrosPublic(BaseModel):
    name: str
    publication: date
    author_id: int
    stock: int


class ListBooks(BaseModel):
    livros: list[LivrosPublic]


class BookUpdate(BaseModel):
    author: str = Field(
        description='Nome do autor cadastrado.', examples=['Brando Sanderson']
    )
    name: str = Field(
        description='Nome do Livro cadastrado.', examples=['Mistborn']
    )
    new_inventory: int = Field(
        description='Noo valor do estoque do livro', examples=[32]
    )


class DelLivro(BaseModel):
    author: str = Field(
        description='Nome do autor cadastrado.', examples=['Brando Sanderson']
    )
    book: str = Field(
        description='Nome do Livro cadastrado.', examples=['Mistborn']
    )
