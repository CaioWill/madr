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


@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=UserPublic,
    summary='Criação de usuários',
    response_description='Usuário cadastrado com sucesso.',
)
async def creat_accounts(session: Session, user: UserSchema):
    """
    Cadastrar um novo usuário na aplicação

    - **username**: Nome do usuário.
    - **email**: Email da conta.
    - **password**: Senha da conta.
    """
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
    summary='Atualização de usuários.',
    response_description='Atualização realizada com sucesso!',
)
async def update_user(
    user: UserUpdate,
    session: Session,
    current_user: Current_user,
):
    """
    Fazer atualização de atributos do proprio usuários cadastrados no sistema

    - **username**: Novo username.
    - **password**: Nova senha.
    """
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
            detail='Username já existe.',
        )


@router.delete(
    '/delete',
    status_code=HTTPStatus.OK,
    response_model=Mensagem,
    summary='Deletar sua Conta.',
    response_description='Conta deletada com sucesso!',
)
async def delete_user(current_user: Current_user, session: Session):
    """
    Deletação da propria conta, não sendo possivel deletar contas de
    outros usuarios

    """
    name = current_user.username

    await session.delete(current_user)
    await session.commit()

    return {'mensagem': f'Conta com username: {name} deletada permanetimente!'}
