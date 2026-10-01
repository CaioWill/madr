from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr.database_conect import get_session
from madr.models import Authors, User
from madr.schemas.schema import Mensagem
from madr.schemas.schema_authors import ListRomancistas, RomancistaSchema
from madr.security import format_name, get_current, get_current_admin

Session = Annotated[AsyncSession, Depends(get_session)]
Get_admin = Annotated[User, Depends(get_current_admin)]
Get_user = Annotated[User, Depends(get_current)]

router = APIRouter(prefix='/authors', tags=['authors'])


@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=Mensagem,
    summary='Criar novos autores.',
    response_description='Autor criado com sucesso.',
)
async def create_authors(
    user: Get_admin, romancista: RomancistaSchema, session: Session
):
    """
    Endpoint para cadastrar novos autores no banco de dados

    - **autores**: Nome do autor
    """
    romancista.name = format_name(romancista.name)

    name = await session.scalar(
        select(Authors).where(Authors.name == romancista.name)
    )

    if name:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Autor já cadastrado.'
        )

    author = Authors(name=romancista.name)

    session.add(author)
    await session.commit()
    await session.refresh(author)

    return {'mensagem': f'Autor: {author.name} adicionado com sucesso!'}


@router.get(
    '/list_authors',
    response_model=ListRomancistas,
    status_code=HTTPStatus.OK,
    summary='Listar autores cadastrados.',
    response_description='Autores cadastrados:',
)
async def listar_autores(user: Get_user, session: Session):
    """
    Endpoint para listar autores cadastrados no banco de dados.
    """
    authors = await session.scalars(select(Authors))

    return {'autores': authors}


@router.delete(
    '/delete_author{author}',
    status_code=HTTPStatus.OK,
    response_model=Mensagem,
    summary='Deletar autor.',
    response_description='Autor deletado com sucesso!',
)
async def deletar_author(author: str, user: Get_admin, session: Session):
    """
    Endpoint para fazer a remoção de autores do banco de dados.
    """
    author = format_name(author)

    author_del = await session.scalar(
        select(Authors).where(Authors.name == author)
    )

    if not author_del:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Autor {author} não encontrado!',
        )

    await session.delete(author_del)
    await session.commit()

    return {'mensagem': f'Author {author} deletado!'}
