from datetime import date

from pydantic import BaseModel, Field


class LoansSchema(BaseModel):
    book: str = Field(description='Nome do livro.', examples=['Mistborn'])
    author: str = Field(
        description='Nome do autor do livro.', examples=['Brandon Sanderson']
    )
    date_deliver: date = Field(
        description='Data de entrega do livro.', examples=['2026-12-28']
    )


class LoansPublic(LoansSchema):
    to_request: str
    active: bool


class ListLoans(BaseModel):
    loans: list[LoansPublic]


class ReturnLoans(BaseModel):
    name_book: str = Field(
        description='Nome do livro pedo emprestado.', examples=['Mistborn']
    )
    name_author: str = Field(
        description='Nome do autor do livro.', examples=['Brandon Sanderson']
    )
