from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr.database_conect import get_session
from madr.models import User
from madr.schemas.schema import Mensagem
from madr.schemas.schema_Auths import (
    AdminPublic,
    Keyadmin,
    UpdateAdmin,
    UserList,
)
from madr.security import get_current, get_current_admin
from madr.settings import Settings

router = APIRouter(prefix='/admin', tags=['Admin'])

Session = Annotated[AsyncSession, Depends(get_session)]
Current_user = Annotated[User, Depends(get_current)]
Current_user_admin = Annotated[User, Depends(get_current_admin)]


@router.put(
    '/',
    status_code=HTTPStatus.OK,
    response_model=AdminPublic,
    summary='Atualização de credencial para administrador.',
    response_description=(
        'Atualização realizada com sucesso, você é um administrador!'
    ),
)
async def update_loans(
    key: Keyadmin, current_user: Current_user, session: Session
):
    """
    Atualização de credencial do usuário para administrador,
    tranformando sua conta em admin

    - **key**: Senha de administração.
    """
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
    '/loans',
    status_code=HTTPStatus.OK,
    response_model=AdminPublic,
    summary='Atualizar credencial de outro usuário.',
    response_description='Credencial do usuário atualizado com sucesso!'
)
async def update_credenciais_users(
    user: UpdateAdmin,
    session: Session,
    current_user: Current_user_admin,
):
    '''
        Atualizar o credencial de outros usuários para administrador
        com uma conta que já é administrador.

        - **username**: nome do usuário que será alterado.
        - **loans**: Novo valor do credencial.
    '''
    response = await session.scalar(
        select(User).where(User.username == user.username)
    )

    if not response:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Usuario não encontrado'
        )

    if user.credencial == 'admin':
        response.is_admin = True
    else:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Digite um valor valido'
        )

    session.add(response)
    await session.commit()
    await session.refresh(response)

    return response


@router.get(
    '/list_users',
    status_code=HTTPStatus.OK,
    response_model=UserList,
    summary='Listar usuários cadastrados.',
    response_description='Usuários cadastrados:'
)
async def list_users(current_user: Current_user_admin, session: Session):
    '''
        Listar todos os usuários cadastrados na aplicação.
    '''
    users = await session.scalars(select(User))

    return {'users': users}


@router.delete(
    '/delete{username}',
    status_code=HTTPStatus.OK,
    response_model=Mensagem,
    summary='Deletar usuários.',
    response_description='Usuário deletado com sucesso!'
)
async def delete_user(
    username: str, current_user: Current_user_admin, session: Session
):
    '''
        Deletar usuários de outras pessoas usando uma conta admin.
    '''
    user = await session.scalar(select(User).where(User.username == username))

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Usuario: {username} Não encontrado',
        )

    name = user.username

    await session.delete(user)
    await session.commit()

    return {'mensagem': f'Conta com username: {name} deletada permanetimente!'}
