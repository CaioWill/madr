import re
import unicodedata
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from madr.database_conect import get_session
from madr.models import User
from madr.schemas.schema_Auths import (
    UpdateCredencias,
    UserPublic,
    UserSchema,
    UserUpdate,
)
from madr.security import criptografar, get_current

router = APIRouter(prefix='/login', tags=['login'])

Session = Annotated[AsyncSession, Depends(get_session)]
Current_user = Annotated[User, Depends(get_current)]


# Criação de novos usuarios
@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def criar_conta(session: Session, user: UserSchema):

    # Formatação do username
    username_novo_user = user.username
    formatacao_username = (
        unicodedata
        .normalize('NFKD', username_novo_user)
        .encode('ASCII', 'ignore')
        .decode('ASCII')
    )
    user.username = re.sub(r'[^a-zA-Z0-9 ]', '', formatacao_username)

    # Procurando se o novo usuario não da conflito com os campos uniques
    response = await session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    # Se o select retornar um user, mensagem de erro mostral qual esta igual
    if response:
        if response.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT, detail='Username já existente'
            )
        if response.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT, detail='Email já existente'
            )

    # adicionando o novo user no db
    response = User(
        username=user.username,
        email=user.email,
        password=criptografar(user.password),
    )

    session.add(response)
    await session.commit()
    await session.refresh(response)
    return response


# Endpoint para atualizar um novo usuario
@router.put(
    '/update_user',  # adicionamos a variavel, paramentro da url
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
)
async def update_user(
    user: UserUpdate,
    session: Session,
    current_user: Current_user,
):

    current_user.username = user.username
    # alterando a senha limpa recebida para um hash
    current_user.password = criptografar(user.password)

    # tentando fazer o commit da trasação
    try:
        session.add(current_user)
        await session.commit()
        await session.refresh(current_user)

        return current_user

    # Caso dê erro de integridade
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='User name or Email already exists',
        )


# Endpoint para adm atualizar credenciais dos outros
@router.put(
    '/credenciais',  # adicionamos a variavel, paramentro da url
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
)
async def update_credenciais_users(
    user: UpdateCredencias,
    session: Session,
    current_user: Current_user,
):

    if current_user.credenciais != 'Admin':
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    user_update = await session.scalar(
        select(User).where(User.username == user.username)
    )

    if not user_update:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Usuario não encontrado'
        )

    user_update.credenciais = user.credenciais

    # tentando fazer o commit da trasação
    try:
        session.add(user_update)
        await session.commit()
        await session.refresh(user_update)

        return current_user

    # Caso dê erro de integridade
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='User name or Email already exists',
        )
