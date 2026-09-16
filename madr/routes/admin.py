from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from madr.database_conect import get_session
from madr.models import User
from madr.schemas.schema_Auths import AdminPublic, Keyadmin, UpdateAdmin
from madr.security import get_current
from madr.settings import Settings

router = APIRouter(prefix='/admin', tags=['Admin'])

Session = Annotated[AsyncSession, Depends(get_session)]
Current_user = Annotated[User, Depends(get_current)]


@router.put('/', status_code=HTTPStatus.OK, response_model=AdminPublic)
async def credenciais(
    key: Keyadmin, current_user: Current_user, session: Session
):

    if key.key == Settings().ADMIN_KEY:
        current_user.is_admin = True

    else:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Senha de autorização incorreta',
        )

    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)

    return current_user


@router.put(
    '/credenciais',  # adicionamos a variavel, paramentro da url
    status_code=HTTPStatus.OK,
    response_model=AdminPublic,
)
async def update_credenciais_users(
    user: UpdateAdmin,
    session: Session,
    current_user: Current_user,
):

    if not current_user.is_admin:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    response = await session.scalar(
        select(User).where(User.username == user.username)
    )

    if not response:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Usuario não encontrado'
        )

    if user.credencial == 'admin':
        response.is_admin = True
    elif user.credencial == 'user':
        response.is_admin = False
    else:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Digite um valor valido'
        )

    # tentando fazer o commit da trasação
    try:
        session.add(response)
        await session.commit()
        await session.refresh(response)

        return response

    # Caso dê erro de integridade
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='User name or Email already exists',
        )
