from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr.database_conect import get_session
from madr.models import Livros, Romancistas, User
from madr.schemas.schema import Mensagem
from madr.schemas.schema_romancista import (
    DelLivro,
    ListLivros,
    LivrosPublic,
    LivrosPut,
    LivrosSchema,
)
from madr.security import format_name, get_current, get_current_admin

router = APIRouter(prefix='/livros', tags=['livros'])

Session = Annotated[AsyncSession, Depends(get_session)]
Get_current_admin = Annotated[User, Depends(get_current_admin)]
Get_current = Annotated[User, Depends(get_current)]


@router.post(
    '/adicionar_livro',
    status_code=HTTPStatus.CREATED,
    response_model=LivrosPublic,
)
async def adicionar_livro(
    livro: LivrosSchema, user: Get_current_admin, session: Session
):
    livro.name = format_name(livro.name)
    livro.author = format_name(livro.author)

    if livro.estoque < 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Digite um valor de estoque valido',
        )

    author = await session.scalar(
        select(Romancistas).where(Romancistas.name == livro.author)
    )

    if not author:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Author não encontrado!'
        )

    livros_author = author.livros

    for livro_existente in livros_author:
        if livro_existente.name == livro.name:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Livro já cadastrado no author!',
            )

    new_livro = Livros(
        name=livro.name,
        publication=livro.publication,
        author_id=author.id,
        estoque=livro.estoque,
    )

    session.add(new_livro)
    await session.commit()
    await session.refresh(new_livro)

    return new_livro


@router.get(
    '/list_livros', response_model=ListLivros, status_code=HTTPStatus.OK
)
async def listar_livros(user: Get_current, session: Session):

    livros = await session.scalars(select(Livros))

    return {'livros': livros}


@router.get(
    '/list_livros_{author}',
    response_model=ListLivros,
    status_code=HTTPStatus.OK,
)
async def listar_livros_de_author(
    author: str, user: Get_current, session: Session
):

    author = format_name(author)

    author_id = await session.scalar(
        select(Romancistas).where(Romancistas.name == author)
    )

    if not author_id:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Author não encontrado!'
        )

    livros = await session.scalars(
        select(Livros).where(Livros.author_id == author_id.id)
    )

    return {'livros': livros}


@router.put(
    '/atualizar_estoque',
    response_model=LivrosPublic,
    status_code=HTTPStatus.OK,
)
async def atualizar_estoque(
    livro: LivrosPut, user: Get_current_admin, session: Session
):

    livro.name = format_name(livro.name)
    livro.author = format_name(livro.author)

    author = await session.scalar(
        select(Romancistas).where(Romancistas.name == livro.author)
    )

    if not author:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Autor: {livro.author} não encontrado!',
        )

    livro_put = await session.scalar(
        select(Livros).where(
            Livros.name == livro.name, Livros.author_id == author.id
        )
    )

    if not livro_put:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Livro: {livro.name} não encontrado!',
        )

    livro_put.estoque += livro.new_inventory

    if livro_put.estoque < 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Livros não podem ter um estoque a baixo de zero',
        )

    session.add(livro_put)
    await session.commit()
    await session.refresh(livro_put)

    return livro_put


@router.delete(
    '/deletar_livro', response_model=Mensagem, status_code=HTTPStatus.OK
)
async def deletar_livro(
    livro: Annotated[DelLivro, Query()],
    user: Get_current_admin,
    session: Session,
):

    livro.livro = format_name(livro.livro)
    livro.author = format_name(livro.author)

    author_id = await session.scalar(
        select(Romancistas).where(Romancistas.name == livro.author)
    )

    if not author_id:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Autor: {livro.author} não encontrado!',
        )

    livro_del = await session.scalar(
        select(Livros).where(
            Livros.name == livro.livro, Livros.author_id == author_id.id
        )
    )

    if not livro_del:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Livro: {livro.livro} não encontrado!',
        )

    await session.delete(livro_del)
    await session.commit()

    return {
        'mensagem': f'Livro {livro.livro} do author {livro.author} deletado'
    }
