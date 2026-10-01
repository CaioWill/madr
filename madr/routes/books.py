from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr.database_conect import get_session
from madr.models import Authors, Books, User
from madr.schemas.schema import Mensagem
from madr.schemas.schema_authors import (
    BookUpdate,
    DelLivro,
    ListBooks,
    LivrosPublic,
    LivrosSchema,
)
from madr.security import format_name, get_current, get_current_admin

router = APIRouter(prefix='/books', tags=['books'])

Session = Annotated[AsyncSession, Depends(get_session)]
Get_admin = Annotated[User, Depends(get_current_admin)]
Get_user = Annotated[User, Depends(get_current)]


@router.post(
    '/create_book',
    status_code=HTTPStatus.CREATED,
    response_model=LivrosPublic,
    summary='Criação de novos livros.',
    response_description='Livro criado com sucesso!',
)
async def create_book(book: LivrosSchema, user: Get_admin, session: Session):
    """
    Endpoint de criação de novos livros, para criar um novo livro
    é necessario que o autor do livro ja esteja cadastrado.

    - **name**: Nome do livro
    - **publication**: Data de publicação
    - **author**: Nome do autor
    - **stock**: Quantidade do estoque
    """

    book.name = format_name(book.name)
    book.author = format_name(book.author)

    if book.stock < 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Digite um valor de estoque valido',
        )

    author = await session.scalar(
        select(Authors).where(Authors.name == book.author)
    )

    if not author:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Author não encontrado!'
        )

    books_author = author.books

    for livro_existente in books_author:
        if livro_existente.name == book.name:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Livro já cadastrado no author!',
            )

    new_book = Books(
        name=book.name,
        publication=book.publication,
        author_id=author.id,
        stock=book.stock,
    )

    session.add(new_book)
    await session.commit()
    await session.refresh(new_book)

    return new_book


@router.get(
    '/list_books',
    response_model=ListBooks,
    status_code=HTTPStatus.OK,
    summary='Listar livros cadastrados.',
    response_description='Livros cadastrados:',
)
async def list_books(user: Get_user, session: Session):
    """
    Endpoit para listar os livros que foram cadastrados no banco de dados.
    """
    books = await session.scalars(select(Books))

    return {'livros': books}


@router.get(
    '/list_books_{author}',
    response_model=ListBooks,
    status_code=HTTPStatus.OK,
    summary='Listar livros por autor.',
    response_description='Livros do autor selecionado:',
)
async def list_books_author(author: str, user: Get_user, session: Session):
    """
    Endpoint para listar livros de um autor especifico passado
    pelo usuário.
    """
    author = format_name(author)

    author_id = await session.scalar(
        select(Authors).where(Authors.name == author)
    )

    if not author_id:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Autor não encontrado!'
        )

    books = await session.scalars(
        select(Books).where(Books.author_id == author_id.id)
    )

    return {'livros': books}


@router.put(
    '/update_stock',
    response_model=LivrosPublic,
    status_code=HTTPStatus.OK,
    summary='Atualizar estoque do livro.',
    response_description='Estoque do livro atualizado com sucesso!',
)
async def update_stock(book: BookUpdate, user: Get_admin, session: Session):
    """
    Endpoint para atualizar o estoque do livro que o administrador passar.

    - **author**: Nome do autor do livro.
    - **name**: Nome do livro.
    - **stock**: Nova quantidado do estoque do livro.
    """
    book.name = format_name(book.name)
    book.author = format_name(book.author)

    author = await session.scalar(
        select(Authors).where(Authors.name == book.author)
    )

    if not author:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Autor: {book.author} não encontrado!',
        )

    update_book = await session.scalar(
        select(Books).where(
            Books.name == book.name, Books.author_id == author.id
        )
    )

    if not update_book:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Livro: {book.name} não encontrado!',
        )

    update_book.stock += book.new_inventory

    if update_book.stock < 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Livros não podem ter um estoque a baixo de zero',
        )

    session.add(update_book)
    await session.commit()
    await session.refresh(update_book)

    return update_book


@router.delete(
    '/delete_book',
    response_model=Mensagem,
    status_code=HTTPStatus.OK,
    summary='Deletar livros.',
    response_description='Livro deletado com sucesso!',
)
async def delete_book(
    book: Annotated[DelLivro, Query()],
    user: Get_admin,
    session: Session,
):
    """
    Endpoit para deletar livros cadastrados.
    """
    book.book = format_name(book.book)
    book.author = format_name(book.author)

    author = await session.scalar(
        select(Authors).where(Authors.name == book.author)
    )

    if not author:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Autor: {book.author} não encontrado!',
        )

    livro_del = await session.scalar(
        select(Books).where(
            Books.name == book.book, Books.author_id == author.id
        )
    )

    if not livro_del:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Livro: {book.book} não encontrado!',
        )

    await session.delete(livro_del)
    await session.commit()

    return {'mensagem': f'Livro {book.book} do author {book.author} deletado'}
