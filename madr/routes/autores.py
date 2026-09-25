from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr.database_conect import get_session
from madr.models import Romancistas, User
from madr.schemas.schema import Mensagem
from madr.schemas.schema_romancista import ListRomancistas, RomancistaSchema
from madr.security import format_name, get_current, get_current_admin

Session = Annotated[AsyncSession, Depends(get_session)]
Get_curret_admin = Annotated[User, Depends(get_current_admin)]
Get_curret = Annotated[User, Depends(get_current)]

router = APIRouter(prefix='/autores', tags=['autores'])


@router.post('/', status_code=HTTPStatus.CREATED, response_model=Mensagem)
async def criar_romancista(
    user: Get_curret_admin, romancista: RomancistaSchema, session: Session
):

    romancista.name = format_name(romancista.name)

    name = await session.scalar(
        select(Romancistas).where(Romancistas.name == romancista.name)
    )

    if name:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Author já cadastrado.'
        )

    author = Romancistas(name=romancista.name)

    session.add(author)
    await session.commit()
    await session.refresh(author)

    return {'mensagem': f'Author: {author.name} adicionado com sucesso!'}


@router.get(
    '/listar_authores',
    response_model=ListRomancistas,
    status_code=HTTPStatus.OK,
)
async def listar_autores(user: Get_curret, session: Session):
    autores = await session.scalars(select(Romancistas))

    return {'autores': autores}


@router.delete(
    '/deletar_author{author}',
    status_code=HTTPStatus.OK,
    response_model=Mensagem,
)
async def deletar_author(
    author: str, user: Get_curret_admin, session: Session
):
    author = format_name(author)

    author_del = await session.scalar(
        select(Romancistas).where(Romancistas.name == author)
    )

    if not author_del:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Author {author} não encontrado!',
        )

    await session.delete(author_del)
    await session.commit()

    return {'mensagem': f'Author {author} deletado!'}
