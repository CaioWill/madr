from datetime import date
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr.database_conect import get_session
from madr.models import Authors, Books, Loans, User
from madr.schemas.schema import Mensagem
from madr.schemas.schema_loans import (
    ListLoans,
    LoansPublic,
    LoansSchema,
    ReturnLoans,
)
from madr.security import format_name, get_current, get_current_admin

router = APIRouter(prefix='/loans', tags=['loans'])

Session = Annotated[AsyncSession, Depends(get_session)]
Get_admin = Annotated[User, Depends(get_current_admin)]
Get_user = Annotated[User, Depends(get_current)]


@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=LoansPublic,
    summary='Criação de emprestimos de livros.',
    response_description='Emprestimo realizado com sucesso.',
)
async def to_resquest_loans(
    loans: LoansSchema, user: Get_user, session: Session
):
    """
    Endpoint de criação de emprestimos de livros cadastrados na
    conta do usuario que fez o emprestimo.

    - **book**: Nome do livro cadastrado.
    - **author**: Nome do autor do livro.
    - **date_deliver**: data de entrega do livro.
    """
    loans.book = format_name(loans.book)
    loans.author = format_name(loans.author)

    if loans.date_deliver <= date.today():
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Digite uma data de entrega válida!',
        )

    author = await session.scalar(
        select(Authors).where(Authors.name == loans.author)
    )

    if not author:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Author: {loans.author} não encontrado!',
        )

    book = await session.scalar(
        select(Books).where(
            Books.name == loans.book, Books.author_id == author.id
        )
    )

    if not book:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Livro: {loans.book} não encontrado!',
        )

    if book.stock < 1:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f'Livro: {loans.book} sem estoque!',
        )

    new_loans = Loans(
        user_id=user.id,
        books_id=book.id,
        date_deliver=loans.date_deliver,
    )

    book.stock -= 1

    session.add(new_loans)
    session.add(book)
    await session.commit()
    await session.refresh(new_loans)

    response = LoansPublic(
        to_request=user.username,
        book=loans.book,
        author=loans.author,
        date_deliver=loans.date_deliver,
        active=new_loans.active,
    )

    return response


@router.get(
    '/list_loans',
    response_model=ListLoans,
    status_code=HTTPStatus.OK,
    summary='Listar emprestimos cadastrados.',
    response_description='Emprestimos cadastrados:',
)
async def list_loans(user: Get_admin, session: Session):
    """
    Endpoint para administradores listarem todos os emprestimos
    cadastrados no banco de dados.
    """
    list_loans = []

    list = await session.scalars(select(Loans))

    for loans in list:
        list_loans.append({
            'book': loans.book.name,
            'author': loans.book.author.name,
            'date_deliver': loans.date_deliver,
            'to_request': loans.to_request.username,
            'active': loans.active,
        })

    return {'loans': list_loans}


@router.get(
    '/loans_active',
    status_code=HTTPStatus.OK,
    response_model=ListLoans,
    summary='Listar emprestimos ativos da conta.',
    response_description='Emprestimos ativos na sua conta:',
)
async def empretimos_ativos(user: Get_user, session: Session):
    """
    Endpoint para listar os empretimos ativos na conta que fez a
    solicitação.
    """
    list_loans = []
    list = await session.scalars(
        select(Loans).where(Loans.user_id == user.id, Loans.active)
    )

    for loans in list:
        list_loans.append({
            'book': loans.book.name,
            'author': loans.book.author.name,
            'to_request': loans.to_request.username,
            'date_deliver': loans.date_deliver,
            'active': loans.active,
        })

    return {'loans': list_loans}


@router.put(
    '/return_loans',
    status_code=HTTPStatus.OK,
    response_model=Mensagem,
    summary='Devolução de empretimos.',
    response_description='Emprestimo devolvido com sucesso!',
)
async def return_loans(book: ReturnLoans, user: Get_user, session: Session):
    """
    Endpoint para usuarios devolverem seus emprestimos ativos.

    - **name_book**: Nome do livro.
    - **name_author**: Nome do autor do livro.
    """
    book.name_book = format_name(book.name_book)
    book.name_author = format_name(book.name_author)

    author = await session.scalar(
        select(Authors).where(Authors.name == book.name_author)
    )

    if not author:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Author: {book.name_author} não encontrado!',
        )

    book_leans = await session.scalar(
        select(Books).where(
            Books.name == book.name_book, Books.author_id == author.id
        )
    )

    if not book_leans:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Livro: {book.name_book} não encontrado!',
        )

    loans = await session.scalar(
        select(Loans).where(
            Loans.user_id == user.id,
            Loans.active,
            Loans.books_id == book_leans.id,
        )
    )

    if not loans:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Você não pegou o livro: {book.name_book} emprestado.',
        )

    loans.active = False

    book_leans.stock += 1

    session.add(loans)
    await session.commit()
    await session.refresh(loans)

    return {'mensagem': f'Livro {book_leans.name} devolvido com sucesso.'}
