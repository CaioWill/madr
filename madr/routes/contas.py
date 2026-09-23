from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from madr.database_conect import get_session
from madr.models import User
from madr.schemas.schema import Mensagem
from madr.schemas.schema_Auths import (
    UserPublic,
    UserSchema,
    UserUpdate,
)
from madr.security import criptografar, format_name, get_current

router = APIRouter(prefix='/login', tags=['login'])

Session = Annotated[AsyncSession, Depends(get_session)]
Current_user = Annotated[User, Depends(get_current)]


# Criação de novos usuarios
@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def criar_conta(session: Session, user: UserSchema):

    # Formatação do username
    user.username = format_name(user.username)

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

    current_user.username = format_name(user.username)
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
            detail='User name already exists',
        )


@router.delete('/delete', status_code=HTTPStatus.OK, response_model=Mensagem)
async def delete_user(current_user: Current_user, session: Session):

    name = current_user.username

    await session.delete(current_user)
    await session.commit()

    return {'mensagem': f'Conta com username: {name} deletada permanetimente!'}
